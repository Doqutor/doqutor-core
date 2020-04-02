import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)

def main(event, context):
    log_event(event)

    params = event['pathParameters']
    _id = params['id']

    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"doctor with id {_id} does not exist")
