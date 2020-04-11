from app_lib import *
import gzip
import json
import base64
import boto3
import os
import time

table_name = os.environ.get('TABLE_NAME')
table = get_table(table_name)

# triggered every 30 mins or something

def main(event, context):
    # go through entire table
    # for each element, 
        expiry = item['exp']
        if time.time() > expiry:
            table.delete_item(Key={ 
            'token': item['token']
            })