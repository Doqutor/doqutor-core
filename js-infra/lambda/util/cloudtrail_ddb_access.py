import boto3
import logging
import os
import json

TABLE_ARN = os.getenv('TABLE_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iam')
iam = boto3.resource('iam')

# block all access to IAM
def make_iam_policy():
    iam_deny_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Deny",
                "Action": "iam:*",
            "Resource": "*"
            }
        ]
    }
            
    iam_block = client.create_policy(
        PolicyName='blockIAMaccess',
        PolicyDocument=json.dumps(iam_deny_policy)
    )
    return iam_block
    


def main(event, context):
    #logger.info('Event details: %s', event['userIdentity'])
    print(json.dumps(event))
    action = event['detail']['userIdentity']
    username = action["userName"]
    if action["type"] == "IAMUser":
        user = iam.User(username)
        group = iam.Group("adminusers")
        admin_users = group.users.all()
        if user in admin_users:
            print(username + " is admin")
            policies = client.list_policies(Scope='Local')
            policy_list = policies['Policies']
            hasIAMPolicy = False
            iam_arn = ""
            for policy in policy_list:
                if policy['PolicyName'] == 'blockIAMaccess':
                    hasIAMPolicy = True
                    iam_arn = policy['Arn']


            if hasIAMPolicy:
                user.attach_policy(PolicyArn=iam_arn)
            else:
                iam_policy = make_iam_policy()
                user.attach_policy(PolicyArn=iam_policy['Policy']['Arn'])
    return event
     