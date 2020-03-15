import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    body = json.loads(event['body'])
    LOG.info("BODY: " + json.dumps(body))
    if body is None:
        return None

    id = body['id']
    LOG.info("id: " + id)
    if id is None:
        return None

    name = body['name']
    LOG.info("name: " + name)
    if name is None:
        return None
    
    age = body['age']
    LOG.info("age: " + str(age))
    if age is None:
        return None
    
    field = body['field']
    LOG.info("field: " + field)
    if field is None:
        return None
    
    return doctor_update(id, name, age, field)

def doctor_update(id, name, age, field):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.put_item(Item={
        'id': id,
        'name': name,
        'age': age,
        'field': field,
    })

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'[Status: {response["ResponseMetadata"]["HTTPStatusCode"]}] Doctor created with name: {name} and id: {id}'
    }