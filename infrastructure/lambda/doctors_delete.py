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
        return {
        'statusCode': 400,
        }

    try:
        id_ = params['id']
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': '{"error": "Missing field: id."}'
        }
    else:
        if id_ == '':
            return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': '{"error": "id cannot be empty."}'
        }
    
    return doctor_delete(id_)

def doctor_delete(id_):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    dynamodbexceptions = boto3.client('dynamodb').exceptions
    table = dynamodb.Table(table_name)

    #print(id_)
    #headers = {'Content-Type': 'text/plain'}
    
    try:
        response = table.delete_item(
        Key={ 
            'id': id_
        }, 
        ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        statusCode = 400
        body = f'{{"error": "Doctor with id {id_} does not exist and cannot be deleted."}}'
    else:
        statusCode = 200
        body = f'[Status: {response["ResponseMetadata"]["HTTPStatusCode"]}] Deleting doctor: {id_}'
        
    return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': body
    }