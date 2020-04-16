import os
import json
import boto3
import sys
import uuid
import random


def generateName():
    return "Barry Fake"

def generateEmail(name: str):
    suffixes = ["gmail.com", "outlook.com", "bigpond.com.au", "live.com"]
    return name.replace(" ", "_") + "@" + random.choice(suffixes)

def generatePhoneNumber():
    return "+" + str(random.randint(10**10, (10**11)-1))

def generateAge():
    return random.randint(0, 100)

def generatePerson():
    name = generateName()
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': generateEmail(name),
        'phone_number': generatePhoneNumber(),
        'age': generateAge(),
        'is_active': True
    }


dynamodb = boto3.resource('dynamodb')
dynamodbexceptions = boto3.client('dynamodb').exceptions
logs = boto3.client('logs')
iam = boto3.client('iam')

if len(sys.argv) != 5:
    print(f"Usage: {sys.argv[0]} numberOfHoneyTokens tablename subscriptionFilterdestinationArn subscriptionFilterLogGroupName")
    exit()

n = int(sys.argv[1])
assert(n != 0)
tablename = sys.argv[2]#.rstrip()
destarn = sys.argv[3]#.rstrip()
loggroupName = sys.argv[4]#.rstrip()
table = dynamodb.Table(tablename)

#print(tablename)
#print(destarn)
#print(loggroupName)

ids = []

for i in range(n):
    item = generatePerson()
    try:
        data = table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
        if data['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(data)
            exit()
        ids.append(item['id'])
    except dynamodbexceptions.ConditionalCheckFailedException:
        i -= 1

# [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*5555*]
filterPattern = '[type=INFO, timestamp=*Z, requestid=*-*,'

filterPattern += ' event=*' + ids[0] + '*'
for i in range(1, len(ids)):
    filterPattern += ' || event=*' + ids[i] + '*'
filterPattern += ']'
print(filterPattern)


# atm running this will overwrite existing subscription filter
# so previous honey records will still exist in the table but will not trigger the filter
# should use describe_subscription_filters() to get current subscription filter
# and add the new ids to the current

response = logs.put_subscription_filter(
    logGroupName = loggroupName,
    filterName = loggroupName + '-subscription',
    filterPattern = filterPattern,
    destinationArn = destarn#,
    #roleArn = createRole()
)


'''
assumeRolePolicy = {
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Principal": {"Service": "logs.ap-southeast-2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }
}

rolePolicy = {
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
         ],
         "Resource": "arn:aws:logs:*:*:*"
      },
      {
         "Effect": "Allow",
         "Action": [
            "lambda:InvokeFunction"
         ],
         "Resource": [
            "*"
         ]
      }
   ]
}
print(rolePolicy)

def createRole():
    rolename = 'cloudwatchlogs-subscriptionfilter-honeyrecord'
    try:
        response = iam.create_role(
            RoleName = rolename,
            AssumeRolePolicyDocument = json.dumps(assumeRolePolicy)
            # PermissionsBoundary='string',
        )
        arn = response['Role']['Arn']
    except iam.exceptions.EntityAlreadyExistsException:
        arn = iam.get_role(RoleName = rolename)['Role']['Arn']
    iam.put_role_policy(
        RoleName = rolename,
        PolicyName = 'cloudwatchlogs-subscriptionfilter-honeyrecord',
        PolicyDocument = json.dumps(rolePolicy)
    )
    return arn
'''




