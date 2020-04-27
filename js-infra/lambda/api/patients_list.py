import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
    
def main(event, context):
    log_event(event)

    user = get_user(event)
    if get_role(user) != 'doctor':
        return send_error(403, 'you are not authorized to view this resource')

    data = table.scan()
    return send_response(200, data["Items"])