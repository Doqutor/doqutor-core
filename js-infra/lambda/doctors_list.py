import boto3
import logging
import json
import os
import uuid
from decimal import Decimal

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT (list): " + json.dumps(event))
    
    return doctor_list()

def doctor_list():
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan()

    return {
        'statusCode': 200,
        'body': json.dumps(response["Items"])
    }