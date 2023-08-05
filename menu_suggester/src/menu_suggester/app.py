import base64
import json
import os
from dotenv import load_dotenv
import openai
import requests

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

MEAL_STUB = '{\n  "meal_list": [\n    {\n      "meal_name": "German Sausage and Sauerkraut",\n      "meal_description": "Grilled sausages served with sauerkraut and mustard"\n    },\n    {\n      "meal_name": "Vegetable Stir-Fry",\n      "meal_description": "Assorted vegetables stir-fried with soy sauce and garlic"\n    },\n    {\n      "meal_name": "Korean Bibimbap",\n      "meal_description": "Mixed rice bowl topped with sautéed vegetables, tofu, and a fried egg"\n    },\n    {\n      "meal_name": "Spaghetti Carbonara",\n      "meal_description": "Pasta tossed in a creamy sauce with eggs, cheese, and bacon"\n    }\n  ]\n}'

CHANNEL_ID = "C05JEBJHNQ4"

def lambda_handler(event, context):
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    # Set your OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    MODEL = "gpt-3.5-turbo"

    SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

    # WebClient instantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    slack_client = WebClient(token=SLACK_TOKEN)

    # Load priming instruction for LLM from priming_instruction.txt
    with open("priming_instruction.txt") as f:
        priming_instruction = f.read()

    # Send priming instruction to OpenAI API and get response
    # response = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": priming_instruction},
    #         {
    #             "role": "user",
    #             "content": "Generate a new set of suggested dinners for this week.",
    #         },
    #     ],
    #     max_tokens=2000,
    #     temperature=0.3,
    #     n=1,
    #     stop=None,
    #     functions=[
    #         {
    #             "name": "generate_meal_plan",
    #             "description": "Generate structured meal plan",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "meal_list": {
    #                         "type": "array",
    #                         "items": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "meal_name": {
    #                                     "type": "string",
    #                                     "description": "title of the meal",
    #                                 },
    #                                 "meal_description": {
    #                                     "type": "string",
    #                                     "description": "a description of the meal",
    #                                 },
    #                             },
    #                         },
    #                     }
    #                 },
    #             },
    #         }
    #     ],
    # )

    # menu = json.loads(response.choices[0].message.function_call.arguments)
    menu = json.loads(MEAL_STUB)

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text="Here's your suggested menu for this week:",
    )

    # Loop through menu. For each meal, call DALL-E API to generate an image based on the meal description
    for meal in menu["meal_list"]:
        # TODO: This call may fail if censored
        meal_image = dall_e_api_call(f"{meal['meal_name']} - {meal['meal_description']}")

        try:
            result = slack_client.files_upload(
                channels=CHANNEL_ID,
                initial_comment=f"• *{meal['meal_name']}*: {meal['meal_description']}",
                content=meal_image,
                filename=f"{meal['meal_name']}.png",
            )
            # Log the result
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error uploading file: {}".format(e))

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text="Post in the channel if you'd like to request any tweaks!",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"response": menu}),
    }


def dall_e_api_call(meal_description):
    response = openai.Image.create(
        prompt=meal_description, n=1, size="512x512", response_format="b64_json"
    )

    raw_b64 = response["data"][0]["b64_json"]
    return base64.b64decode(raw_b64)
