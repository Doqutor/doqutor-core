import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT (delete): " + json.dumps(event))

    params = event['queryStringParameters']
    if params is None:
        return None

    id = params['id']
    if id is None:
        return None
    
    return doctor_get(id)

def doctor_get(id):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.get_item(
        Key={
            'id': id
        }
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'Yeeting you over doctor: {response["Item"]}'
    }