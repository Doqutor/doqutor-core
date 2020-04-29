#!/bin/bash
# This is an example of intended use. It will add the records to the patients table,
# and put a subscription filter on the patients get and patients delete lambdas
# Maybe just put this in the documentation, not as a standalone file
# I will convert this to python if necessary
# relies on output format text. Use --output text

if [ $# -lt 2 ]
then
    echo "Usage: $0 numOfHoneyrecords stackname"
else
    NUM=$1
    STACKNAME=$2

    RESOURCES=$(aws cloudformation list-stack-resources --output text --stack-name $STACKNAME)

    TABLENAME=$( echo "$RESOURCES" | grep patients.*AWS::DynamoDB::Table | cut -f4)
    DESTARN=$(aws lambda get-function --output text --function-name $( echo "$RESOURCES" | grep blockuser.*AWS::Lambda::Function | cut -f4) |  grep -o 'arn:aws:lambda[a-zA-Z0-9:-]*')
    SRC1=$(echo /aws/lambda/$( echo "$RESOURCES" | grep patientsget.*AWS::Lambda::Function | cut -f4))
    SRC2=$(echo /aws/lambda/$( echo "$RESOURCES" | grep patientsdelete.*AWS::Lambda::Function | cut -f4))
    python honeyrecordgen.py $NUM $TABLENAME $DESTARN $SRC1 $SRC2
fi
