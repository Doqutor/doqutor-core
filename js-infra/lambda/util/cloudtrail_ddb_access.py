import boto3
import logging
import os
import json

TABLE_NAME = os.getenv('TABLE_NAME')
SNS_ARN = os.getenv('SNS_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
cloudtrail = boto3.client('cloudtrail')
sns = boto3.client('sns')

def publish_logging(client, sns_arn, subject, patient_id, modify_data):
    client.publish(
        TargetArn=sns_arn,
        Subject=subject,
        Message=f'Unauthorised modification of patient table data type {modify_data} on id: {patient_id}',
    )

def main(event, context):
    print(json.dumps(event))
    if event['Records'][0]['eventName'] == 'MODIFY':
        print('modify event')
        curr = event['Records'][0]
        # check on non alterable value
        new_image = curr['dynamodb']['NewImage']
        old_image = curr['dynamodb']['OldImage']
        new_image_insurance_id = new_image['insurance_id']['S']
        old_image_insurance_id = old_image['insurance_id']['S']
        print("new: " + new_image_insurance_id + " old: " + old_image_insurance_id)
        if new_image_insurance_id != old_image_insurance_id:
            # trigger a "rollback" on bad value editing
            print("rollback occurred")
            print(curr['dynamodb']['Keys']['id']['S'])
            table = dynamodb.Table(TABLE_NAME)
            target_id = curr['dynamodb']['Keys']['id']['S']
            restore_item = {
                'id': target_id,
                'name': old_image['name']['S'],
                'email': old_image['email']['S'],
                'phone': old_image['phone']['S'],
                'is_active': old_image['is_active']['BOOL'],
                'insurance_id': old_image['insurance_id']['S']
            }
            table.delete_item(Key={ 'id': target_id })
            response = table.put_item(Item=restore_item)
            if response:
                subject = "WARNING: Illegal write operation in Patient table"
                publish_logging(client=sns, 
                                sns_arn=SNS_ARN, 
                                subject=subject, 
                                modify_data="insurance_id",
                                patient_id=target_id)
            print(response)
                
    
    return event
     