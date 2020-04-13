from app_lib import *
import gzip
import json
import base64
import boto3
import os
iam = boto3.client('iam')
cognito = boto3.client('cognito-idp')
sns = boto3.client('sns')

import time

# this is in api folder because I get permission issues with lambdas in util folder

# "\"path\": \"/doctors/5555\""
# [type=INFO, timestamp, somecode, label=*id*, id=5555, ...]
# [type=INFO, timestamp=*Z, request_id="*-*", event=*reqid*5555*]
# logger.info(json.dumps({"reqid": _id, "userArn": userArn, "sourceip": sourceip, "cognitopool": cognitopool, "cognitoid": cognitoid, "accessKey": accessKey}))
# [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb*]
# [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*5555*]


table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
userpoolid = os.environ.get('USERPOOL_ID')
snsarn = os.environ.get('SNS_TOPIC_ARN')

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
    sourceip = e['requestContext']['identity']['sourceIp']
    requesttime = e['requestContext']['requestTime'] # should this be sent to sns as local or GMT?

    # todo: can trigger sns from lambda?

    if userArn is not None:
        # lambda was triggered by user -> block user
        username = userArn.split("/", 1)[1] # is this really a reliable way of getting the username?
        print(username)
        #Below command is used to Block a user. Do not uncomment this for testing.
        #iam.attach_user_policy(UserName = username, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')
        sns.publish(TopicArn=snsarn, Message=f'Honeytoken triggered by AWS user {username}\nfrom IP {sourceip}\nat {requesttime}.\n User has been blocked.')
    elif e['headers'] is not None and 'Authorization' in e['headers']:
        # lambda triggered through api call -> block cognito user and invalidate token

        # retrieve token and claims
        authHeader = e['headers']['Authorization']
        token = authHeader.split("Bearer ", 1)[1]
        # check split failure
        # print(token)
        claims = e['requestContext']['authorizer']['claims']
        expiry = claims['exp']
        username = claims['username']

        # the expiry in the lambda logs is in a text time format
        # the expiry in the jwt is epoch
        # could use a library to read jwt directly to get epoch,
        # or avoid having to provide dependecy and convert text back to epoch
        # or just use approximate expiry time and use current epoch or requestTimeEpoch from logs
        # date format is based on old logs, wasn't able to verify that seconds is zero padded
        # "Wed Apr 08 13:25:30 UTC 2020"
        expiryepoch = int(time.mktime(time.strptime(expiry, '%a %b %d %H:%M:%S %Z %Y')))

        # add token to invalidated tokens database
        item = {'token': token, 'expiry': expiryepoch}
        data = table.put_item(Item=item)
        # old tokens cleared with dynamodb ttl

        # sign out and disable user
        # force password change with mfa or something?
        # can get userpool id from iss field like: "https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_CzNUhN04s"
        # but I'm not sure that that will always be accurate
        response = cognito.admin_disable_user(
            UserPoolId = userpoolid,
            Username = username
        )
        response = cognito.admin_user_global_sign_out(
        UserPoolId = userpoolid,
        Username = username
        )

        sns.publish(TopicArn=snsarn, Message=f'Honeytoken triggered by cognito user {username}\nfrom IP {sourceip}\nat {requesttime}.\n User has been blocked.')

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

# https://www.programiz.com/python-programming/datetime/strptime
# https://stackoverflow.com/questions/7241170/how-to-convert-current-date-to-epoch-timestamp