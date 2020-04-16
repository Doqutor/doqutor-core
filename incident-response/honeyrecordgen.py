import os
import json
import boto3
import sys
import uuid
import random

dynamodb = boto3.resource('dynamodb')
dynamodbexceptions = boto3.client('dynamodb').exceptions
logs = boto3.client(logs)

n = int(sys.argv[1])
assert(n != 0)
tablename = sys.argv[2]
destarn = sys.argv[3]
table = dynamodb.Table(tablename)

ids = []

for i in range(n):
    item = generatePerson()
    try:
        data = table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
    except dynamodbexceptions.ConditionalCheckFailedException:
        i -= 1
        continue
    
    ids.append(item['id'])

# [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*5555*]
filterPattern = '[type=INFO, timestamp=*Z, requestid=*-*,'

filterPattern += ' event=*' + ids[0] + '*'
for i in range(1, len(ids)):
    filterPattern += ' || event=*' + id + '*'
filterPattern += ']'
print(filterPattern)

loggroupName = 'gettthis'
response = logs.put_subscription_filter(
    logGroupName = loggroupName,
    filterName = loggroupName + '-subscription',
    filterPattern = filterPattern,
    destinationArn = destarn,
    roleArn = createRole()
)

def generateName():
    return "Barry Fake"

def generateEmail(name):
    suffixes = ["gmail.com", "outlook.com", "bigpond.com.au" "live.com"]
    return name.replace(" ", "_") + "@" + random.choice(suffixes)

def generatePhoneNumber():
    return "+" + str(random.randint(10**10, (10**11)-1))

def generateAge():
    return random.randint(0, 120)

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

def createRole():
    return '0'