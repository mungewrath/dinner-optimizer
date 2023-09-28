import json

import logging
from slack_sdk import WebClient

from dinner_optimizer_shared import credentials_handler as creds


logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

CHANNEL_ID = "C05JEBJHNQ4"


def lambda_handler(event, context):
    credentials = creds.fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text="*It's time to meal plan soon!*\n\nPost before 2pm with any special requests you might have this week, and I'll include them.",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"success": True}),
    }


def cli():
    lambda_handler(None, None)


if __name__ == "__main__":
    cli()
