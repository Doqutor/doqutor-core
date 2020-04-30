import sys
import boto3
import getpass
from botocore.exceptions import ParamValidationError
from typing import Callable


cognito = boto3.client('cognito-idp')
cloudformation = boto3.client('cloudformation')

# returns physical id for first stack resource for which compareFn(resource) returns true
def searchStackResources(stackResources: dict, stackName: str, compareFn: Callable[[dict], bool]) -> str:
    for item in stackResources['StackResourceSummaries']:
        #print(item['LogicalResourceId'], item['ResourceType'])
        if compareFn(item):
            return item['PhysicalResourceId']
    
    nextToken = stackResources.get('NextToken', None)
    while nextToken != None:
        stackResources = cloudformation.list_stack_resources(
            StackName = stackName,
            NextToken = nextToken
        )
        for item in stackResources['StackResourceSummaries']:
            if compareFn(item):
                return item['PhysicalResourceId']
        nextToken = stackResources.get('nextToken', None)
    return None

# return url, err
def getURL(stackResources: dict, stackName: str, userpoolid: str) -> (str, str):
    response = cognito.describe_user_pool(
        UserPoolId = userpoolid
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        # do something
        return None, 'describe user pool failed'

    domain = response['UserPool']['Domain']
    regionname = boto3.session.Session().region_name
    compareFn = lambda item: item['LogicalResourceId'].startswith('appclient') and item['ResourceType'] == 'AWS::Cognito::UserPoolClient'
    clientid = searchStackResources(stackResources, stackName, compareFn)
    url = 'https://' + domain + '.auth.' + regionname + '.amazoncognito.com' + '/login' + '?' + 'client_id=' + clientid + '&response_type=token&scope=doqutore/application&redirect_uri=http://localhost'
    return url, None

def extractToken(url: str) -> str:
    return "Bearer " + url.split("access_token=", 1)[1].split("&")[0]

# Return None on success
def addUser(userpoolid: str, username: str, password: str) -> str:
    try:
        response = cognito.admin_create_user(
            UserPoolId = userpoolid,
            Username = username,
            UserAttributes=[
                {
                    'Name': 'phone_number',
                    'Value': '+1212555123'
                },
                {
                    'Name': 'email',
                    'Value': 'testuser@jdjfjid.testuser'
                },
                {
                    'Name': 'custom:type',
                    'Value': 'doctor'
                },
                {
                    'Name': 'email_verified',
                    'Value': 'True'
                },
                {
                    'Name': 'phone_number_verified',
                    'Value': 'True'
                }
            ],
            TemporaryPassword = password,
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            # do something
            return 'add user failed'
        else:
            response = cognito.admin_set_user_password(
                UserPoolId = userpoolid,
                Username = username,
                Password = password,
                Permanent = True
            )
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                # do something
                return 'Set password failed'
    #exceptions = [cognito.exceptions.error]
    except ParamValidationError as err:
        return err
    except cognito.exceptions.UsernameExistsException as err:
        return err
    except cognito.exceptions.InvalidPasswordException as err:
        return err
    except cognito.exceptions.InvalidParameterException as err:
        return err
    # there must be another way to catch a series of exceptions
    # can't capture cognito.exceptions.* in variable name
    return None

def getUserPoolid(stackResources: dict, stackName: str) -> str:
    compareFn = lambda item: item['LogicalResourceId'].startswith('crmusers') and item['ResourceType'] == 'AWS::Cognito::UserPool'
    userpoolid = searchStackResources(stackResources, stackName, compareFn)
    return userpoolid
    # logical id crmusers44BE6CEC	
    # type AWS::Cognito::UserPool

# Return resourcelist, err
def getStackResources(stackname: str) -> (dict, str):
    response: dict = cloudformation.list_stack_resources(
        StackName = stackname
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        # do something
        responsemetadata = response['ResponseMetadata']
        #return None, f'List stack resources failed: {response['ResponseMetadata']}' # why is this invalid syntax
        return None, f'List stack resources failed: {responsemetadata}'
    return response, None

def getToken(stackname: str) -> str:
    stackResources, err = getStackResources(stackname)
    if err != None:
        print(err)
        return None
    userpoolid = getUserPoolid(stackResources, stackname)
    print(f'Userpoolid: {userpoolid}')
    newUserChoice = input('Create a new cognito user (Y) or use an existing user (N): ')
    if newUserChoice.upper() == 'Y':
        username = input('Username: ')
        password = getpass.getpass('Password: ')
        print('Creating new user...')
        err = addUser(userpoolid, username, password)
        if err != None:
            print(err)
            return None

    url, err = getURL(stackResources, stackname, userpoolid)
    if err != None:
        print(err)
        return None
    print(f'Log in at this url and paste the redirect link here.\n{url}\n')
    redirectlink = input()
    token = extractToken(redirectlink)
    return token

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} stackname')
    else:
        token = getToken(sys.argv[1])
        if token != None:
            print()
            print('Token:')
            print(token)
            # need some way to make this easier to extract since can't use < or $() because there is other output
