import base64
import json
import openai
import boto3
from botocore.exceptions import ClientError

import logging
from slack_sdk import WebClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

SECRET_NAME = "dinner-optimizer-credentials"

TABLE_NAME = "UserResponseTable"

MEAL_STUB = '{\n  "meal_list": [\n    {\n      "meal_name": "German Sausage and Sauerkraut",\n      "meal_description": "Grilled sausages served with sauerkraut and mustard"\n    },\n    {\n      "meal_name": "Vegetable Stir-Fry",\n      "meal_description": "Assorted vegetables stir-fried with soy sauce and garlic"\n    },\n    {\n      "meal_name": "Korean Bibimbap",\n      "meal_description": "Mixed rice bowl topped with sautéed vegetables, tofu, and a fried egg"\n    },\n    {\n      "meal_name": "Spaghetti Carbonara",\n      "meal_description": "Pasta tossed in a creamy sauce with eggs, cheese, and bacon"\n    }\n  ]\n}'
WEEK_STUB = "07-29-2023"

CHANNEL_ID = "C05JEBJHNQ4"

MODEL = "gpt-3.5-turbo"

dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    credentials = fetch_creds_from_secrets_manager()

    # Set your OpenAI API key
    openai.api_key = credentials["OPENAI_API_KEY"]

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    # Load priming instruction for LLM from priming_instruction.txt
    with open("priming_instruction.txt") as f:
        priming_instruction = f.read()

    # TODO: This code is shared, pull into helper
    # Load existing chat messages for the past week from Dynamo
    response = dynamodb.get_item(TableName=TABLE_NAME, Key={"Week": {"S": WEEK_STUB}})

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": WEEK_STUB}, "Interactions": {"L": []}}
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
            "content": "Generate a new set of suggested dinners for this week.",
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
                        }
                    },
                },
            }
        ],
    )

    logger.info("OpenAI response: %s", json.dumps(response, indent=2))

    menu = json.loads(response.choices[0].message.function_call.arguments)
    # menu = json.loads(MEAL_STUB)

    recorded_message = "Here's your suggested menu for this week:"

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text=recorded_message,
    )

    recorded_message += "\n"
    for meal in menu["meal_list"]:
        recorded_message += f"{meal['meal_name']} - {meal['meal_description']}\n"

    record_conversation_message(
        {
            "role": {"S": "assistant"},
            "time": {"S": f"{WEEK_STUB} 08:00:00"},
            "text": {"S": recorded_message},
        }
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
        # text="Post in the channel if you'd like to request any tweaks!",
        text="Let me know if there are any customizations you want after looking, and I can re-think the list.",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"response": menu}),
    }


def fetch_creds_from_secrets_manager():
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    credentials = json.loads(get_secret_value_response["SecretString"])
    return credentials


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


def record_conversation_message(entry):
    # Retrieve the existing item based on the key
    response = dynamodb.get_item(TableName=TABLE_NAME, Key={"Week": {"S": WEEK_STUB}})

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": WEEK_STUB}, "Interactions": {"L": []}}
    )

    existing_item["Interactions"]["L"].append({"M": entry})

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"Week": {"S": WEEK_STUB}},
        UpdateExpression="SET Interactions = :interactions",
        ExpressionAttributeValues={":interactions": existing_item["Interactions"]},
    )


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
