import os
import json
import boto3
import uuid

print("This script simulates an illegal read into a DynamoDB table caused by a faulty group policy")
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
    print("Verifying values...")
    os.system("aws dynamodb update-item --table-name "
                + table_name
                + " --key '{ \"id\": {\"S\": \""
                + patient_id
                + "\"} }'")
    print("The patient table is inaccessible to users in 'adminusers' IAM group.")
    insurance_id = str(uuid.uuid4())
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
else:
    print("Exiting...")