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

def write_to_ddb(event):
    doctor_table_name = os.environ.get('DOCTOR_TABLE')
    patient_table_name = os.environ.get('PATIENT_TABLE')
    dynamodb = boto3.resource('dynamodb')
    attr = event["request"]["userAttributes"]
    
    if attr['type'] == 'doctor':
        table = dynamodb.table(doctor_table_name)
    elif attr['type'] == 'patient':
        table = dynamodb.table(patient_table_name)
    else:
        LOG.error(f"invalid user type {repr(attr['type'])}")
        return

    # make info readable to python and then ship it off to dynamo

    table.put_item(Item={
        'id': attr['sub'],
        'family_name': attr['family_name'],
        'given_name': attr['given_name'],
        'middle_name': attr['middle_name'],
        'email': attr['email'],
        'birthdate': attr['birthdate'],
        'gender': attr['gender'],
        'phone_number': attr['phone_number']
    })

    LOG.info(f"{attr['type']} account with id {attr['sub']} updated")
    
