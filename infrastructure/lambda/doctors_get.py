import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    params = event['queryStringParameters']
    if params is None:
        return None

    id_ = params['id']
    if id_ == '':
        return {
        'statusCode': 400,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'{{"error": "id cannot be empty."}}'
    }
    
    return doctor_get(id_)

def doctor_get(id_):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={
        'id': id_
    })
    if "Item" in response:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': str(response["Item"])
            # aws requires body in quotes or crash
            # but this doesn't work right - says Decimal('60') for number
        }
    else:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'{{"error": "Doctor with id {id_} does not exist."}}'
        }

        