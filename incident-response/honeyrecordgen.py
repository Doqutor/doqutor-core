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

def generateName() -> str:
    return fake.name()
    # return "Barry Fake"

def generateEmail(name: str) -> str:
    suffixes = ["gmail.com", "outlook.com", "bigpond.com.au", "live.com", "protonmail.com"]
    separators = ["_", ".", "", "-"]
    return name.replace(" ", random.choice(separators)) + "@" + random.choice(suffixes)

def generatePhoneNumber() -> str:
    return "+" + str(random.randint(10**10, (10**11)-1))

def generateAge() -> int:
    return random.randint(0, 100)

def generatePerson() -> dict:
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

#------------------------------------------------------------------------
def extractArgs(argv: list) -> (int, str, str, list):
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} numberOfHoneyTokens tablename subscriptionFilterdestinationArn subscriptionFilterLogGroupName subscriptionFilterLogGroupName2 ...")
        exit()

    n = int(sys.argv[1])
    if n < 1 or n > 21:
        print("n must be at least 1. Maximum n is 21 as filter patterns can only be up to 1024 bytes in length")
        exit()
    tablename = sys.argv[2]#.rstrip()
    destarn = sys.argv[3]#.rstrip()
    loggroupNames = sys.argv[4:]
    #print(tablename)
    #print(destarn)
    #print(loggroupName)
    return n, tablename, destarn, loggroupNames
    
#-----------------------------------------------------------------------------------------------
# Return True on error
def extractids(pattern: str) -> (list, bool):
    foundids = []
    next = pattern
    try:
        while next != [']']:
            id, rest = next.split('*',1)[1].split('*', 1)
            # will except if doesn't match
            foundids.append(id)
            next = rest.split('event=', 1) # *id* ...
            if len(next) == 2:
                next = next[1]
            # else, if eventstr = ']', then loop will end
            # if not, will continue to id, eventstr = line and raise exception
            # This seems awful code
    except:
        return foundids, True
    return foundids, False


def clearExistingPattern(curfilter: dict, _loggroupName: str):
    deleteSubscription = False
    print('You may quit running, or delete it and then rerun the program to create a new filter.')
    curpattern = curfilter['filterPattern']
    filterPatternStart = '[type=INFO,timestamp=*Z,requestid=*-*,event=*'
    print(curpattern)
    if curpattern.startswith(filterPatternStart):
        print('The filter pattern seems to match the known pattern. Delete it and its honey records? Y/N')
        if input().upper() == 'Y':
            idsstring = curpattern.split('[type=INFO,timestamp=*Z,requestid=*-*,event=', 1)[1]
            # extract ids from filter pattern
            foundids, err = extractids(idsstring)
            if err == True:
                print('Filter string diverged from pattern and the deletion process may not delete all existing honey records')
            print('The following ids were found in the current filter pattern.')
            for i in range(len(foundids)):
                print(str(i+1) + ': ' + foundids[i])
            print('Delete these database items and the current filter pattern? Y/N')
            if input().upper() == 'Y':
                deleteSubscription = True
                for id in foundids:
                    # delete id
                    response = table.delete_item(Key = {'id': id})
                    # print(response)
    else:
        print("The filter pattern is not compatible with this program's filter pattern structure and the program will not be able to perform any actions relating to its contents.\nDelete it anyway? Y/N")
        deleteSubscription = (input().upper() == 'Y')

    if deleteSubscription:
        response = logs.delete_subscription_filter(
            logGroupName = _loggroupName,
            filterName = curfilter['filterName']
        )
    # don't have to delete filter pattern, will just get overridden

# return True if there is an existing filter
def clearExistingFilters(_loggroupNames: list) -> bool:
    # check current filter pattern and delete if necessary
    existing = False
    for loggroupName in _loggroupNames:
        response = logs.describe_subscription_filters(
            logGroupName = loggroupName
        )
        #print(response)
        filters = response['subscriptionFilters']
        if filters == []:
            print(f'No existing pattern in {loggroupName}. Continuing...') # not print continuing from function
        else:
            print(f'Existing pattern in {loggroupName}.')
            clearExistingPattern(filters[0], loggroupName)
            existing = True
            print()
        # print(filters)
    return existing

#--------------------------------------------------------------------------------------------

# to database
# return True to indicate error
def addRecords(table, n: int) -> (list, bool):
    ids = []
    for i in range(n):
        item = generatePerson()
        try:
            data = table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
            if data['ResponseMetadata']['HTTPStatusCode'] != 200:
                print(data)
                return ids, True
            ids.append(item['id'])
        except dynamodbexceptions.ConditionalCheckFailedException:
            i -= 1
    return ids, False

def createPattern(ids: list) -> str:
    # [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*5555*]
    filterPattern = '[type=INFO,timestamp=*Z,requestid=*-*,'
    filterPattern += 'event=*' + ids[0] + '*'
    for i in range(1, len(ids)):
        filterPattern += '||event=*' + ids[i] + '*'
    filterPattern += ']'
    print(filterPattern)
    return filterPattern

def addSubscriptions(_loggroupNames: list, filterPattern: str, _destarn: str):
    for loggroupName in _loggroupNames:
        response = logs.put_subscription_filter(
            logGroupName = loggroupName,
            filterName = loggroupName + '-subscription',
            filterPattern = filterPattern,
            destinationArn = _destarn#,
            #roleArn = createRole()
        )

#----------------------------------------------------------------------------

dynamodb = boto3.resource('dynamodb')
dynamodbexceptions = boto3.client('dynamodb').exceptions
logs = boto3.client('logs')
iam = boto3.client('iam')

numRecords, tablename, destarn, loggroupNames = extractArgs(sys.argv)
table = dynamodb.Table(tablename)
existing = clearExistingFilters(loggroupNames)
if not existing:
    ids, err = addRecords(table, numRecords)
    if err is False:
        filterPattern = createPattern(ids)
        addSubscriptions(loggroupNames, filterPattern, destarn)
