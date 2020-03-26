import boto3
import logging
import json
import os
import uuid
from decimal import Decimal

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

CORSheaders = { 'Access-Control-Allow-Origin': '*' }

def main(event, context):
    LOG.info("EVENT (delete): " + json.dumps(event))
    
    return doctor_list()

def doctor_list():
    table_name = os.environ.get('TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan()

    return {
        'statusCode': 200,
        'headers': CORSheaders,
        'body': json.dumps(response["Items"], default=decimal_default)
    }
    #'body': str(response["Items"])
    # AWS is requiring body be a string, str(response["Items"]) gives Decimal('60') for numbers. hence the json.dumps
    
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    return obj
    