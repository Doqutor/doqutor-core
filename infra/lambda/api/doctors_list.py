import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
tokens_table_name = os.environ.get('TOKENS_TABLE_NAME')
tokens_table = get_table(tokens_table_name)
    
def main(event, context):
    if not checkToken(tokens_table, event['headers']):
        log_event({"result": "lambda called using revoked token"})
        return send_error(401, 'The incoming token has been revoked')

    log_event(event)
    
    user = get_user(event)
    role = get_role(user)
    if role != 'doctor' and role != 'patient':
        return send_error(403, 'you are not authorized to view this resource')


    data = table.scan()
    return send_response(200, data["Items"])