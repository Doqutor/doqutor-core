import boto3
import logging
import os
import json

TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudtrail_client = boto3.client('cloudtrail')
sns_client = boto3.client('sns')
iam = boto3.client('iam')




def publish_logging(client, sns_arn, event, subject, user):
    client.publish(
        TargetArn=sns_arn,
        Subject=subject,
        Message=f'CloudTrail event {event} invoked by user {user} for ARN {sns_arn}',
    )


def main(event, context):
    logger.info('Event details: %s', event['detail'])
    trail_arn = event['detail']['requestParameters']['name']
    action = event['detail']['eventName']

    sns_arn = os.environ['SNS_ARN']

    if action == 'StopLogging' and trail_arn == TRAIL:
        publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='WARNING: CloudTrail stopped by user',
                        user=event['detail']['userIdentity']['userName'])
        cloudtrail_client.start_logging(Name=trail_arn)

        #Below command is used to Block a user. Do not uncomment this for testing.
        #iam.attach_user_policy(UserName= event['detail']['userIdentity']['userName'], PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')

        logger.info('restarted cloudtrail with arn %s', trail_arn)
    if action == 'StartLogging' and trail_arn == TRAIL:
        publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='CloudTrail started successfully',
                        user='lambda/cloudtrail_restartlog')

    else:
        logger.info('some other arn or event, not our problem')

    return event
