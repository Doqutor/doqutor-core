import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INCL_HEADERS = {
    'access-control-allow-origin': '*'
}

def log_event(event):
    logger.info(json.dumps(event))

def get_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)

def get_body(event):
    return event['body']

def send_response(statusCode=200, data={}, headers=None):
    if headers != None:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}),
            'headers': {**headers, **INCL_HEADERS}
        }
    else:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}),
            'headers': {**INCL_HEADERS}
        }

def send_error(statusCode=500, error='internal server error', headers=None):
    if headers != None:
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": error}),
            'headers': {**headers, **INCL_HEADERS}
        }
    else:
        return {
            'statusCode': statusCode,
            'body': json.dumps({"error": error}),
            'headers': {**INCL_HEADERS}
        }