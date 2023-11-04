import json
import boto3

import logging
from slack_sdk import WebClient

from dinner_optimizer_shared import credentials_handler as creds
from dinner_optimizer_shared import message_persistence as db
from dinner_optimizer_shared import time_utils

from dinner_optimizer_shared.interaction import Interaction
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

# For #dinner-optimizer
# CHANNEL_ID = "C05JEBJHNQ4"
# #dinner-optimizer-beta
# CHANNEL_ID = "C060L3A1J4W"
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
    slack_channel_id = payload["channel"]

    if sender == BOT_USER_ID:
        logger.info("Hearing myself; exiting without actions")
        return api_gateway_response({})

    if "conjure" in user_response.lower():
        logger.info("Invoking menu suggestion lambda")
        client = boto3.client("lambda")
        lambda_name = os.environ["MENU_SUGGESTER_LAMBDA_ARN"]
        event = {"slack_channel_id": slack_channel_id}
        client.invoke(
            FunctionName=lambda_name, InvocationType="Event", Payload=json.dumps(event)
        )
        return

    current_week = time_utils.most_recent_saturday()

    entry = Interaction(
        role="user",
        time=f"{current_week} {time_utils.current_time()}",
        text=user_response,
        timestamp=timestamp,
    )

    credentials = creds.fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    db.record_conversation_message(entry, current_week)

    logger.info("Message recorded.")

    slack_client.chat_postMessage(
        channel=slack_channel_id,
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
