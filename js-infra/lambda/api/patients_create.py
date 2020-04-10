import os
import uuid
import boto3
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
dynamodbexceptions = boto3.client('dynamodb').exceptions

def main(event, context):
    log_event(event)
    body = get_body(event)

    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'email': body['email'],
        'phone_number': body['phone_number'],
        'age': body['age'],
        'is_active': body.get('is_active', True)
    }

    try:
        data = table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        return send_error(400, f"item with id {id_} already exists. please try adding again. And watch yourself because you are very unlucky.")
        
    return send_response(200, item)