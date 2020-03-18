import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    # TODO: much more resilant testing
    # remove after debug and change fields delievered by cognito json
    LOG.info("EVENT: " + json.dumps(event))
    if event["request"]["userAttributes"]["sub"]:
        write_to_ddb(event)

def write_to_ddb(event):
    table_name = os.environ.get('TABLE_NAME')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # make info readable to python and then ship it off to dynamo
    event_data = event["request"]["userAttributes"]
    u_id = str(uuid.uuid4())[0:8]
    table.put_item(Item={
        'id': u_id, 
        'doctor_id': event_data["sub"],
        'name': event_data["name"],
        'age': event_data["age"],
        'spec': event_data["spec"]
    })

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'COGNITO: doctor created with name : {name} age: {age} spec: {spec}'})
    }
