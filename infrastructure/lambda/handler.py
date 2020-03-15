import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    query_string_params = event["queryStringParameters"]
    if query_string_params is not None:
        name = query_string_params['name']
        if name is not None:
            return create_doctor(event)

def create_doctor(event):
    table_name = os.environ.get('TABLE_NAME')

    name = event["queryStringParameters"]["name"]

    id = str(uuid.uuid4())[0:8]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={
        'id': id,
        'name': name
    })

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'doctor created with name : {name}'
    }