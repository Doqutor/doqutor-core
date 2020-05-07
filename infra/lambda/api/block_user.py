from app_lib import *
import gzip
import json
import base64
import boto3
import os
import time
iam = boto3.client('iam')
cognito = boto3.client('cognito-idp')
sns = boto3.client('sns')

# this is in api folder because I get permission issues with lambdas in util folder
# ideally it would be in util folder

# Logs event and errors

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)
userpoolid = os.environ.get('USERPOOL_ID')
snsarn = os.environ.get('SNS_TOPIC_ARN')
# can get userpool id from iss field like: "https://cognito-idp.ap-southeast-2.amazonaws.com/ap-southeast-2_CzNUhN04s"
# but I'm not sure that that will always be accurate

def main(event, context):
    fields = interpretEvent(event)
    userArn = fields['requestContext']['identity']['userArn']
    sourceip = fields['requestContext']['identity']['sourceIp']
    requesttime = fields['requestContext']['requestTime'] # should this be sent to sns as local or GMT?

    if userArn is not None:
        # lambda was triggered by user -> block user
        username = userArn.split("/", 1)[1]
        print(username)
        try:
            iam.attach_user_policy(UserName = username, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll') # returns none
            publish(f'INCIDENT RESPONDED: Honeytoken triggered by AWS user {username} -> user blocked successfully', f'Honeytoken triggered by AWS user {username}\nfrom IP {sourceip}\nat {requesttime}.\nAWS user blocked.')
        except:
            publish(f'INCIDENT RESPONSE FAILED: Honeytoken triggered by AWS user {username}', f'Honeytoken triggered by AWS user {username}\nfrom IP {sourceip}\nat {requesttime}.\nFailed to apply deny policy to IAM account. Please investigate.')
    elif fields['headers'] is not None and 'Authorization' in fields['headers']:
        # lambda triggered through api call -> block cognito user and invalidate token
        error = False
        message = ''
        # retrieve token and claims
        username, token, expiry = extractAuth(fields)
        # print(token)
        
        # convert text expiry in lambda logs to epoch time
        expiryepoch = int(time.mktime(time.strptime(expiry, '%a %b %d %H:%M:%S %Z %Y')))

        # add token to invalidated tokens database
        # old tokens are cleared with dynamodb ttl
        item = {'token': token, 'expiry': expiryepoch}
        error, message = addToDB(item)
        cognitoError, cognitoMessage = disableUser(username)
        message += cognitoMessage
        error |= cognitoError

        if not error:
            publish(f'INCIDENT RESPONDED: Honeytoken triggered by Cognito user {username} -> user blocked successfully', f'Honeytoken triggered by cognito user {username}\nfrom IP {sourceip}\nat {requesttime}.\n' + message)
        else:
            publish(f'INCIDENT RESPONSE FAILED: Honeytoken triggered by Cognito user {username}', f'Honeytoken triggered by cognito user {username}\nfrom IP {sourceip}\nat {requesttime}.\n' + message)
    # else: pass
        # not possible with current setup afaik
    

# sns.publish() wrapper
def publish(subject: str, message: str):
    sns.publish(TopicArn = snsarn, Subject=subject, Message=message)

# Subscription filter destination receives event compressed and encoded
# This decompresses, decomposes and loads relevant part into JSON
# subscription filter format, which informs extractedFields in this function:
# [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*a3a...*]
def interpretEvent(event: dict) -> dict:
    encodeddata = event['awslogs']['data']
    decodeddata = base64.b64decode(encodeddata)
    uncompresseddata = gzip.decompress(decodeddata)
    payload = json.loads(uncompresseddata)
    print(payload)
    #log_event(payload)
    return json.loads(payload['logEvents'][0]['extractedFields']['event'])

# returns username, token, expiry from jwt claims
def extractAuth(fields: dict) -> (str, str, str):
    claims = fields['requestContext']['authorizer']['claims']
    expiry = claims['exp']
    username = claims['username']
    authHeader = fields['headers']['Authorization']
    token = authHeader.split("Bearer ", 1)[1]
    # check split failure
    return username, token, expiry

# Add item to database
# Returns error (true if error, false if success), message
def addToDB(item: dict) -> (bool, str):
    try:
        response = table.put_item(Item=item) # raises exception on failure
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()
        return False, "User's token invalidated\n"
    except Exception as err:
        print(err)
        return True, "Could not invalidate user's token\n"

# Sign out and disable user from Cognito user pool
# Returns error (True if error, False if success), message
def disableUser(username: str) -> (bool, str):
    try:
        # these cognito functions raise exceptions on failure, hence try/except, raise Exception() structure
        response = cognito.admin_user_global_sign_out(UserPoolId = userpoolid, Username = username)
        # print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()
        response = cognito.admin_disable_user(UserPoolId = userpoolid, Username = username)
        # print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()
        return False, "User signed out and disabled\n"
    except Exception as err:
        print(err)
        return True, 'User could not be signed out and disabled\n'


# expiryepoch:
# the expiry in the lambda logs is in a text time format
# the expiry in the jwt is epoch
# could use a library to read jwt directly to get epoch, but would have to provide dependency (eg jose) with lambda
# or could convert text back to epoch
# or just use approximate expiry time and use current epoch or requestTimeEpoch from logs
# date format is based on old logs, wasn't able to verify that seconds is zero padded
# "Wed Apr 08 13:25:30 UTC 2020"
