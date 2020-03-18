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
        'body': json.dumps({"error": "Missing argument field(s). Need name, age and spec."})
        }

    id_ = str(uuid.uuid4())[0:8]
    
    try:
        name = body['name'] 
        age = body['age'] 
        spec = body['spec']
    except KeyError:
        return {
        'statusCode': 400,
        'body': json.dumps({"error": "Missing argument field(s). Need name, age and spec."})
        }
    else:
        inputError = validate_input(name, age, spec)
        if inputError is not None:
            return inputError
        else:
            return doctor_create(id_, name, age, spec)

def doctor_create(id_, name, age, spec):
    table_name = os.environ.get('TABLE_NAME')
    #LOG.info("c1")

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    #LOG.info("c2")

    try:
        response = table.put_item(Item={
            'id': id_,
            'name': name,
            'age': age,
            'spec': spec,
        },
        ConditionExpression='attribute_not_exists(id)')
        #LOG.info("c3")
    except dynamodbexceptions.ConditionalCheckFailedException:
        #LOG.info("except")
        statusCode = 400
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": f"Doctor with {id_} already exists. Please try adding again. And watch yourself because you are very unlucky."})
        }
        
    else:
        #LOG.info("else")
        statusCode = 200
        return {
            'statusCode': statusCode,
            'body': json.dumps({"message": f"Doctor created with name: {name} and id: {id_}"})
        }
        
def validate_input(name, age, spec):
    LOG.info("name: " + name)
    if name == "":
        statusCode = 400
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": "Doctor not created. Name cannot be empty."})
        }
    
    LOG.info("age: " + str(age))
    if not isinstance(age, int) or age < 0 or age > 200: # should it allow number as string?
        statusCode = 400
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": "Doctor not created. Age must be an integer 0-200"})
        }
    
    LOG.info("spec: " + spec)
    if spec == '':
        statusCode = 400
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": "Doctor not created. Specialisation cannot be empty."})
        }

    return None