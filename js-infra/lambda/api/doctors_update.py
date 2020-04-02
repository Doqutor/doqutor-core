import boto3
import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
dynamodbexceptions = boto3.client('dynamodb').exceptions

def main(event, context):
    log_event(event)

    params = event['pathParameters']
    _id = params['id']
    body = get_body(event)

    item = {
        'id': _id,
        'given_name': body['given_name'],
        'family_name': body['family_name'],
        'email': body['email'],
        'phone_number': body['phone_number'],
        'birth_date': body['birth_date'],
        'is_active': body.get('is_active', True)
    }

    try:
        table.put_item(Item=item, ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        return send_error(400, f"doctor with id {_id} does not exist")

    return send_response(200, item)