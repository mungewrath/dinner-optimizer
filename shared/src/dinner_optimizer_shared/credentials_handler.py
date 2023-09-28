import boto3
from botocore.exceptions import ClientError
import json

SECRET_NAME = "dinner-optimizer-credentials"


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
