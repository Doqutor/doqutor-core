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
    if body == {}:
        return {
        'statusCode': 400,
        }

    try:
        id_ = body['id']
        name = body['name'] 
        age = body['age'] 
        spec = body['spec']
    except KeyError:
        return {
        'statusCode': 400,
        'headers': {'Content-Type': 'text/plain'},
        'body': '{"error": "Missing argument field(s). Need id, name, age and spec."}'
        }
    else:
        inputError = validateInput(id_, name, age, spec)
        if inputError is not None:
            return inputError
        else:
            return doctor_update(id_, name, age, spec)

def doctor_update(id_, name, age, spec):
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    dynamodbexceptions = boto3.client('dynamodb').exceptions
    table = dynamodb.Table(table_name)

    try:
        response = table.put_item(Item={
        'id': id_,
        'name': name,
        'age': age,
        'spec': spec,
        },
        ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        statusCode = 400
        body = f'{{"error": "Doctor with id {id_} does not exist and cannot be updated. A new doctor has not been created."}}'
    else:
        statusCode = 200
        body = f'[Status: {response["ResponseMetadata"]["HTTPStatusCode"]}] Updating doctor id {id_} with new information Name: {name}. Age: {age}. Specialisation: {spec}'

    return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': body
    }

def validateInput(id_, name, age, spec):
    statusCode = 400
    LOG.info("id: " + id_)
    if id_ == "":
        return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'{{"error": "Doctor not updated. ID cannot be empty."}}'
        }

    LOG.info("name: " + name)
    if name == "":
        return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'{{"error": "Doctor not created. Name cannot be empty."}}'
        }
    
    LOG.info("age: " + str(age))
    if not isinstance(age, int) or age < 0 or age > 200: # should it allow number as string?
        return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'{{"error": "Doctor not created. Age must be an integer 0-200"}}'
        }
    
    LOG.info("spec: " + spec)
    if spec == '':
        return {
        'statusCode': statusCode,
        'headers': {'Content-Type': 'text/plain'},
        'body': f'{{"error": "Doctor not created. Specialsation cannot be empty."}}'
        }

    return None