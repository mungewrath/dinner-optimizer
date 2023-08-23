import base64
import json
import os
from dotenv import load_dotenv

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

CHANNEL_ID = "C05JEBJHNQ4"
SECRET_NAME = "dinner-optimizer-credentials"


def lambda_handler(event, context):
    # load_dotenv()

    # SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

    credentials = fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text="It's time to meal plan soon! Post before 2pm with any special requests you might have, and I'll include them.",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"success": True}),
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


def cli():
    lambda_handler(None, None)


if __name__ == "__main__":
    cli()
