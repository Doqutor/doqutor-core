import boto3
import logging
import json
import os
import uuid
from decimal import Decimal

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    #params = event['queryStringParameters']
    params = event['pathParameters']
    if params is None:
        return {
        'statusCode': 400,
        'body': json.dumps({"error": "aws plz"})
        }

    try:
        id_ = params['id']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "aws wtf. Missing field: id."})
        }
    else:
        if id_ == '':
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "aws has errored. id cannot be empty."})
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
            'body': json.dumps(response["Item"], default=decimal_default)
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": f"Doctor with id {id_} does not exist."})
        }

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    return obj