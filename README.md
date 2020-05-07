
# [Doqutor-core](https://doqutor.github.io/doqutor-core/)
### Identification and simulation of automated security incident response using AWS serverless stack. 

- [Objective](#objective)
- [Architecture](#architecture)
- [Incident Response](#incident-response)
    1. [Attempted Vandalism](#1-attempted-vandalism)
    2. [Compromised AWS Account](#2-compromised-aws-account)
    3. [Data Exfiltration](#3-data-exfiltration)
    4. [Non-Patient Reading Patient Data](#4-non-patient-reading-patient-data)
    5. [Compromised CRM Account/Brute-force Attack](#5-compromised-crm-accountbrute-force-attack)
    6. [API Attack](#6-api-attack)
- [Features](#features)

### Objective
The main purpose of the project is to have responses ready for some defined threats which can be applied to any application to make our lives easier. The project aims to highlight common use cases in a web application based on AWS serverless infrastructure. We have used AWS CDK to deploy the complete [core project](./infra/). Use the [readme](./infra/README.md) to set up and deploy the AWS infrastructure.

### Architecture
![Architecture Diagram](https://github.com/Doqutor/doqutor-core/blob/master/images/arch.jpg?raw=true "Arch Diag")
We have utilized a completely serverless stack for this project. We are using DynamoDB as our database of choice. We are using AWS Lambda functions as the CRUD API’s and tied them to an API gateway which directs the request to the correct endpoint. We have also utilized an AWS WAF (Web Application Firewall) in front of the API gateway to protect it against some common web exploits that may affect availability, compromise security or consume excessive resources. We are using AWS Cognito for user authentication and authorization. For logging we utilize heavily on CloudWatch and CloudTrail. CloudWatch stores the logs for all the services used in AWS and cloudTrail saves all the events by AWS users.


### Incident Response
#### 1. Attempted Vandalism
A potential attack vector we noticed was that a bad actor could create or modify files in the S3 bucket. This could be from misconfigured authorization settings on the S3 bucket, or even an insider with S3 permissions that wishes to tamper with the bucket. We have decided that the only changes to the frontend considered legitimate must come from an execution of the entire CI/CD pipeline (in an ideal world the CI/CD pipeline will have many rounds of tests, and any modifications that bypass these safeguards could wreak havoc on the end-product).

To mitigate this potential attack vector, we have set up a watcher on the CloudTrail logs which detects changes to the S3 bucket. If the changes were enacted by the CI/CD pipeline (i.e. the " frontend-deployment" user with its own set of public and private keys), then the changes are ignored. If any other user makes the changes, then a lambda is triggered which reruns the CI/CD pipeline to create a fresh copy and deployment of the frontend to replace any of the unsolicited changes to the S3 bucket.


Reverts back the S3 bucket to the previous version.

Simulate this incident with the given [demo](./incident-response#1-illicit-modifications-to-the-frontend-s3-bucket).


![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/s3_IR.png?raw=true)

#### 2. Compromised AWS Account
CloudTrail is a very important service from AWS. This service enables AWS account to maintain and store logs throughout the AWS account. These logs can be analysed for governance, compliance, operational auditing, and risk auditing of your AWS account. It maintains action history logs of all actions performed through AWS Management Console, AWS SDKs, command line tools, and other AWS services. With support from CloudWatch, we can add rules on special cases and fire events based on CloudTrail event. 

Since it is very important for an AWS account to have logs, stopping the logs would prove to be a security risk for the AWS account. If the AWS CloudTrail is switched off, any user can update any setting and we would not have logs to have them accountable for it. Hence it is essential to keep CloudTrail running. Further, disabling logs is a common move for an attacker after infiltrating a system, so monitoring cloudtrail serves as an effective indicator of compromise.

When a trail is turned off by a user, we flag that user as malicious. It could have been the case that the access to the AWS account has been compromised of some user. For our use case, we detect the when the CloudTrail has been turned off. CloudTrail emits an event called, “StoppedLogging” we use this event to trigger response for the event. 

We respond the event by switching on the CloudTrail instance and blocking the user by attaching the policy of “deny-all”. We also emit important log information about events through simple notification service to the subscribed channels. For blocking the user, we use the lambda functions. Lambda function utilizes serverless code which can execute at an event and we do not need to run them an event detection process on a server. We use an instance of IAM from python AWS SDK, boto3 for attaching the policy to the user. We also send notifications to inform the subscribed channels about “StoppedLogging” and “StartLogging”. These notifications also contain the username of the arguable malicious AWS account user.

Simulate this incident with the given [demo](./incident-response#2-cloudtrail-stopped-by-user). Make sure to set up a dummy user.

![CloudTrail IR](https://github.com/Doqutor/doqutor-core/blob/master/images/cloudtrail.png?raw=true)

#### 3. Data Exfiltration
Data exfiltration is described as unauthorized copying or retrieval of sensitive data from a computer system. Organizations with high-value data are particularly at high risk of these types of attacks, whether they are from outside attackers or trusted insiders. Data exfiltration is among organizations’ top concerns today. According to research, more than 50% of security professionals responded that they have experienced a data breach at their current work or organization.


Thus, we came up with detecting access to honey tokens as an indicator of compromised or abused credentials, and of data exfiltration. Our implementation of a honey token, or honey record, is an item added to a database that does not represent any real-world entity. A genuine user (i.e. a doctor, receptionist) would only access patient records of patients they are working with, so patient records that are not assigned to any doctor should not be accessed. If they are accessed through the API, we take it to signal that a doctor’s website account, or their current authorization token, has been compromised. Perhaps an attacker is attempting to download certain attractive patient records, or many random patient records.

When this indicator is triggered, our response is to sign out and disable the website user, and then invalidate their current authorisation token. We also notify the administrators.


Simulate this incident with the given [demo](./incident-response#3-honeyrecord-accessed-by-website-user).


![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/honeytoken.png?raw=true)
#### 4. Non-Patient Reading/Writing Patient Data
In any application, one of the most important tasks is to maintain the security of the database. In this Medical CRM, we have created two tables – Doctors and Patients. In any medical facility, the administrators can be given the access of the Doctors information but is it secure to give them access of the Patient’s data like their prescriptions, medical history or in our case their insurance id.

To avoid such a situation, we have created a customer managed IAM policy known as “BlockPatientTable” which is applied to a group called “adminusers” who have “AdministratorAccess” policy attached to it. The policy is an entity which when applied to a resource or identity defines their permission. This policy is used to deny the complete access of the patient table by any member of the mentioned group. Our main objective here is to be ready for a situation where a user despite having the BlockPatientTable permission tries to access the table from outside the application.

In order to track the changes committed on the table, AWS provides us with DynamoDB Streams. When you enable a stream on a table, DynamoDB captures information about every modification to data items in the table. You can configure the stream so that the stream records capture additional information, such as the "before" and "after" images of modified items.

We have enabled a stream on our patients table which triggers a lambda function “cloudtrail_ddb_access” whenever there is a change in the table. The stream emits an event which is used by the lambda to check if the event is “Modify”. It compares the old value of the insurance id with the new one. If there are any changes, the lambda stores the old values of all fields and deletes the current entry from the table. The lambda then generates a new entry with the restored values. Since this event is not a Modify event, the lambda will not be triggered and hence the changes made by the user will not be reflected in the table. Along with this we also send a notification using AWS Simple Notification Service to the subscribed channel indicating that there has been a change made in the table. The notification contains the primary key, which is called id, on which the changes has been made.

Simulate this incident with the given [demo](./incident-response#4-illegal-write-into-patient-table).
![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/dynamo.png?raw=true)
#### 5. Compromised CRM Account/Brute-force Attack
This is routinely featured on the OWASP top-10 list as Broken Authentication. By breaking authentication, an adversary can compromise user accounts, as well as user data if an administrator’s credentials are found.

Our solution uses a Cognito user pool to handle all aspects of user management, from signing up new users, to multi factor authentication and password management. We used Cognito’s built-in features to perform the detection for us, mainly because it is already implemented but also because we didn’t have access to the internals API to retrieve metrics from Cognito.

When the user tries a password too many times, Cognito will start to rate limit their attempts and will also gradually increase the time which they can retry the password. Additionally if a user logs in from a new location, Cognito will also trigger a Multi Factor Authentication event, which will require the user to enter in a code from a text message. On top of this, we have configured a lambda function to send an email to the user on any suspicious login attempts.

Simulate this incident with the given [demo](./incident-response#5-brute-forcing-cognito).

![cognito](https://github.com/Doqutor/doqutor-core/blob/master/images/brute-force-login.png?raw=true)

#### 6. API Attack
Rate limiting is important to web applications as it prevents resources from being exhausted, as well as detecting and preventing data exfiltration. In the cloud where resources are easily auto scaled, another risk known as economic denial of sustainability can surface where a malicious attacker attempts to inflate the bill of a cloud customer by triggering the autoscaling capabilities within the customer’s apps. Other risks involve cross-site scripting and injection attacks, which could compromise the security and data of an application.

A Web Application Firewall (WAF) can be used to detect and prevent most of these attacks. With Amazon’s WAF, we set up a rule to limit requests to 128 every 5 minutes, which is plenty for a user at home to view and update their medical records. We also enabled other options such as XSS and an IP reputation list, to better secure our application against other attacks that we may have not thought about. 

Once the WAF detects more than our threshold of requests in a certain timeframe, it immediately starts to block access to the web application. In addition to this, a sample of the requests coming through the WAF is taken for further analysis for the developers to gain some insight from possible attacks. If the number of blocked requests from a source reaches a further 128 requests from the baseline of blocked requests, we will then notify the administrator about the problem.

Simulate this incident with the given [demo](./incident-response#6-rate-limiting).
![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/waf.png?raw=true)

### Features
- AWS [Lambda](./infra/lambda/api) functions as serverless REST API's.
- AWS [Lambda](./infra/lambda/util) functions for serverless automated incident response. 
- Seperated [stacks](./infra/lib) using [AWS CDK](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html) and [cloudformation](https://aws.amazon.com/cloudformation/).
- Custom [config](./infra/bin/infra.ts#L17) for deploying [multiple](./infra/bin/) stack names in the same account.

