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

    try:
        table.delete_item(Key={ 
            'id': _id
        }, ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        return send_error(400, f"item with id {_id} does not exist")

    return send_response()