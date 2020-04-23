import boto3
import logging
import os
import json

TABLE_NAME = os.getenv('TABLE_NAME')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def main(event, context):
    print(json.dumps(event))
    if event['Records'][0]['eventName'] == 'MODIFY':
        print('modify event')
        curr = event['Records'][0]
        # check on non alterable value
        new_image = curr['dynamodb']['NewImage']['insurance_id']['S']
        old_image = curr['dynamodb']['OldImage']['insurance_id']['S']
        print("new: " + new_image + " old: " + old_image)
        if new_image != old_image:
            # trigger a "rollback" on bad value editing
            print("rollback occurred")
            print(curr['dynamodb']['Keys']['id']['S'])
            table = dynamodb.Table(TABLE_NAME)
            print(table.creation_date_time)
            restore_item = {
                'id': curr['dynamodb']['Keys']['id']['S'],
                'name': curr['dynamodb']['OldImage']['name']['S'],
                'email': curr['dynamodb']['OldImage']['email']['S'],
                'phone_number': curr['dynamodb']['OldImage']['phone_number']['S'],
                'age': curr['dynamodb']['OldImage']['age']['S'],
                'is_active': curr['dynamodb']['OldImage']['is_active']['BOOL'],
                'insurance_id': curr['dynamodb']['OldImage']['insurance_id']['S']
            }
            response = table.put_item(Item=restore_item)
            print(response)
    
    return event
     