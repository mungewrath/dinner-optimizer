import json
import logging
import boto3

from .interaction import Interaction

dynamodb = boto3.client("dynamodb")

TABLE_NAME = "UserResponseTable"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def record_conversation_message(entry: Interaction, week: str, channel_id: str):
    # Retrieve the existing item based on the key
    response = dynamodb.get_item(
        TableName=TABLE_NAME, Key={"Week": {"S": f"{week}-{channel_id}"}}
    )

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": f"{week}-{channel_id}"}, "Interactions": {"L": []}}
    )

    if any(
        x["M"]["timestamp"] == entry.timestamp
        for x in existing_item["Interactions"]["L"]
    ):
        logger.info(
            "Entry with message '%s' and timestamp %s already exists in record; skipping write",
            entry.text,
            entry.timestamp,
        )
        return

    existing_item["Interactions"]["L"].append(entry.to_dynamo())

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"Week": {"S": f"{week}-{channel_id}"}},
        UpdateExpression="SET Interactions = :interactions",
        ExpressionAttributeValues={":interactions": existing_item["Interactions"]},
    )
    logger.info("DB update successful")


# Load existing chat messages for the given week from Dynamo, or an empty list of interactions if none exists
def retrieve_interactions_for_week(week: str, channel_id: str) -> list[Interaction]:
    response = dynamodb.get_item(
        TableName=TABLE_NAME, Key={"Week": {"S": f"{week}-{channel_id}"}}
    )

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": f"{week}-{channel_id}"}, "Interactions": {"L": []}}
    )

    interactions = sorted(
        existing_item["Interactions"]["L"], key=lambda x: x["M"]["time"]["S"]
    )

    logger.info("interactions: %s", json.dumps(interactions, indent=2))
    return [Interaction.from_dynamo(di) for di in interactions]
