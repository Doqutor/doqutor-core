from app_lib import *
import gzip
import json
import base64
import boto3
import os
iam = boto3.client('iam')
cognito = boto3.client('cognito-idp')

# this is in api folder because I get permission issues with lambdas in util folder

# [type=INFO, timestamp=*Z, request_id="*-*", event=*reqid*5555*]
# logger.info(json.dumps({"reqid": _id, "userArn": userArn, "sourceip": sourceip, "cognitopool": cognitopool, "cognitoid": cognitoid, "accessKey": accessKey}))
# [type=INFO, timestamp=*Z, requestid=*-*, event=*5555*]

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
userpoolid = 'ap-southeast-2_CzNUhN04s' 

def main(event, context):
    encodeddata = event['awslogs']['data']
    compresseddata = base64.b64decode(encodeddata)
    uncompresseddata = gzip.decompress(compresseddata)
    payload = json.loads(uncompresseddata)
    print(payload)
    #log_event(payload)
    # userArn = e['userArn']
    # authHeader = e['token']
    e = json.loads(payload['logEvents'][0]['extractedFields']['event'])
    userArn = e['requestContext']['identity']['userArn']
    if userArn is not None:
        # lambda was triggered by user -> block user
        username = userArn.split("/", 1)[1] # is this really a reliable way of getting the username?
        print(username)
        #Below command is used to Block a user. Do not uncomment this for testing.
        #iam.attach_user_policy(UserName = username, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')
    elif e['headers'] is not None and 'Authorization' in e['headers']:
        # lambda triggered through api call -> block cognito user and invalidate token

        # retrieve token and claims
        authHeader = e['headers']['Authorization']
        token = authHeader.split("Bearer ", 1)[1]
        # check split failure
        print(token)
        claims = e['requestContext']['authorizer']['claims']
        expiry = claims['exp']
        username = claims['username']

        # add token to invalidated tokens database
        item = {'token': token, 'expiry': expiry}
        # item = {'token': token, 'expiry': 100}
        data = table.put_item(Item=item)
        # need another lambda function triggered every hour or something that cleans the tokens that have expired

        # sign out and disable user
        # force password change with mfa or something?
        # can get userpool id from iss field like: "https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_CzNUhN04s"
        # but I'm not sure that that will always be accurate
        # or maybe pass in as env variable
        response = cognito.admin_disable_user(
            UserPoolId = userpoolid,
            Username = username
        )
        response = cognito.admin_user_global_sign_out(
        UserPoolId = userpoolid,
        Username = username
        )

        # access vs id tokens - how to invalidate both?
    else:
        pass
        # how did this get triggered?
    
# https://stackoverflow.com/questions/50295838/cloudwatch-logs-stream-to-lambda-python

'''
#from jose import jwt
import jwt
# or i could print out the claims with the doctor_get logs

def getTokenExpiry(token):
    # claims = jwt.get_unverified_claims(token)
    claims = jwt.decode(token, verify=False) # at this point assuming that cognito has verified the token
    print(claims)
    return claims['exp']
'''
# https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py