#!/bin/bash
# make some adjustment to this. 
# The user pool id is an output from cdk deploy, so probably don't need to get it from stackname
# I will convert this to python

USERPOOLID=$1
EMAIL=$2
INC=$3
ARGS=$4
aws cognito-idp admin-create-user $ARGS --user-pool-id $USERPOOLID \
--username justin$INC \
--user-attributes Name=email,Value=$EMAIL Name=phone_number,Value="+1212555123" Name=custom:type,Value=doctor Name=email_verified,Value=True Name=phone_number_verified,Value=True \
--temporary-password passwordH5%
