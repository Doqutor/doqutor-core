import boto3
import logging
import os
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client('sns')

# Global variable hack is a temporary fix
# Serverless functions should be stateless and idempotent
# This should work 99% of the time
# In the event that this hot fix doesn't work, the repercussions are insignificant
# It will just trigger the CI/CD pipeline multiple times which will queue them up on GitHub Actions
already_run = False

def publish_logging(client, sns_arn, event, subject, user):
    client.publish(
        TargetArn=sns_arn,
        Subject=subject,
        Message=f'CloudTrail event {event} invoked by user {user}',
    )

def main(event, context):
    global already_run
    if already_run:
        return
    
    already_run = True

    logger.info('Event details: %s', event['detail'])

    sns_arn = os.environ['SNS_ARN']

    user = event['detail']['userIdentity']['userName']
    if user == 'frontend-deployment':
        return event
    
    reqUrl = "https://api.github.com/repos/Doqutor/doqutor-frontend/dispatches"
    reqJson = {"event_type": "Redeploy from webhook!"}
    reqAuth = ('aws-devops-bot', '047ffcdcb64eb943171429ea7fd34ebb9efc1ba1')
    reqHeaders = {"Accept":"application/vnd.github.everest-preview+json"}
    r = requests.post(reqUrl, json=reqJson, auth=reqAuth, headers=reqHeaders)
    return event
