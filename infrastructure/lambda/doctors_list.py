import boto3
import logging
import json
import os
import uuid

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

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
        'headers': {'Content-Type': 'text/plain'},
        'body': str(response["Items"])
            # aws requires body in quotes or crash
            # but this doesn't work quite right
    }
    