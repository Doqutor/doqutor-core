import os
import json
import boto3
import uuid

print("PLEASE CONFIGURE A TEST USER WITH setup_user.py")
print("This script simulates an illegal write into a DynamoDB table caused by a faulty group policy")
print("Incident: Admin user attempts to write into patient table")
print("Response: Updated record rollbacks and an email is sent to admin groups' email")
print("\nPlease ensure your AWS CLI config is in json format")

print("\nPress y/n to proceed:")
decision = input()
if decision == 'y' or decision == 'Y':
    print("\nInput the patient table name in your account:")
    table_name = input()
    print("Input the id of the patient record:")
    patient_id = input()
    print("Verifying values... (Please take note of the value of insurance_id at this point)")
    os.system("aws dynamodb get-item --table-name "
                + table_name
                + " --key '{ \"id\": {\"S\": \""
                + patient_id
                + "\"} }'")
    print("The patient table is inaccessible to users in 'adminusers' IAM group.")
    print("However for demo purposes, the generated user will have read access")
    print("Continue on? (y/n)")
    user_input = input()
    if user_input == 'y' or user_input == 'Y':
        print("Input a malicious insurance id for the patient record:")
        insurance_id = input()
        print("\nAttempting to write new random ("+insurance_id+") insurance_id for patient id: " + patient_id)
        os.system("aws dynamodb update-item --table-name "
                    + table_name
                    + " --key '{ \"id\": {\"S\": \""
                    + patient_id
                    + "\"} }'"
                    + " --update-expression 'SET insurance_id = :q' "
                    + "--expression-attribute-values '{ \":q\": {\"S\": \""
                    + insurance_id
                    + "\"} }' "
                    + "--return-values ALL_NEW")
        print("Continue on? (y/n)")
        user_input = input()
        if user_input == 'y' or user_input == 'Y':
            print("Check if rollback occurred...")
            os.system("aws dynamodb get-item --table-name "
                        + table_name
                        + " --key '{ \"id\": {\"S\": \""
                        + patient_id
                        + "\"} }'")
else:
    print("Exiting...")