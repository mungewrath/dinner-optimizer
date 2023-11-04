import json

import logging
from slack_sdk import WebClient

from dinner_optimizer_shared import credentials_handler as creds
from dinner_optimizer_shared import message_persistence as persistence
from dinner_optimizer_shared import time_utils

from dinner_optimizer_shared.interaction import Interaction

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def lambda_handler(event, context):
    channel_id = event["slack_channel_id"]

    credentials = creds.fetch_creds_from_secrets_manager()

    slack_client = WebClient(token=credentials["SLACK_BOT_TOKEN"])

    past_recommendations: list[Interaction] = []
    for n in reversed(range(2, 5)):
        w = time_utils.nth_most_recent_saturday(n)
        past_interactions = persistence.retrieve_interactions_for_week(w)

        # Add them to the current week's history.
        bot_messages = list(filter(lambda x: x.role == "assistant", past_interactions))
        if len(bot_messages) < 1:
            continue

        past_recommendations.append(bot_messages[-1])

    for pr in past_recommendations:
        persistence.record_conversation_message(pr, time_utils.most_recent_saturday())

    slack_client.chat_postMessage(
        channel=channel_id,
        text="*It's time to meal plan soon!*\n\nPost before 2pm with any special requests you might have this week, and I'll include them.",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"success": True}),
    }


def cli():
    event = {
        # Beta
        "slack_channel_id": "C060L3A1J4W"
    }
    lambda_handler(event, None)


if __name__ == "__main__":
    cli()
