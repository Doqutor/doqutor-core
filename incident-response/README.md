# Incident Response

:information_source:
Requirements: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html "Install AWS CLI")
<br/> 
###### Select JSON/None as the [default output format](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html "Configuring the AWS CLI")

To simulate incident response we must install requirements and additional packages.
<br/>
```bash
 $ pip install -r requirements.txt
 ```

----
# Simulations

#### 1. Illicit modifications to the frontend S3 bucket
When an illicit change (i.e. a change that was not deployed by the CI/CD pipeline) is detected, a full rerun of the pipeline will be commissioned.

To trigger this action: try adding, deleting or modifying any file in the frontend S3 bucket. Name of the s3 bucket would be: `s3://doqutore-frontend-frontends3bucket-*`




##### 2. CloudTrail stopped by user: 
If a user shuts down any CloudTrail instance, the user will be blocked by attaching <b>AWSDenyAll</b> policy to the user.

Set up a dummy user for demonstration. You must have admin rights to access this user. This user was already created with your stack. 
```bash
$ python setup_user.py
 ```
 You can manually create a user using IAM. [Create an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html "Create AWS IAM user guide") and change your [local AWS config](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html "Configuring the AWS CLI"). 

To simulate with a wizard
```bash
$ python cloudtrail_ir.py
 ```
:warning: You can block yourself from AWS account if you did not follow step to create user. 


#### 3. Honeyrecord accessed by website user:
If a cognito user accesses a honeyrecord through the API, the user will be signed out and disabled, and the abused token will be invalidated by adding it to a revoked tokens database. Note that the user used in this step will be disabled.

Note that the honeyrecord generation script runhoneygen.py serves as part of the deployment stack, intended to be run after cdk deploy. The relevant lambdas (patients_get and patients_delete) will also need to be run once before the script is executed, to create the log groups that will be monitored. The lambdas could be run through the website/API or the API Gateway test console.

Running simulation:
1. <b>Generate honeyrecords</b>  
To complete deployment by generating honeyrecords and creating the subscription filter, run runhoneygen.py:
    ```bash
    $ python runhoneygen.py $numberOfHoneyTokens $stackName
    ```
    Or, to run the backing script with custom inputs, use honeyrecordgen.py:
    ```bash
    $ python honeyrecordgen.py $numberOfHoneyTokens $tablename $subscriptionFilterdestinationArn $sourceLogGroupName $sourceLogGroupName2 ...
    ```
    
2. <b>Retrieve auth token for API access</b>  
Run gettoken.py and follow the instructions:
    ```bash
    $ python gettoken.py $stackName
    ```
    The process can also be done manually and involves:  
    1. Create a cognito user
    2. Login using cognito user and extract access_token from login result, eg by  
    a) Logging in through hosted ui (with query parameters '&response_type=token&scope=doqutore/application&redirect_uri=http://localhost' following client_id) and extracting access_token from redirect url  
    b) Logging in through website and getting config:token from localstorage  
    c) Using cognito initiate-auth using aws cli
 
 3. <b>Simulate</b>  
Run honeyrecordsim.py.
The API endpoint can be retrieved from output of cdk deploy.
Intended use requires appending '/patients' to that url.
    ```bash
    $ python honeyrecordsim.py $APIEndpoint "$AuthToken"
    ```


#### 4. Illegal write into Patient table
Data that is assumed to be unmodifiable (in this case _insurance_id_) is rolled back if an administrator makes changes to that field

Wizard and demo of the incident can be executed using below command.
```bash
$ python ddb_access_ir.py
```

#### 5. Brute-Forcing Cognito
First, we have a script to create a cognito user in `create-cognito-user.sh`. This creates a user which we can use to log in to the cognito pool. The password will be sent to the phone
number within the script. Modify the variables at the beginning of the script to set attributes.

```sh
$ ./create-cognito-user.sh
```

This selenium script goes to the login page and tries to log in with the specified username and a random password for 15 times. This will allow it to trigger Cognito's suspicious login
detection.

```sh
$ python demo-password.py
```


#### 6. Rate limiting
This cURL script just hits the endpoint around 1000 times which should be enough to trigger the WAF. It runs requests sequentially
```sh
$ ./demo-waf.sh
```
