import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    #params = event['queryStringParameters']
    params = event['pathParameters']

    # TODO: probably remove this checking
    if params is None:
        return {
        'statusCode': 400,
        'body': '{"error": "aws wtf"}'
        }

    try:
        id_ = params['id']
    except KeyError:
        return {
            'statusCode': 400,
            'body': '{"error": "aws no. Missing field: id."}'
        }
    else:
        if id_ == '':
            return {
            'statusCode': 400,
            'body': '{"error": "aws bad. id cannot be empty."}'
        }
    # end remove
    
    return doctor_delete(id_)

def doctor_delete(id_):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    dynamodbexceptions = boto3.client('dynamodb').exceptions
    table = dynamodb.Table(table_name)

    try:
        response = table.delete_item(
        Key={ 
            'id': id_
        }, 
        ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        statusCode = 400
        body = json.dumps({"error": f"Doctor with id {id_} does not exist and cannot be deleted."})
    else:
        statusCode = 200
        body = json.dumps({"message": f"Deleting doctor: {id_}"})
        
    return {
        'statusCode': statusCode,
        'body': body
    }

# 'headers': {'Content-Type': 'text/plain'},
