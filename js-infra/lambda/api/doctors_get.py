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
    if not checkToken(tokens_table, event['headers']):
        log_event({"result": "lambda called using revoked token"})
        return send_error(401, 'The incoming token has been revoked')
        # should use {"message": ..} not {"error": ..}

    log_event(event)
    user = get_user(event)
    if get_role(user) != 'doctor':
        return send_error(403, 'you are not authorized to view this resource')

    params = event['pathParameters']
    _id = params['id']

    data = table.get_item(Key={
        'id': _id
    })

    if "Item" in data:
        return send_response(200, data["Item"])
    
    return send_error(400, f"doctor with id {_id} does not exist")



'''
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
    '''

