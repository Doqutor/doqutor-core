#!/bin/bash
# make some adjustment to this. 
# The user pool id is an output from cdk deploy, so probably don't need to get it from stackname
# I will convert this to python if necesssary
# maybe can use cognito initiate-auth to sign in and get token? or some kind of request
# initiate-auth: can't get to work. request: too complicated to copy request made by browser
# maybe can at least generate signin link
# make this a gettoken script
# that creates user, provides signin link, and takes redirect url and provides token
# or maybe should just simulate using website..


USERPOOLID=$1
EMAIL=$2
INC=$3
ARGS=$4
aws cognito-idp admin-create-user $ARGS --user-pool-id $USERPOOLID \
--username justin$INC \
--user-attributes Name=email,Value=$EMAIL Name=phone_number,Value="+1212555123" Name=custom:type,Value=doctor Name=email_verified,Value=True Name=phone_number_verified,Value=True \
--temporary-password passwordH5%
