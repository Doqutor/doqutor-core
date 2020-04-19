import boto3
import logging
import os
import json

#TRAIL = os.getenv('TRAIL_ARN')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iam')
iam = boto3.resource('iam')

def main(event, context):
    #logger.info('Event details: %s', event['userIdentity'])
    action = event['userIdentity']
    username = action["userName"]
    if action["type"] == "IAMUser":
        user = iam.User(username)
        group = iam.Group("adminusers")
        admin_users = group.users.all()
        ddb_iam_policy = {}
        if user in admin_users:
            print(username + " is admin")
            ddb_iam_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "VisualEditor0",
                        "Effect": "Deny",
                        "Action": [
                            "dynamodb:ListContributorInsights",
                            "dynamodb:DescribeReservedCapacityOfferings",
                            "dynamodb:ListGlobalTables",
                            "dynamodb:ListTables",
                            "dynamodb:DescribeReservedCapacity",
                            "dynamodb:ListBackups",
                            "dynamodb:PurchaseReservedCapacityOfferings",
                            "dynamodb:DescribeLimits",
                            "dynamodb:ListStreams"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Sid": "VisualEditor1",
                        "Effect": "Deny",
                        "Action": "dynamodb:*",
                        "Resource": "*"
                    }
                ]
            }
            
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
            
            response = client.create_policy(
                PolicyName='blockDynamoDBAccess',
                PolicyDocument=json.dumps(ddb_iam_policy)
            )
            print(response['Policy']['Arn'])
            user.attach_policy(PolicyArn=response['Policy']['Arn'])
            user.attach_policy(PolicyArn=iam_block['Policy']['Arn'])

            
            #print(response)
        #return event
     