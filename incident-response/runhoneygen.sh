#!/bin/bash
# This is an example of intended use. It will add the records to the patients table,
# and put a subscription filter on the patients get and patients delete lambdas

if [ $# -lt 2 ]
then
    echo "Usage: $0 numOfHoneyrecords stackname"
else
    NUM=$1
    STACKNAME=$2

    TABLENAME=$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patients.*AWS::DynamoDB::Table | cut -f4)
    DESTARN=$(aws lambda get-function --function-name $(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep blockuser.*AWS::Lambda::Function | cut -f4) |  grep -o 'arn:aws:lambda[a-zA-Z0-9:-]*')
    SRC1=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsget.*AWS::Lambda::Function | cut -f4))
    SRC2=$(echo /aws/lambda/$(aws cloudformation list-stack-resources --stack-name $STACKNAME | grep patientsdelete.*AWS::Lambda::Function | cut -f4))
    python honeyrecordgen.py $NUM $TABLENAME $DESTARN $SRC1 $SRC2
fi
