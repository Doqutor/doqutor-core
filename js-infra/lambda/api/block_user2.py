from app_lib import *
import gzip
import json
import base64
import boto3
import os
iam = boto3.client('iam')

# this is in api folder because I get permission issues with lambdas in util folder

# [type=INFO, timestamp=*Z, request_id="*-*", event=*reqid*5555*]
# logger.info(json.dumps({"reqid": _id, "userArn": userArn, "sourceip": sourceip, "cognitopool": cognitopool, "cognitoid": cognitoid, "accessKey": accessKey}))


table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)

def main(event, context):
    encodeddata = event['awslogs']['data']
    compresseddata = base64.b64decode(encodeddata)
    uncompresseddata = gzip.decompress(compresseddata)
    #log_event(uncompresseddata)
    #print(uncompresseddata)
    payload = json.loads(uncompresseddata)
    #print(payload)
    #log_event(payload)
    #print(payload['logEvents'])
    #print(payload['logEvents'][0]['extractedFields'])
    e = json.loads(payload['logEvents'][0]['extractedFields']['event'])
    #print(e)
    userArn = e['userArn']
    authHeader = e['token']
    #print(userArn)

    if userArn != None:
        username = userArn.split("/", 1)[1] # is this really a reliable way of getting the username?
        print(username)
        #Below command is used to Block a user. Do not uncomment this for testing.
        #iam.attach_user_policy(UserName = username, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')
    elif authHeader is not None:
        token = authHeader.split("Bearer ", 1)[1]
        # check split failure
        print(token)
        #expiry = getTokenExpiry(token)
        #item = {'token': token, 'expiry': expiry}
        item = {'token': token, 'expiry': 100}
        data = table.put_item(Item=item)
        # need another lambda function triggered every hour or something that cleans the tokens that have expired
        
    else:
        pass
        # how did this get triggered?
    
    
# https://stackoverflow.com/questions/50295838/cloudwatch-logs-stream-to-lambda-python

'''
from jose import jwt
#import jwt

def getTokenExpiry(token):
    claims = jwt.get_unverified_claims(token)
    return claims['exp']
'''
# https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py