import boto3
import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
dynamodbexceptions = boto3.client('dynamodb').exceptions
tokens_table_name = os.environ.get('TOKENS_TABLE_NAME')
tokens_table = get_table(tokens_table_name)

def main(event, context):
    if not checkToken(tokens_table, event['headers']):
        log_event({"result": "lambda called using revoked token"})
        return send_error(401, 'The incoming token has been revoked')
        
    log_event(event)
    params = event['pathParameters']
    _id = params['id']

    try:
        table.delete_item(Key={ 
            'id': _id
        }, ConditionExpression='attribute_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        return send_error(400, f"doctor with id {_id} does not exist")

    return send_response()