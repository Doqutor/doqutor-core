
# Doqutore
### Indentification and simulation of automated security incident response using AWS serverless stack. 

- [Objective](#objective)
- [Architecture](#architecture)
- [Features](#features)
- [Incident Response](#incident-response)
    1. [Attempted Vandalism](#1-attempted-vandalism)
    2. [Compromised AWS Account](#2-compromised-aws-account)
    3. [Data Exfiltration](#3-data-exfiltration)
    4. [Non-Patient Reading Patient Data](#4-non-patient-reading-patient-data)
    5. [Compromised CRM Account/Brute-force Attack](#5-compromised-crm-accountbrute-force-attack)
    6. [API Attack](#6-api-attack)


### Objective
The project aims to highlight common use cases in an web application based on AWS serverless infrastructure. We have used AWS CDK to deploy the complete [core project](https://github.com/Doqutor/doqutor-core/tree/master/infra). Use the [readme](https://github.com/Doqutor/doqutor-core/blob/master/infra/README.md) to set up and deploy the AWS infrastructure.

### Architecture
![Architecture Diagram](https://github.com/Doqutor/doqutor-core/blob/master/images/arch.jpg)

### Features
- AWS [Lambda](https://github.com/Doqutor/doqutor-core/tree/master/infra/lambda/api) functions as rest API's

### Incident Response
#### 1. Attempted Vandalism
Extraneous file added to S3 bucket : A potential attack vector we noticed was that a bad actor could create or modify files in the S3 bucket. This could be from misconfigured authorization settings on the S3 bucket, or even an insider with S3 permissions that wishes to tamper with the bucket. We have decided that the only changes to the frontend considered legitimate must come from an execution of the entire CI/CD pipeline (in an ideal world the CI/CD pipeline will have many rounds of tests, and any modifications that bypass these safeguards could wreak havoc on the end-product).

To mitigate this potential attack vector, we have set up a watcher on the CloudTrail logs which detects changes to the S3 bucket. If the changes were enacted by the CI/CD pipeline (i.e. the " frontend-deployment" user with its own set of public and private keys), then the changes are ignored. If any other user makes the changes, then a lambda is triggered which reruns the CI/CD pipeline to create a fresh copy and deployment of the frontend to replace any of the unsolicited changes to the S3 bucket.

![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/s3_IR.png)

#### 2. Compromised AWS Account
CloudTrail is a very important service from AWS. This service enables AWS account to maintain and store logs throughout the AWS account. These logs can be analysed for governance, compliance, operational auditing, and risk auditing of your AWS account. It maintains action history logs of all actions performed through AWS Management Console, AWS SDKs, command line tools, and other AWS services. With support from CloudWatch, we can add rules on special cases and fire events based on CloudTrail event. 

Since it is very important for an AWS account to have logs, stopping the logs would prove to be a security risk for the AWS account. If the AWS CloudTrail is switched off, any user can update any setting and we would not have logs to have them accountable for it. Hence it is essential to keep CloudTrail running. Further, disabling logs is a common move for an attacker after infiltrating a system, so monitoring cloudtrail serves as an effective indicator of compromise.

When a trail is turned off by a user, we flag that user as malicious. It could have been the case that the access to the AWS account has been compromised of some user. For our use case, we detect the when the CloudTrail has been turned off. CloudTrail emits an event called, “StoppedLogging” we use this event to trigger response for the event. 

We respond the event by switching on the CloudTrail instance and blocking the user by attaching the policy of “deny-all”. We also emit important log information about events through simple notification service to the subscribed channels. For blocking the user, we use the lambda functions. Lambda function utilizes serverless code which can execute at an event and we do not need to run them an event detection process on a server. We use an instance of IAM from python AWS SDK, boto3 for attaching the policy to the user. We also send notifications to inform the subscribed channels about “StoppedLogging” and “StartLogging”. These notifications also contain the username of the arguable malicious AWS account user.

#### 3. Data Exfiltration
#### 4. Non-Patient Reading Patient Data
#### 5. Compromised CRM Account/Brute-force Attack
#### 6. API Attack
