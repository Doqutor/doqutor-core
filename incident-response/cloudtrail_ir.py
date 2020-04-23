import os
import json
import boto3


print('This is a CLI for incident response on cloudTrail')
print('\nIncident: Someone disables cloudTrail')
print('Response: CloudTrail switches on itself and blocks user')

print('\nWARNING!: You might be blocked during this demonstration. Add a new user in your account and test that user.')
print('Make sure your AWS cli response is in JSON')

print('\ntype "y/n" to proceed')
decision = input()
if decision == 'y' or decision == 'Y':

    os.system('aws cloudtrail list-trails > trails.json')
    f = None
    try:
        # Opening JSON file
        f = open('trails.json')

        # returns JSON object as
        data = json.load(f)

        trail_arn = None
        if len(data['Trails']) >= 1:
            trail_arn = data['Trails'][0]['TrailARN']

        if not trail_arn:
            print('\nWarning: You do not have any Trails at the moment. Please create one to test this IR')
        else:
            print(f'\nSwitching off trail with ARN : {trail_arn}')
            cloudtrail_client = boto3.client('cloudtrail')
            cloudtrail_client.stop_logging(Name=trail_arn)
            print('Logging OFF, the user should now be blocked')
            print('\nPlease wait for few mins to test the Automated response, check your access type "check"')
            input_string = ''
            while input_string != 'exit':
                print('type "check" or "exit"')
                input_string = input()
                if input_string == 'check':
                    os.system('aws cloudtrail list-trails')

    except:
        print("An exception occurred")
    finally:
        f.close()
        if os.path.exists("trails.json"):
            os.remove("trails.json")
else:
    print('exiting!')

