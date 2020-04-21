import boto3
import logging
import os
import json

TABLE_ARN = os.getenv('TABLE_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iam')
iam = boto3.resource('iam')

# a small note, this policy document should be altered if global table and/or backups are used
def make_ddb_policy():
    ddb_iam_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Deny",
                "Action": [
                    "dynamodb:BatchGetItem",
                    "dynamodb:ConditionCheckItem",
                    "dynamodb:DescribeTable",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:ListTagsOfResource",
                    "dynamodb:Query",
                    "dynamodb:DescribeTimeToLive",
                    "dynamodb:DescribeTableReplicaAutoScaling"
                ],
                "Resource": TABLE_ARN
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Deny",
                "Action": [
                    "dynamodb:DescribeReservedCapacityOfferings",
                    "dynamodb:DescribeReservedCapacity",
                    "dynamodb:DescribeLimits",
                    "dynamodb:ListStreams"
                ],
            "Resource": "*"
            }
        ]
    }
    ddb_block = client.create_policy(
        PolicyName='blockDynamoDBAccess',
        PolicyDocument=json.dumps(ddb_iam_policy)
    )
    return ddb_block

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
    action = event['userIdentity']
    username = action["userName"]
    if action["type"] == "IAMUser":
        user = iam.User(username)
        group = iam.Group("adminusers")
        admin_users = group.users.all()
        if user in admin_users:
            print(username + " is admin")
            policies = client.list_policies(Scope='Local')
            #print(policies)
            policy_list = policies['Policies']
            #print(policies['Policies'][2]['PolicyName'])
            hasDbPolicy = False
            hasIAMPolicy = False
            ddb_arn = ""
            iam_arn = ""
            for policy in policy_list:
                if policy['PolicyName'] == 'blockDynamoDBAccess':
                    hasDbPolicy = True
                    ddb_arn = policy['Arn']
                elif policy['PolicyName'] == 'blockIAMaccess':
                    hasIAMPolicy = True
                    iam_arn = policy['Arn']

            
            if hasDbPolicy:
                user.attach_policy(PolicyArn=ddb_arn)
            else:
                ddb_policy = make_ddb_policy()
                user.attach_policy(PolicyArn=ddb_policy['Policy']['Arn'])

            #if hasIAMPolicy:
            #    user.attach_policy(PolicyArn=iam_arn)
            #else:
            #    iam_policy = make_iam_policy()
            #    user.attach_policy(PolicyArn=iam_policy['Policy']['Arn'])
    return event
     