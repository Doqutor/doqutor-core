import os
import json
import boto3


print('This is a CLI for incident response on cloudTrail')
print('Incident: Someone disables cloudTrail')
print('Response: CloudTrail switches on itself and blocks user')
print('Make sure your AWS cli response is in JSON')

os.system('aws cloudtrail list-trails > trails.json')

try:
    # Opening JSON file
    f = open('trails.json')

    # returns JSON object as
    data = json.load(f)

    trail_arn = None
    if len(data['Trails']) >= 1:
        trail_arn = data['Trails'][0]['TrailARN']

    if not trail_arn:
        print('Warning: You do not have any Trails at the moment. Please create one to test this IR')
    else:
        print(f'Switching off trail with ARN : {trail_arn}')
        cloudtrail_client = boto3.client('cloudtrail')
        cloudtrail_client.stop_logging(Name=trail_arn)
        print('Logging OFF, the user should now be blocked')


except:
    print("An exception occurred")
finally:
  f.close()