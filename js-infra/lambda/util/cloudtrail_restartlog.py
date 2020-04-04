import boto3
import logging
import os
import json

TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudtrail_client = boto3.client('cloudtrail')
sns_client = boto3.client('sns')


def publish_logging(client, sns_arn, event):
    event_name = event['detail']['eventName']
    user_name = event['detail']['userIdentity']['userName']
    print(event)
    client.publish(
        TargetArn=sns_arn,
        Message=f'CloudTrail event  invoked by user {user_name}. Stating cloudtrail with ARN : {sns_arn} again',
    )


def main(event, context):
    logger.info('Event details: %s', event['detail'])
    trail_arn = event['detail']['requestParameters']['name']
    action = event['detail']['eventName']

    sns_arn = os.environ['SNS_ARN']

    if action == 'StopLogging' and trail_arn == TRAIL:
        publish_logging(client=sns_client, sns_arn=sns_arn, event=event)
        cloudtrail_client.start_logging(Name=trail_arn)
        logger.info('restarted cloudtrail with arn %s', trail_arn)

    else:
        logger.info('some other arn or event, not our problem')

    return event