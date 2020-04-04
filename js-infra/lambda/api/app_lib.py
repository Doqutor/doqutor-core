import boto3
import os
import json
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CORSheaders = { 'Access-Control-Allow-Origin': '*' }

def log_event(event):
    logger.info(json.dumps(event))

def get_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)

def get_body(event):
    #return event['body']
    return json.loads(event['body'])

def send_response(statusCode=200, data={}, headers=None):
    if headers != None:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}, default=decimal_default),
            'headers': CORSheaders.update(headers)
        }
    else:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}, default=decimal_default),
            'headers': CORSheaders
        }

def send_error(statusCode=500, error='internal server error', headers=None):
    if headers != None:
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": error}),
            'headers': CORSheaders.update(headers)
        }
    else:
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": error}),
            'headers': CORSheaders
        }


    #'body': json.dumps(response["Item"], default=decimal_default)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    return obj