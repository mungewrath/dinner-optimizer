import boto3
import datetime

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")
SOURCE_TABLE_NAME = "UserResponseTable_from_01-17-2025"
DESTINATION_TABLE_NAME = "DinnerOptimizerHistory"

# Replace with your table name
source_table = dynamodb.Table(SOURCE_TABLE_NAME)
destination_table = dynamodb.Table(DESTINATION_TABLE_NAME)


def get_previous_monday(saturday_date_str):
    """
    Converts a Saturday (YYYY-MM-DD format) into the preceding Monday.
    Example: '11-02-2024' -> '10-28-2024'
    """
    saturday_date = datetime.datetime.strptime(saturday_date_str, "%m-%d-%Y").date()
    # Validate that the input is actually a Saturday to avoid unexpected behavior
    if saturday_date.weekday() != 5:
        raise ValueError(f"{saturday_date_str} is not a Saturday!")

    # Calculate the previous Monday
    previous_monday = saturday_date - datetime.timedelta(days=5)
    return previous_monday.strftime("%m-%d-%Y")


def migrate_table():
    """
    Scans the source DynamoDB table, updates partition keys, and uploads to the new table.
    """
    response = source_table.scan()
    items = response.get("Items", [])

    # Batch write items to the new table with updated keys
    with destination_table.batch_writer() as batch:
        for item in items:
            saturday_key = item.get("Week")
            if not saturday_key:
                print("Item is missing the partition key: ", item)
                continue

            try:
                split = saturday_key.split("_")
                saturday_date = split[0]
                monday_date = get_previous_monday(saturday_date)
                item["Week"] = f"{monday_date}_{split[1]}"  # Update the partition key
            except ValueError as e:
                print(f"Skipping item due to invalid date format or logic: {e}")
                continue

            batch.put_item(Item=item)
            batch.delete_item(
                Key={
                    "Week": monday_date + split[1],
                }
            )

    print(f"Migrated {len(items)} items to the destination table.")


migrate_table()
