import boto3
import logging
import os

#TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iam')

def main(event, context):
    #logger.info('Event details: %s', event['userIdentity'])
    action = event['userIdentity']
    username = action["userName"]
    if action["type"] == "IAMUser":
        test = client.list_attached_user_policies(UserName=username)
        print(test)
    print('table accessed')

    #return event