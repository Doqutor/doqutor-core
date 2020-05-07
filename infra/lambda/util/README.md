# Lambda functions

These lambda function will perform tasks required to respond to the incidents.

- cognito_postauth_trigger.py: used for "[Illegal write into Patient table](../../../incident-response#3-illegal-write-into-patient-table)" incident response.
- cloudtrail_restartlog.py : used for "[CloudTrail stopped by user](../../../incident-response#1-cloudtrail-stopped-by-user)" incident response.
- cloudtrail_retrigger_pipeline.py: used for "PENDING" incident response.
- [block_user.py](../api/block_user.py): used for "[Honeyrecord accessed by website user](../../../incident-response#2-honeyrecord-accessed-by-website-user)" incident response.

- cognito_postauth_trigger.py: Adds users created in Cognito to the DynamoDB databases of patients and doctors.
