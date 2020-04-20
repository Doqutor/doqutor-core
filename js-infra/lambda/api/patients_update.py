import boto3
import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
dynamodbexceptions = boto3.client('dynamodb').exceptions

def main(event, context):
    log_event(event)

    user = get_user(event)

    params = event['pathParameters']
    _id = params['id']

    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:    
        if get_role(user) != 'doctor' and user['attributes']['sub'] != data['Item']['id']:
            return send_error(403, 'you are not authorized to view this resource')
        return send_response(200, data["Item"])

    body = get_body(event)

    item = {
        'id': _id,
        'name': body['name'],
        'email': body['email'],
        'phone_number': body['phone_number'],
        'age': body['age'],
        'is_active': body.get('is_active', True)
    }

    try:
        table.put_item(Item=item, ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        return send_error(400, f"item with id {_id} does not exist")

    return send_response(200, item)