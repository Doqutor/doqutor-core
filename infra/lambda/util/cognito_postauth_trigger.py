import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    if event["request"]["userAttributes"]["sub"]:
        write_to_ddb(event)
    else:
        raise Exception("some random weird error occurred")
    
    return event
    

def write_to_ddb(event):
    doctor_table_name = os.environ.get('DOCTOR_TABLE')
    patient_table_name = os.environ.get('PATIENT_TABLE')
    dynamodb = boto3.resource('dynamodb')
    attr = event["request"]["userAttributes"]
    
    if 'custom:type' not in attr:
        raise Exception('no user type specified')

    if attr['custom:type'] == 'doctor':
        table = dynamodb.Table(doctor_table_name)
    elif attr['custom:type'] == 'patient':
        table = dynamodb.Table(patient_table_name)
    else:
        raise Exception(f"invalid user type {repr(attr['custom:type'])}")

    # make info readable to python and then ship it off to dynamo
    item = table.get_item(Key={'id':attr['sub']})
    if 'Item' in item:
        table.update_item(Key={'id':attr['sub']}, AttributeUpdates={
            'name': {
                'Value': attr.get('given_name', '') + ' ' + attr.get('family_name', ''),
                'Action': 'PUT'
            },
            'email': {
                'Value': attr.get('email', ''),
                'Action': 'PUT'
            },
            'phone_number': {
                'Value': attr.get('phone_number', ''),
                'Action': 'PUT'
            },
            'is_active': {
                'Value': True,
                'Action': 'PUT'
            }
        })       
        LOG.info(f"{attr['custom:type']} account with id {attr['sub']} updated")
    else:
        table.put_item(Item={
            'id': attr['sub'],
            'name': attr.get('given_name', '') + ' ' + attr.get('family_name', ''),
            'email': attr.get('email', ''),
            'phone_number': attr.get('phone_number', ''),
            'is_active': True
        }) 
        LOG.info(f"{attr['custom:type']} account with id {attr['sub']} created")



    
