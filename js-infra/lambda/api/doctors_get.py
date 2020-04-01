import os
from app_lib import send_response, send_error, get_table, logger, log_event

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)

def main(event, context):
    log_event(event)
    
    params = event['pathParameters']
    if not params and 'id' not in params:
        return send_error(400, 'no id specified')
    
    _id = params['id']

    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_response(400, f"item with id {_id} does not exist")
