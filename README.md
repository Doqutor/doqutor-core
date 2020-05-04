
# Doqutore
### Indentification and simulation of automated security incident response using AWS serverless stack. 

- [Objective](#objective)
- [Architecture](#architecture)
- [Features](#features)
- [Incident Response](#incident-response)


### Objective
The project aims to highlight common use cases in an web application based on AWS serverless infrastructure. We have used AWS CDK to deploy the complete [core project](https://github.com/Doqutor/doqutor-core/tree/master/infra). Use the [readme](https://github.com/Doqutor/doqutor-core/blob/master/infra/README.md) to set up and deploy the AWS infrastructure.

### Architecture
![Architecture Diagram](https://github.com/Doqutor/doqutor-core/blob/master/images/arch.jpg)

### Features
- AWS [Lambda](https://github.com/Doqutor/doqutor-core/tree/master/infra/lambda/api) functions as rest API's

### Incident Response
#### 1. Extraneous file added to S3 bucket

![File add to s3 bucket](https://github.com/Doqutor/doqutor-core/blob/master/images/s3_IR.png)
