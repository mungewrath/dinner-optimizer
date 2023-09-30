import base64
import json
import openai
import boto3

import logging
from slack_sdk import WebClient
import dinner_optimizer_shared.credentials_handler as creds
import dinner_optimizer_shared.message_persistence as db
import dinner_optimizer_shared.time_utils as time_utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

TABLE_NAME = "UserResponseTable"

MEAL_STUB = '{\n  "meal_list": [\n    {\n      "meal_name": "German Sausage and Sauerkraut",\n      "meal_description": "Grilled sausages served with sauerkraut and mustard"\n    },\n    {\n      "meal_name": "Vegetable Stir-Fry",\n      "meal_description": "Assorted vegetables stir-fried with soy sauce and garlic"\n    },\n    {\n      "meal_name": "Korean Bibimbap",\n      "meal_description": "Mixed rice bowl topped with sautéed vegetables, tofu, and a fried egg"\n    },\n    {\n      "meal_name": "Spaghetti Carbonara",\n      "meal_description": "Pasta tossed in a creamy sauce with eggs, cheese, and bacon"\n    }\n  ]\n}'

CHANNEL_ID = "C05JEBJHNQ4"

MODEL = "gpt-3.5-turbo"

dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    credentials = creds.fetch_creds_from_secrets_manager()

    # Set your OpenAI API key
    openai.api_key = credentials["OPENAI_API_KEY"]

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    current_week = time_utils.most_recent_saturday()

    # Load priming instruction for LLM from priming_instruction.txt
    with open("priming_instruction.txt") as f:
        priming_instruction = f.read()

    # TODO: This code is shared, pull into helper
    # Load existing chat messages for the past week from Dynamo
    response = dynamodb.get_item(
        TableName=TABLE_NAME, Key={"Week": {"S": current_week}}
    )

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": current_week}, "Interactions": {"L": []}}
    )

    interactions = sorted(
        existing_item["Interactions"]["L"], key=lambda x: x["M"]["time"]["S"]
    )

    logger.info("interactions: %s", json.dumps(interactions, indent=2))

    messages = [
        {"role": "system", "content": priming_instruction},
    ]

    for i in interactions:
        messages.append({"role": i["M"]["role"]["S"], "content": i["M"]["text"]["S"]})

    messages.append(
        {
            "role": "user",
            "content": "Generate a new set of suggested dinners for this week. Please take our particular requests for this week into account",
        }
    )

    logger.info("messages being sent: %s", json.dumps(messages, indent=2))

    # Send priming instruction to OpenAI API and get response
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=2000,
        temperature=0.3,
        n=1,
        stop=None,
        functions=[
            {
                "name": "generate_meal_plan",
                "description": "Generate structured meal plan",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "meal_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "meal_name": {
                                        "type": "string",
                                        "description": "title of the meal",
                                    },
                                    "meal_description": {
                                        "type": "string",
                                        "description": "a description of the meal",
                                    },
                                },
                            },
                        },
                        "commentary": {
                            "type": "string",
                            "description": "A detailed meal-by-meal description, explaining what factors led to the meal being chosen, and whether it takes the user's special requests into account",
                        },
                    },
                },
            }
        ],
    )

    logger.info("OpenAI response: %s", json.dumps(response, indent=2))

    menu = json.loads(response.choices[0].message.function_call.arguments)

    recorded_message = "Here's your suggested menu for this week:"

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text=recorded_message + "\n" + menu["commentary"],
    )

    recorded_message += "\n"
    for meal in menu["meal_list"]:
        recorded_message += f"{meal['meal_name']} - {meal['meal_description']}\n"

    db.record_conversation_message(
        {
            "role": {"S": "assistant"},
            "time": {"S": f"{current_week} {time_utils.current_time()}"},
            "text": {"S": recorded_message},
        },
        current_week,
    )

    any_meals_failed_to_upload = False

    for meal in menu["meal_list"]:
        any_meals_failed_to_upload = post_meal_photo(
            slack_client, meal, any_meals_failed_to_upload
        )

    if any_meals_failed_to_upload:
        msg = "I had some trouble uploading some of the pictures. Here's a text-only copy of the full menu:\n"
        msg += "\n".join(
            f"{meal['meal_name']} - {meal['meal_description']}"
            for meal in menu["meal_list"]
        )
        slack_client.chat_postMessage(
            channel=CHANNEL_ID,
            text=msg,
        )

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text=menu["commentary"],
    )

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        # text="Post in the channel if you'd like to request any tweaks!",
        text="Let me know if there are any customizations you want after looking, and I can re-think the list.",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"response": menu}),
    }


def post_meal_photo(slack_client, meal, any_meals_failed_to_upload):
    try:
        meal_image = dall_e_api_call(
            f"{meal['meal_name']} - {meal['meal_description']}"
        )

        result = slack_client.files_upload(
            channels=CHANNEL_ID,
            initial_comment=f"• *{meal['meal_name']}*: {meal['meal_description']}",
            content=meal_image,
            filename=f"{meal['meal_name']}.png",
        )
        logger.info(result)
    except:
        logger.error(
            "Error uploading file for %s: %s",
            meal["meal_name"],
            meal["meal_description"],
            exc_info=True,
        )
        any_meals_failed_to_upload = True

    return any_meals_failed_to_upload


def dall_e_api_call(meal_description):
    response = openai.Image.create(
        prompt=meal_description, n=1, size="512x512", response_format="b64_json"
    )

    raw_b64 = response["data"][0]["b64_json"]
    return base64.b64decode(raw_b64)


def cli():
    lambda_handler(None, None)


if __name__ == "__main__":
    cli()
