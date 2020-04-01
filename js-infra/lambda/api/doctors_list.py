import os
from app_lib import send_response, get_table, logger, log_event

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
    
def main(event, context):
    log_event(event)
    
    data = table.scan()
    return send_response(200, data["Items"])