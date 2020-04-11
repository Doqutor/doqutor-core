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
    # cognitopool = useridentity['cognitoIdentityPoolId']
    # cognitoid = useridentity['cognitoIdentityId']
    # accessKey = useridentity['accessKey']
    token = None
    if event['headers'] is not None and 'Authorization' in event['headers']:
        token = event['headers']['Authorization']
    logger.info(json.dumps({"reqid": _id, 
    "userArn": userArn, "sourceip": sourceip, "token": token}))
    # "userArn": userArn, "sourceip": sourceip, cognitopool": cognitopool, "cognitoid": cognitoid, "accessKey": accessKey}))

    # cognitopool, cognitoid, accessKey above are always null
    # when called through API gateway authorizer, userArn is null but sourceip is set
    # authorization header is in 
    # event['headers']['Authorization']
    # in form 'Bearer {token}'


    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"doctor with id {_id} does not exist")


def checkToken(token):
    # get dirtytokens table name from env
    # if token in table, deny
    pass

