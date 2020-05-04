import boto3
import logging
import os

TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudtrail_client = boto3.client('cloudtrail')
sns_client = boto3.client('sns')
iam = boto3.client('iam')


def publish_logging(client, sns_arn, event, subject, user, trail_arn):
    client.publish(
        TargetArn=sns_arn,
        Subject=subject,
        Message=f'CloudTrail event {event} invoked by user {user} for ARN {trail_arn}',
    )


def main(event, context):
    logger.info('Event details: %s', event['detail'])

    sns_arn = os.environ['SNS_ARN']

    trail_arn = event['detail']['requestParameters']['name']
    action = event['detail']['eventName']

    if action == 'StopLogging':
        user = event['detail']['userIdentity']['userName']

        publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='WARNING: CloudTrail stopped by user',
                        user=user, trail_arn=trail_arn)
        cloudtrail_client.start_logging(Name=trail_arn)

        #Below command is used to Block a user. Do not uncomment this for testing.
        iam.attach_user_policy(UserName=user, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')

        logger.info('restarted cloudtrail with arn %s', trail_arn)
    if action == 'StartLogging':
        publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='CloudTrail started successfully',
                        user='lambda/cloudtrail_restartlog', trail_arn=trail_arn)

    else:
        logger.info('some other arn or event, not our problem')

    return event
