#!/bin/sh

PHONE_NUMBER="+61400000000"
USER_POOL="ap-southeast-2_GGovEEu2d"
USERNAME="testuser"
EMAIL="sysadmin@prod.aws9447.me"
ACC_TYPE="doctor"

aws cognito-idp admin-create-user --user-pool-id "$USER_POOL"  --username "$USERNAME" \
	--user-attributes "Name=email,Value=$EMAIL" Name=email_verified,Value=true \
	"Name=phone_number,Value=$PHONE_NUMBER" Name=phone_number_verified,Value=true \
    Name=given_name,Value='Dr Test' Name=family_name,Value='Aws' "Name=custom:type,Value=$ACC_TYPE"
