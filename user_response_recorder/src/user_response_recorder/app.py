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

    payload = json.loads(event["body"])["event"]

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

    response = {}

    return api_gateway_response(body=response)


def api_gateway_response(body):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        # "headers": { "headerName": "headerValue", ... },
        "body": json.dumps(body),
    }


def cli():
    lambda_handler(
        {
            "body": '{"token":"7kqwwLKsSI5EFKHvepHBZjCQ","team_id":"T05K1K7K5TJ","context_team_id":"T05K1K7K5TJ","context_enterprise_id":null,"api_app_id":"A05LCPE500M","event":{"client_msg_id":"199b139c-5ea7-4be6-a371-1846c71b1ea5","type":"message","text":"would like a way to use up lentils in something other than a soup","user":"U05JQH9JN57","ts":"1696042947.448099","blocks":[{"type":"rich_text","block_id":"BebPw","elements":[{"type":"rich_text_section","elements":[{"type":"text","text":"would like a way to use up lentils in something other than a soup"}]}]}],"team":"T05K1K7K5TJ","channel":"C05JEBJHNQ4","event_ts":"1696042947.448099","channel_type":"channel"},"type":"event_callback","event_id":"Ev05ULBYSQG3","event_time":1696042947,"authorizations":[{"enterprise_id":null,"team_id":"T05K1K7K5TJ","user_id":"U05L9285S6A","is_bot":true,"is_enterprise_install":false}],"is_ext_shared_channel":false,"event_context":"4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDVLMUs3SzVUSiIsImFpZCI6IkEwNUxDUEU1MDBNIiwiY2lkIjoiQzA1SkVCSkhOUTQifQ"}'
        },
        None,
    )


if __name__ == "__main__":
    cli()
