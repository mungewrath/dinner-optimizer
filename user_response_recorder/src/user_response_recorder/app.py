import json
from dotenv import load_dotenv
import boto3

import logging
from slack_sdk import WebClient
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

CHANNEL_ID = "C05JEBJHNQ4"
BOT_USER_ID = "U05L9285S6A"

TABLE_NAME = "UserResponseTable"

SECRET_NAME = "dinner-optimizer-credentials"

WEEK = "07-29-2023"

dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    payload = json.loads(event["body"])["event"]

    logger.info(json.dumps(payload))

    user_response = payload["text"]
    sender = payload["user"]

    if sender == BOT_USER_ID:
        logger.info("Hearing myself; exiting without actions")
        return api_gateway_response({})

    # TODO: Parse date and time
    entry = {
        "role": {"S": "user"},
        "time": {"S": f"{WEEK} 08:00:00"},
        "text": {"S": user_response},
    }

    credentials = fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    record_conversation_message(entry)

    logger.info("Item updated successfully.")

    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text=f">{user_response}\nGot it :thumbsup:",
    )

    response = {}

    return api_gateway_response(body=response)


def record_conversation_message(entry):
    # Retrieve the existing item based on the key
    response = dynamodb.get_item(TableName=TABLE_NAME, Key={"Week": {"S": WEEK}})

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": WEEK}, "Interactions": {"L": []}}
    )

    existing_item["Interactions"]["L"].append({"M": entry})

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"Week": {"S": WEEK}},
        UpdateExpression="SET Interactions = :interactions",
        ExpressionAttributeValues={":interactions": existing_item["Interactions"]},
    )


def api_gateway_response(body):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        # "headers": { "headerName": "headerValue", ... },
        "body": json.dumps(body),
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
    lambda_handler({"body": "Hello World!"}, None)


if __name__ == "__main__":
    cli()
