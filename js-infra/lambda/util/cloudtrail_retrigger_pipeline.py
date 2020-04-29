import boto3
import logging
import os

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
        publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='THIS IS A GOOD DEPLOY', user=user)
        return event



    publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='THIS IS A BAD DEPLOY', user=user)
    return event

    # if action == 'StopLogging':
    #     user = event['detail']['userIdentity']['userName']

    #     publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='WARNING: CloudTrail stopped by user',
    #                     user=user, trail_arn=trail_arn)
    #     cloudtrail_client.start_logging(Name=trail_arn)

    #     #Below command is used to Block a user. Do not uncomment this for testing.
    #     iam.attach_user_policy(UserName=user, PolicyArn='arn:aws:iam::aws:policy/AWSDenyAll')

    #     logger.info('restarted cloudtrail with arn %s', trail_arn)
    # if action == 'StartLogging':
    #     publish_logging(client=sns_client, sns_arn=sns_arn, event=action, subject='CloudTrail started successfully',
    #                     user='lambda/cloudtrail_restartlog', trail_arn=trail_arn)

    # else:
    #     logger.info('some other arn or event, not our problem')

    # return event
