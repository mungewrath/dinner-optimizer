import boto3

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")

# Define the table name
table_name = "UserResponseTable"  # Replace with your actual table name

# Define the suffix to append to the partition key
suffix = "C05JEBJHNQ4"

# Access the DynamoDB table
table = dynamodb.Table(table_name)  # type: ignore

items = []

# Scan the table to fetch all items
response = table.scan()

# Loop through all items using pagination
while True:
    items.extend(response["Items"])
    # Check if there are more items to fetch
    if "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
    else:
        break

# Iterate through each item and update the partition key
with table.batch_writer() as batch:
    for item in items:
        week = item["Week"]
        new_week = f"{week}_{suffix}"

        new_contents = {**item, "Week": new_week}
        # Create a new item with the updated partition key
        batch.put_item(Item=new_contents)

for item in items:
    week = item["Week"]

    # Delete the old item with the previous partition key
    table.delete_item(Key={"Week": week})
