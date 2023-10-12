import json

import logging
import os
import requests

import dinner_optimizer_shared.credentials_handler as creds
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    credentials = creds.fetch_creds_from_secrets_manager()

    paprika_username = credentials["PAPRIKA_USERNAME"]
    paprika_password = credentials["PAPRIKA_PASSWORD"]

    # TODO: hardcoded for now, but ideally this should be fetched from the Paprika app
    dinner_category_id = "959A2BAB-9A79-4465-ADCE-582D7D3E982D"

    paprika_response = requests.get(
        "https://www.paprikaapp.com/api/v1/sync/recipes/",
        auth=(paprika_username, paprika_password),
    )

    recipes = paprika_response.json()
    logger.info(json.dumps(recipes))

    recipe_names = []

    for r in recipes["result"]:
        recipe_id = r["uid"]
        paprika_recipe_response = requests.get(
            f"https://www.paprikaapp.com/api/v1/sync/recipe/{recipe_id}",
            auth=(paprika_username, paprika_password),
        )
        recipe_info = paprika_recipe_response.json()["result"]
        recipe_name = recipe_info["name"]
        if dinner_category_id in recipe_info["categories"]:
            recipe_names.append(recipe_name)

    bucket_name = os.environ["BUCKET_NAME"]

    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=bucket_name,
        Key="recipe_names.json",
        Body=json.dumps(recipe_names),
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
        None,
        None,
    )


if __name__ == "__main__":
    cli()
