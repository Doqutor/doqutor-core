import os
from app_lib import *

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)

def main(event, context):
    log_event(event)
    #log_event(context)

    params = event['pathParameters']
    _id = params['id']

    # adding logging so that subscription filter on log group can see this
    useridentity = event['requestContext']['identity']
    userArn = useridentity['userArn']
    sourceip = useridentity['sourceIp']
    cognitopool = useridentity['cognitoIdentityPoolId']
    cognitoid = useridentity['cognitoIdentityId']
    accessKey = useridentity['accessKey']
    logger.info(json.dumps({"reqid": _id, 
    "userArn": userArn, "sourceip": sourceip, "cognitopool": cognitopool, "cognitoid": cognitoid, "accessKey": accessKey}))


    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"doctor with id {_id} does not exist")
