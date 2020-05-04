
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

Simulate this incident with the given [demo](https://github.com/Doqutor/doqutor-core/tree/master/incident-response#1-cloudtrail-stopped-by-user). Make sure to [set up a dummy user](https://github.com/Doqutor/doqutor-core/tree/master/incident-response#0-set-up-dummy-user).

![CloudTrail IR](https://github.com/Doqutor/doqutor-core/blob/master/images/cloudtrail.png)

#### 3. Data Exfiltration
Data exfiltration is described as unauthorized copying, or retrieval of sensitive data from a computer system. Organizations with high-value data are particularly at high risk of these types of attacks, whether they are from outside attackers or trusted insiders. Data exfiltration is among organizations’ top concerns today. Data breaches can be very damaging to an organisation’s reputation, share price and profitability, and socially-focused organisations will also be concerned about the personal impact on their clients. According to a research, more than 50% of security professionals responded that they have experienced a data breach at their current work or organization.
Our implementation of a honey token, or honey record, is an item added to a database that does not represent any real-world entity. A genuine user (i.e. a doctor, receptionist) would only access patient records of patients they are working with, so patient records that are not assigned to any doctor should not be accessed. If they are accessed through the API, we take it to signal that a doctor’s website account, or their current authorization token, has been compromised. Perhaps an attacker is attempting to download certain attractive patient records, or many random patient records.
We came up with detecting access to honey tokens as an indicator of compromised or abused credentials, and of data exfiltration. When this indicator is triggered, our response is to sign out and disable the website user, and then invalidate their current authorisation token. We also notify the administrators.
Simulate this incident with the given [Demo](https://github.com/Doqutor/doqutor-core/tree/master/incident-response#2-honeyrecord-accessed-by-website-user).


![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/honeytoken.png)
#### 4. Non-Patient Reading Patient Data


![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/dynamo.png)
#### 5. Compromised CRM Account/Brute-force Attack


#### 6. API Attack
