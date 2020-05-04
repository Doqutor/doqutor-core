import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
tokens_table_name = os.environ.get('TOKENS_TABLE_NAME')
tokens_table = get_table(tokens_table_name)

# This is a version that just lists patient names and ids
# so patients_list doesn't give all the info of patients_get and patients_get is more meaningful
# because if people can just get all the info from patients_list then they have no reason to use patients_get and trigger honeytoken
    
def main(event, context):
    if not checkToken(tokens_table, event['headers']):
        log_event({"result": "lambda called using revoked token"})
        return send_error(401, 'The incoming token has been revoked')

    log_event(event)

    user = get_user(event)
    if get_role(user) != 'doctor':
        return send_error(403, 'you are not authorized to view this resource')

    # data = table.scan()
    response = table.scan()
    data = []
    for patient in response["Items"]:
        data.append({"id": patient["id"], "name": patient["name"], "insurance_id": patient["insurance_id"]})

    return send_response(200, data)