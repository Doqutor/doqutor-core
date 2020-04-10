from app_lib import *
import gzip
import json
import base64
import boto3
iam = boto3.client('iam')

# this is in api folder because I get permission issues with lambdas in util folder


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
    #print(userArn)
    username = userArn.split("/", 1)[1] # is this really a reliable way of getting the username?
    print(username)
    #Below command is used to Block a user. Do not uncomment this for testing.
    #iam.attach_user_policy(UserName = username, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')
    
    
# https://stackoverflow.com/questions/50295838/cloudwatch-logs-stream-to-lambda-python