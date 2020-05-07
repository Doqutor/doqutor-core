import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
tokens_table_name = os.environ.get('TOKENS_TABLE_NAME')
tokens_table = get_table(tokens_table_name)

def main(event, context):
    # I moved this above the log_event because when token revoked, I don't want the lambda to log
    # something that will trigger the userblocker again
    # this may be a bit dodgy but on the other hand if we were using a custom authorizer,
    # the lambda wouldn't get run at all so clearly wouldn't log
    # Authentication: verify that token isn't revoked
    if not checkToken(tokens_table, event['headers']):
        log_event({"result": "lambda called using revoked token"})
        return send_error(401, 'The incoming token has been revoked')
        # should use {"message": ..} not {"error": ..}

    log_event(event)

    # Authentication: verify that user has right type to make this request
    user = get_user(event)
    role = get_role(user)
    if role != 'doctor' and role != 'patient':
        return send_error(403, 'you are not authorized to view this resource')

    # extract requested id from event
    params = event['pathParameters']
    _id = params['id']

    # retrieve item from database
    data = table.get_item(Key={
        'id': _id
    })

    # Return item or error if it wasn't found
    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"doctor with id {_id} does not exist")
