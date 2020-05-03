# This is an example of intended use. It will add the records to the patients table,
# and put a subscription filter on the patients get and patients delete lambdas
# Maybe just put this in the documentation, not as a standalone file
# I will convert this to python if necessary

import sys
import boto3
import re

from honeyrecordgen import generate
from gettoken import searchStackResources, getStackResources
# obv importing this from gettoken doesn't make much sense but its not really worth making a separate file

cloudformation = boto3.client('cloudformation')
lambdaboto = boto3.client('lambda')

# probably should have just used aws cli from within python and converted bash directly

# TABLENAME=$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patients.*AWS::DynamoDB::Table | cut -f4)
def getTablename(stackResources: dict, stackname: str, tablenamestart: str) -> str:
    # need physical id from listResources
    compareFn = lambda item: item['LogicalResourceId'].startswith(tablenamestart) and item['ResourceType'] == 'AWS::DynamoDB::Table'
    tablename = searchStackResources(stackResources, stackname, compareFn)
    return tablename

# DESTARN=$(aws lambda get-function --function-name $(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep blockuser.*AWS::Lambda::Function | cut -f4) |  grep -o 'arn:aws:lambda[a-zA-Z0-9:-]*')
def getLambdaArn(stackResources: dict, stackname: str, lambdanamestart: str) -> str:
    compareFn = lambda item: item['LogicalResourceId'].startswith(lambdanamestart) and item['ResourceType'] == 'AWS::Lambda::Function'
    lambdaname = searchStackResources(stackResources, stackname, compareFn)
    response = lambdaboto.get_function(
        FunctionName = lambdaname
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        responsemetadata = response['ResponseMetadata']
        print(f'lambda.get_function failed: {responsemetadata}')
        arn = None
    else:
        arn = response['Configuration']['FunctionArn']
    return arn

# SRC1=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsget.*AWS::Lambda::Function | cut -f4))
# SRC2=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsdelete.*AWS::Lambda::Function | cut -f4))
# Probably better to actually get it using lambda get-function
# that doesn't seem possible
# I can't find anyway to get the name of the log group other than already the start of it
def getLogGroupName(stackResources: dict, lambdanamestart: str) -> str:
    compareFn = lambda item: item['LogicalResourceId'].startswith(lambdanamestart) and item['ResourceType'] == 'AWS::Lambda::Function'
    lambdaname = searchStackResources(stackResources, stackname, compareFn)
    #print(stackResources)
    loggroupname = "/aws/lambda/" + lambdaname
    return loggroupname

def rungen(numOfHoneyrecords: int, stackname: str):
    stackResources, err = getStackResources(stackname)
    if err != None:
        print(err)
    else:
        tablename = getTablename(stackResources, stackname, "patients")
        destinationarn = getLambdaArn(stackResources, stackname, "blockuser")
        src1 = getLogGroupName(stackResources, "patientsget")
        src2 = getLogGroupName(stackResources, "patientsdelete")

        generate(num, tablename, destinationarn, [src1, src2])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} numOfHoneyrecords stackname")
    else:
        num = int(sys.argv[1])
        stackname = sys.argv[2]
        rungen(num, stackname)



# Bash:
# TABLENAME=$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patients.*AWS::DynamoDB::Table | cut -f4)
# DESTARN=$(aws lambda get-function --function-name $(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep blockuser.*AWS::Lambda::Function | cut -f4) |  grep -o 'arn:aws:lambda[a-zA-Z0-9:-]*')
# SRC1=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsget.*AWS::Lambda::Function | cut -f4))
# SRC2=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsdelete.*AWS::Lambda::Function | cut -f4))
# python honeyrecordgen.py $NUM $TABLENAME $DESTARN $SRC1 $SRC2