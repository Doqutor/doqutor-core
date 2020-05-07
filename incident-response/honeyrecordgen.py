import os
import json
import boto3
import sys
import uuid
import random
from faker import Faker
fake = Faker()

# Arguments:
# numberOfHoneyTokens tablename subscriptionFilterdestinationArn sourceLogGroupName sourceLogGroupName2 ...
# tablename: name of patients table. 
#           Example: jm-c51d2d-infrastructure-patientsE885E6D7-7THM1LUCBR93   
#           Retrieval: printed out in cdk deploy outputs, or available from CloudFormation, through console or cli
# destination: arn of block_user lambda. 
#           Example: arn:aws:lambda:ap-southeast-2:acctNumber:function:jm-c51d2d-infrastructure-blockuser2A1530289-3T5FMKMM5GX5
#           Retrieval: CloudFormation, with console or cli
# sourceLogGroup: name of log group that is source for subscription filter.
#           Example: /aws/lambda/jm-c51d2d-infrastructure-patientsget88C45C74-1SQ0SB66ERZKW
#           can be retrieved from Cloudwatch, with console or cli, or inferred from lambda's physical id
# The log group must exist before a subscription filter is added, meaning that the source lambdas must be invoked at least once and perform some logging


dynamodb = boto3.resource('dynamodb')
dynamodbexceptions = boto3.client('dynamodb').exceptions
logs = boto3.client('logs')
iam = boto3.client('iam')


def generateName() -> str:
    return fake.name()

def generateEmail(name: str) -> str:
    suffixes = ["gmail.com", "outlook.com", "bigpond.com.au", "live.com", "protonmail.com"] # for generating honey people
    separators = ["_", ".", "", "-"]
    return name.replace(" ", random.choice(separators)) + "@" + random.choice(suffixes)

def generatePhoneNumber() -> str:
    return "+" + str(random.randint(10**10, (10**11)-1))

def generateAge() -> int:
    return random.randint(0, 100)

def generateInsuranceid() -> str:
    return str(random.randint(10**5, (10**7)-1))

def generatePerson(name: str = None) -> dict:
    if name is None:
        name = generateName()
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': generateEmail(name),
        'phone_number': generatePhoneNumber(),
        'age': generateAge(),
        'is_active': True,
        'insurance_id': generateInsuranceid()
        # should is_active be false?
    }

#------------------------------------------------------------------------
# maybe return (bool, (int, str, str, list))?
def extractArgs(argv: list) -> (int, str, str, list):
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} numberOfHoneyTokens tablename subscriptionFilterdestinationArn sourceLogGroupName sourceLogGroupName2 ...")
        exit()

    n = int(sys.argv[1])
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


def clearExistingPattern(curfilter: dict, loggroupName: str, table):
    deleteSubscription = False
    print('You may quit running, or delete it and then rerun the program to create a new filter.')
    curpattern = curfilter['filterPattern']
    filterPatternStart = '[type=INFO,timestamp=*Z,requestid=*-*,event=*'
    print(curpattern)
    if curpattern.startswith(filterPatternStart):
        if input('The filter pattern seems to match the known pattern. Check it for honeyrecords to delete? Y/N ').upper() == 'Y':
            idsstring = curpattern.split('[type=INFO,timestamp=*Z,requestid=*-*,event=', 1)[1]
            # extract ids from filter pattern
            foundids, err = extractids(idsstring)
            if err == True:
                print('Filter string diverged from pattern and the deletion process may not delete all existing honey records')
            print('The following ids were found in the current filter pattern.')
            for i in range(len(foundids)):
                print(str(i+1) + ': ' + foundids[i])
            if input('Delete these database items and the current filter pattern? Y/N ').upper() == 'Y':
                deleteSubscription = True
                for id in foundids:
                    # delete id
                    response = table.delete_item(Key = {'id': id})
                    # print(response)
    else:
        prompt = "The filter pattern is not compatible with this program's filter pattern structure and the program will not be able to perform any actions relating to its contents.\nDelete it anyway? Y/N "
        deleteSubscription = (input(prompt).upper() == 'Y')

    if deleteSubscription:
        response = logs.delete_subscription_filter(
            logGroupName = loggroupName,
            filterName = curfilter['filterName']
        )
    # don't *have* to delete filter pattern, will just get overridden

