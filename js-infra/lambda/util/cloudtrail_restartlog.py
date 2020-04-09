import boto3
import logging
import os

TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('cloudtrail')

def main(event, context):
    logger.info('Event details: %s', event['detail'])
    trail_arn = event['detail']['requestParameters']['name']
    action = event['detail']['eventName']

    if action == 'StopLogging' and trail_arn == TRAIL:
        client.start_logging(Name=trail_arn)
        logger.info('restarted cloudtrail with arn %s', trail_arn)
    else:
        logger.info('some other arn or event, not our problem')

    return event