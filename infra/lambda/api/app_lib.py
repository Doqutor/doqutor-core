import boto3
import os
import json
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INCL_HEADERS = {
    'access-control-allow-origin': '*',
    'cache-control': 'no-cache'
}

def log_event(event):
    logger.info(json.dumps(event))

def get_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)

def get_body(event):
    return json.loads(event['body'])

def send_response(statusCode=200, data={}, headers=None):
    if headers != None:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}, default=decimal_default),
            'headers': {**headers, **INCL_HEADERS}
        }
    else:
        return {
            'statusCode': statusCode,
            'body': json.dumps({'data': data}, default=decimal_default),
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


def get_user(event):
    client = boto3.client('cognito-idp')
    # check if the role is either doctor or patient
    # headers are case sensitive for some reason
    pool_id = event['requestContext']['authorizer']['claims']['iss'].split('/')[-1]
    username = event['requestContext']['authorizer']['claims']['username']
    res = client.admin_get_user(UserPoolId=pool_id, Username=username)
    return {
        'username': res['Username'],
        'attributes': {
            i['Name']: i['Value'] for i in res['UserAttributes']
        },
        'status': res['UserStatus']
    }

def get_role(user):
    return user['attributes']['custom:type']

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    return obj


# ideally will eventually have this inside custom authorizer
# or maybe not, it might not be worth the complication and extra lambda latency
def checkToken(tokenstable, eventHeaders):
    # if token in table, deny
    if eventHeaders is not None and 'Authorization' in eventHeaders:
        token = eventHeaders['Authorization'].split("Bearer ", 1)[1]
        print(token)
        data = tokenstable.get_item(Key={'token': token})
        if "Item" in data:
            return False
    return True
