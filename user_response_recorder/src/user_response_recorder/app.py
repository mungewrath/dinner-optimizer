import json

import logging
from slack_sdk import WebClient

from dinner_optimizer_shared import credentials_handler as creds
from dinner_optimizer_shared import message_persistence as db
from dinner_optimizer_shared import time_utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

CHANNEL_ID = "C05JEBJHNQ4"
BOT_USER_ID = "U05L9285S6A"


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    for r in event["Records"]:
        payload = json.loads(r["body"])["event"]
        handle_user_message(payload)

    response = {}

    return api_gateway_response(body=response)


def handle_user_message(payload):
    logger.info(json.dumps(payload))

    timestamp = payload["ts"]
    user_response = payload["text"]
    sender = payload["user"]

    if sender == BOT_USER_ID:
        logger.info("Hearing myself; exiting without actions")
        return api_gateway_response({})

    current_week = time_utils.most_recent_saturday()
    entry = {
        "role": {"S": "user"},
        "time": {"S": f"{current_week} {time_utils.current_time()}"},
        "text": {"S": user_response},
        "timestamp": {"S": timestamp},
    }

    credentials = creds.fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    db.record_conversation_message(entry, current_week)

    logger.info("Message recorded.")

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text=f">{user_response}\nGot it :thumbsup:",
    )


def api_gateway_response(body):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        # "headers": { "headerName": "headerValue", ... },
        "body": json.dumps(body),
    }


def cli():
    with open("events/user_response_sqs_event.json", "r") as f:
        event = json.load(f)

    lambda_handler(
        event,
        None,
    )


if __name__ == "__main__":
    cli()
