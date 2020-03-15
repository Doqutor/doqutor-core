import boto3
import logging
import json
import os
import uuid


def main(event, context):
    if event["request"]["userAttributes"]["sub"]:
        write_to_ddb(event)

def write_to_dbb(event):
    table_name = os.environ.get('TABLE_NAME')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # make info readable to python and then ship it off to dynamo
    event_data = event["request"]["userAttributes"]
    u_id = str(uuid.uuid4())[0:8]
    table.put_item(Item={
        'u_id': u_id, 
        'doctor_id': event_data["sub"],
        'given_name': event_data["given_name"],
        'family_name': event_data["family_name"],
        'spec': event_data["spec"],
        'email': event_data["email"],
        'password': event_data["password"]
    })

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'doctor created with name : {given_name} {family_name}'
    }
