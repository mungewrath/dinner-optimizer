import logging
import boto3

dynamodb = boto3.client("dynamodb")

TABLE_NAME = "UserResponseTable"
WEEK = "07-29-2023"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


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
    logger.info("DB update successful")
