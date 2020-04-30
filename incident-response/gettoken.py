import sys
import boto3
import getpass
from botocore.exceptions import ParamValidationError


cognito = boto3.client('cognito-idp')
cloudformation = boto3.client('cloudformation')

def getURL(stackname: str) -> str:
    # build URL from stackname using cloudformation and cognito
    # cognito.describe_user_pool()
    #TODO
    return "https://login-doqutore-infrastructure-prod.auth.ap-southeast-2.amazoncognito.com/login?client_id=1l26brptvhg0hhricpnno0h45d&response_type=token&scope=doqutore/application&redirect_uri=http://localhost"

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
                    'Value': 'a@aksdlfj.ajsi'
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
    # there must be another way to catch a series of exceptions
    # can't capture cognito.exceptions.* in variable name
    return None

def getUserPoolid(stackname: str) -> str:
    response: dict = cloudformation.list_stack_resources(
        StackName = stackname
    )
    for item in response['StackResourceSummaries']:
        if item['LogicalResourceId'].startswith('crmusers') and item['ResourceType'] == 'AWS::Cognito::UserPool':
            return item['PhysicalResourceId']
    '''for key in response:
        if key == 'NextToken':
            nextToken = response[key]'''
    nextToken = response.get('nextToken', None)
            
    while nextToken != None: #response['NextToken'] != None:
        response = cloudformation.list_stack_resources(
            StackName = stackname,
            NextToken = nextToken
        )
        for item in response['StackResourceSummaries']:
            if item['LogicalResourceId'].startswith('crmusers') and item['ResourceType'] == 'AWS::Cognito::Userpool':
                return item['PhysicalResourceId']
        nextToken = response.get('nextToken', None)
    # logical id crmusers44BE6CEC	
    # type AWS::Cognito::UserPool
    return None

def getToken(stackname: str) -> str:
    newUserChoice = input('Create a new cognito user (Y) or use an existing user (N): ')
    if newUserChoice.upper() == 'Y':
        username = input('Username: ')
        password = getpass.getpass('Password: ')
        print('Creating new user...')
        userpoolid = getUserPoolid(stackname)
        print(f'Userpoolid: {userpoolid}')
        err = addUser(userpoolid, username, password)
        if err != None:
            print(err)
            return None

    url = getURL(stackname)
    print(f'Log in at this url and paste the redirect link here.\n{url}')
    print()
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