# return True if there is an existing filter
def clearExistingFilters(loggroupNames: list, table) -> bool:
    # check current filter pattern and delete if necessary
    existing = False
    for loggroupName in loggroupNames:
        response = logs.describe_subscription_filters(
            logGroupName = loggroupName
        )
        #print(response)
        filters = response['subscriptionFilters']
        if filters == []:
            print(f'No existing pattern in {loggroupName}. Continuing...') # not print continuing from function
        else:
            print(f'Existing pattern in {loggroupName}.')
            clearExistingPattern(filters[0], loggroupName, table)
            existing = True
            print()
        # print(filters)
    return existing

#--------------------------------------------------------------------------------------------

# Generate and add records to database
# return idlist, error. True to indicate error, false to indicate success.
def addRecords(table, n: int) -> (list, bool):
    ids = []
    
    # maybe ask if would like to provide particular names, comma separated?
    names = input(f'To add specific names, enter them comma separated here. The first {n} names will be used. If you enter less than {n} names, the rest will be auto-generated. Whitespace will be stripped. Or press enter to skip.\n').split(',')
    if names == ['']:
        names = []
    for _ in range(n-len(names)):
        names.append(generateName())

    print()
    print('Added records:')
    for name in names[:n]:
        item = generatePerson(name)
        try:
            data = table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
            if data['ResponseMetadata']['HTTPStatusCode'] != 200:
                print(data)
                return ids, True
            ids.append(item['id'])
            print(item)
        except dynamodbexceptions.ConditionalCheckFailedException:
            i -= 1
    # print(names)
    print()
    return ids, False

def createPattern(ids: list) -> str:
    # [type=INFO, timestamp=*Z, requestid=*-*, event=*fc409bbc-ed87-4394-b94e-eb6954311bbb* || event=*5555*]
    filterPattern = '[type=INFO,timestamp=*Z,requestid=*-*,'
    filterPattern += 'event=*' + ids[0] + '*'
    for i in range(1, len(ids)):
        filterPattern += '||event=*' + ids[i] + '*'
    filterPattern += ']'
    return filterPattern

def addSubscriptions(loggroupNames: list, filterPattern: str, destarn: str):
    #print(destarn)
    for loggroupName in loggroupNames:
        response = logs.put_subscription_filter(
            logGroupName = loggroupName,
            filterName = loggroupName + '-subscription',
            filterPattern = filterPattern,
            destinationArn = destarn#,
        )

#----------------------------------------------------------------------------

def generate(numRecords: str, tablename: str, destarn: str, loggroupNames: list):
    if numRecords < 1 or numRecords > 21:
        print("n must be at least 1. Maximum n is 21 as filter patterns can only be up to 1024 bytes in length")
    else:
        table = dynamodb.Table(tablename)
        existing = clearExistingFilters(loggroupNames, table)
        if not existing:
            ids, err = addRecords(table, numRecords)
            if err is False:
                filterPattern = createPattern(ids)
                addSubscriptions(loggroupNames, filterPattern, destarn)
                print('Filter pattern:')
                print(filterPattern)


if __name__ == "__main__":
    #numRecords, tablename, destarn, loggroupNames = extractArgs(sys.argv)
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} numberOfHoneyTokens tablename subscriptionFilterdestinationArn sourceLogGroupName sourceLogGroupName2 ...")
    else:
        numRecords = int(sys.argv[1])
        if numRecords < 1 or numRecords > 21:
            print("n must be at least 1. Maximum n is 21 as filter patterns can only be up to 1024 bytes in length")
        else:
            tablename = sys.argv[2]#.rstrip()
            destarn = sys.argv[3]#.rstrip()
            loggroupNames = sys.argv[4:]
            #print(tablename)
            #print(destarn)
            #print(loggroupName)
            generate(numRecords, tablename, destarn, loggroupNames)
