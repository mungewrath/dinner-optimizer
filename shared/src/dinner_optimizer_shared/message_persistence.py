import logging
import boto3

dynamodb = boto3.client("dynamodb")

TABLE_NAME = "UserResponseTable"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def record_conversation_message(entry, week):
    # Retrieve the existing item based on the key
    response = dynamodb.get_item(TableName=TABLE_NAME, Key={"Week": {"S": week}})

    # Get any existing item
    existing_item = (
        response["Item"]
        if "Item" in response
        else {"Week": {"S": week}, "Interactions": {"L": []}}
    )

    if any(
        x["M"]["timestamp"] == entry["timestamp"]
        for x in existing_item["Interactions"]["L"]
    ):
        logger.info(
            "Entry with message '%s' and timestamp %s already exists in record; skipping write",
            entry["text"],
            entry["timestamp"],
        )
        return

    existing_item["Interactions"]["L"].append({"M": entry})

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"Week": {"S": week}},
        UpdateExpression="SET Interactions = :interactions",
        ExpressionAttributeValues={":interactions": existing_item["Interactions"]},
    )
    logger.info("DB update successful")
