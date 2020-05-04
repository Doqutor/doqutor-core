
# Doqutore
### Indentification and simulation of automated security incident response using AWS serverless stack. 

- [Objective](#objective)
- [Architecture](#architecture)
- [Features](#features)
- [Incident Response](#incident-response)
    - [Attempted Vandalism](#1-attempted-vandalism)
    - [Compromised AWS Account](#1-attempted-vandalism)
    - [Data Exfiltration](#1-attempted-vandalism)
    - [Non-Patient Reading Patient Data](#1-attempted-vandalism)
    - [Compromised CRM Account/Brute-force Attack](#1-attempted-vandalism)
    - [API Attack](#1-attempted-vandalism)


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
#### 3. Data Exfiltration
#### 4. Non-Patient Reading Patient Data
#### 5. Compromised CRM Account/Brute-force Attack
#### 6. API Attack
