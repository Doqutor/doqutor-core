import os
import json
import boto3
import sys
import uuid
import random
from faker import Faker
fake = Faker()

# problem: filter pattern can only fit 21 uuids 
# and a log group can only have one subscription filter
# so maximum of 21 honey records in entire database

def generateName():
    return fake.name()
    # return "Barry Fake"

def generateEmail(name: str):
    suffixes = ["gmail.com", "outlook.com", "bigpond.com.au", "live.com", "protonmail.com"]
    separators = ["_", ".", "", "-"]
    return name.replace(" ", random.choice(separators)) + "@" + random.choice(suffixes)

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
        # should is_active be false?
    }

#  return value is pointless rn
def clearExistingPattern(curfilter: dict, _loggroupName: str):
    print('You may quit running, or delete it and then rerun the program to create a new filter.')
    curpattern = curfilter['filterPattern']
    filterPatternStart = '[type=INFO,timestamp=*Z,requestid=*-*,event=*'
    print(curpattern)
    if curpattern.startswith(filterPatternStart):
        print('The filter pattern seems to match the known pattern. Delete it and its honey records? Y/N')
        if input().upper() != 'Y':
            return False
        next = curpattern.split('[type=INFO,timestamp=*Z,requestid=*-*,event=', 1)[1]
        # check split
        # extract ids from filter pattern and delete from database
        foundids = []
        try:
            while next != [']']:
                id, eventstr = next.split('*',1)[1].split('*', 1)
                # will except if doesn't match?
                foundids.append(id)
                next = eventstr.split('event=', 1) # *id* ...
                if len(next) == 2:
                    next = next[1]
                # else, if eventstr = ']', then loop will end
                # if not, will continue to id, eventstr = line and raise exception
                # This is really awful code
        except:
            print('Filter string diverged from pattern and the deletion process may not delete all existing honey records')
        # print found ids
        print('The following ids were found in the current filter pattern.')
        for i in range(len(foundids)):
            print(str(i+1) + ': ' + foundids[i])
        print('Delete these database items and the current filter pattern? Y/N')
        if input().upper() != 'Y':
            return False
        for id in foundids:
            # delete id
            response = table.delete_item(Key = {'id': id})
            # print(response)
    else:
        print("The filter pattern is not compatible with this program's filter pattern structure and the program will not be able to perform any actions relating to its contents.\n Delete it? Delete it anyway? Y/N")
        if input().upper() != 'Y':
            return False
    response = logs.delete_subscription_filter(
        logGroupName = _loggroupName,
        filterName = curfilter['filterName']
    )
    return True
    # don't have to delete filter pattern, will just get overridden


dynamodb = boto3.resource('dynamodb')
dynamodbexceptions = boto3.client('dynamodb').exceptions
logs = boto3.client('logs')
iam = boto3.client('iam')

# extract arguments
if len(sys.argv) < 5:
    print(f"Usage: {sys.argv[0]} numberOfHoneyTokens tablename subscriptionFilterdestinationArn subscriptionFilterLogGroupName subscriptionFilterLogGroupName2 ...")
    exit()

n = int(sys.argv[1])
assert(n != 0)
if n > 21:
    print("Maximum n is 21 as filter patterns can only be up to 1024 bytes in length")
    exit()
tablename = sys.argv[2]#.rstrip()
destarn = sys.argv[3]#.rstrip()
loggroupNames = sys.argv[4:]
# loggroupName = sys.argv[4]#.rstrip()
table = dynamodb.Table(tablename)
#print(tablename)
#print(destarn)
#print(loggroupName)

# check current filter
existing = False
for loggroupName in loggroupNames:
    response = logs.describe_subscription_filters(
        logGroupName = loggroupName
    )
    #print(response)
    filters = response['subscriptionFilters']
    if filters == []:
        print(f'No existing pattern in {loggroupName}. Continuing...')
    else:
        print(f'Existing pattern in {loggroupName}.')
        res = clearExistingPattern(filters[0], loggroupName)
        existing = True
        print()
    # print(filters)
    # check current filter pattern and delete if necessary
if existing:
    exit()

# add records to database and make new filter
filterPattern = '[type=INFO,timestamp=*Z,requestid=*-*,'

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

filterPattern += 'event=*' + ids[0] + '*'
for i in range(1, len(ids)):
    filterPattern += '||event=*' + ids[i] + '*'
filterPattern += ']'
print(filterPattern)

for loggroupName in loggroupNames:
    response = logs.put_subscription_filter(
        logGroupName = loggroupName,
        filterName = loggroupName + '-subscription',
        filterPattern = filterPattern,
        destinationArn = destarn#,
        #roleArn = createRole()
    )


# atm running this will overwrite existing subscription filter (can only have one per log group)
# so previous honey records will still exist in the table but will not trigger the filter
# should use describe_subscription_filters() to get current subscription filter
# and add the new ids to the current

'''
ogfilter = filters[0]
ogfilterpattern = ogfilter['filterPattern']
if ogfilterpattern.startswith(filterPatternStart):
# ofc it still might be incompatible
    filterPattern = ogfilterpattern[:-1] + '||' #.rstrip("]")
    filterName = ogfilter['filterName']
else:
    print("Filter pattern of existing subscription filter is incompatible with this one.\nYou must delete the previous subscription filter.")
    exit()
'''


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




