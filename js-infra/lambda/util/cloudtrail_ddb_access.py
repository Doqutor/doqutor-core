import boto3
import logging
import os

#TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('cloudtrail')

def main(event, context):
    logger.info('Event details: %s', event['event'])
    action = event['eventName']

    logger.info('table accessed')

    return event