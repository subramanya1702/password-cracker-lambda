import json

import boto3

client = boto3.client('dynamodb')

# Local password cache
password_map = {}


def lambda_handler(event, context):
    # Extract shaHash from the request
    sha_hash = event['pathParameters']['shaHash']

    # Fetch password either from cache or dynamoDb
    password = fetch_password(sha_hash)

    if password is not None:
        status_code = 200
        response_body = {
            sha_hash: password
        }
    else:
        status_code = 404
        response_body = {
            "Error": "Password Not Found"
        }

    response = {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

    return response


def fetch_password(sha_hash):
    password = None

    if password_map is not None and sha_hash in password_map:
        password = password_map.get(sha_hash)
        print("Fetching from cache")
    else:
        data = client.get_item(
            TableName='PasswordsHash',
            Key={
                'Hash': {
                    'S': sha_hash
                }
            }
        )

        if 'Item' in data:
            password = str(data['Item']['Password']['S'])
            password_map[sha_hash] = password
            print("Fetching from dynamodb")

    return password
