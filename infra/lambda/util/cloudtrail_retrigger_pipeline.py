import boto3
import logging
import os
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client('sns')
SNS_ARN = os.environ.get('SNS_ARN', '')
GITHUB_KEY = os.environ.get('GITHUB_KEY', '')

# Global variable hack is a temporary fix
# Serverless functions should be stateless and idempotent
# This should work 99% of the time
# In the event that this hot fix doesn't work, the repercussions are insignificant
# It will just trigger the CI/CD pipeline multiple times which will queue them up on GitHub Actions
already_run = False

def publish_logging(event, user):
    sns_client.publish(
        TargetArn=SNS_ARN,
        Subject='Unauthorised frontend modification detected',
        Message=f'Unauthorised frontend deploy by user {user}. {event}',
    )

def main(event, context):
    global already_run
    if already_run:
        return
    
    already_run = True

    logger.info('Event details: %s', event['detail'])



    user = event['detail']['userIdentity']['userName']
    if user == 'frontend-deployment':
        return event

    publish_logging(event=event, user=user)
    
    reqUrl = "https://api.github.com/repos/Doqutor/doqutor-frontend/dispatches"
    reqJson = {"event_type": "Redeploy from webhook!"}
    reqAuth = ('aws-devops-bot', GITHUB_KEY)
    reqHeaders = {"Accept":"application/vnd.github.everest-preview+json"}
    r = requests.post(reqUrl, json=reqJson, auth=reqAuth, headers=reqHeaders)
    return event
