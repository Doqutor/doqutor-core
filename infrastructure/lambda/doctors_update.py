import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    params = event['pathParameters']
    if params is None:
        return {
        'statusCode': 400,
        'body': '{"error": "aws wtf"}'
        }
    id_ = params['id']
    
    body = json.loads(event['body'])
    LOG.info("BODY: " + json.dumps(body))
    if body == {}:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing body field(s). Need name, age and spec."})
        }

    try:
        name = body['name'] 
        age = body['age'] 
        spec = body['spec']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing body field(s). Need name, age and spec."})
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
        body = json.dumps({
            "error": f"Doctor with id {id_} does not exist and cannot be updated. A new doctor has not been created."
        })
    else:
        statusCode = 200
        body = json.dumps({
            "message": f"Updating doctor id {id_} with new information Name: {name}. Age: {age}. Specialisation: {spec}"
        })

    return {
        'statusCode': statusCode,
        'body': body
    }

def validateInput(id_, name, age, spec):
    statusCode = 400
    LOG.info("id: " + id_)
    LOG.info("name: " + name)
    if id_ == "":
        return {
            'statusCode': statusCode,
            'body': json.dumps({
                "error": "Doctor not updated. ID cannot be empty."
            })
        }

    
    if name == "":
        return {
            'statusCode': statusCode,
            'body': json.dumps({
                "error": "Doctor not updated. Name cannot be empty."
            })
        }
    
    LOG.info("age: " + str(age))
    if not isinstance(age, int) or age < 0 or age > 200: # should it allow number as string?
        return {
            'statusCode': statusCode,
            'body': json.dumps({
                "error": "Doctor not updated. Age must be an integer 0-200."
            })
        }
    
    LOG.info("spec: " + spec)
    if spec == '':
        return {
            'statusCode': statusCode,
            'body': json.dumps({
                "error": "Doctor not updated. Specialisation cannot be empty."
            })
        }

    return None