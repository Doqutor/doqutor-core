import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
tokens_table_name = os.environ.get('TOKENS_TABLE_NAME')
tokens_table = get_table(tokens_table_name)

def main(event, context):
    log_event(event)

    params = event['pathParameters']
    _id = params['id']

    if event['headers'] is not None and 'Authorization' in event['headers']:
        if not checkToken(event['headers']['Authorization']):
            return send_error(401, 'The incoming token has been revoked')

    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"item with id {_id} does not exist")


def checkToken(authHeader):
    # if token in table, deny
    token = authHeader.split("Bearer ", 1)[1]
    print(token)
    data = tokens_table.get_item(Key={'token': token})
    if "Item" in data:
        return False
    return True