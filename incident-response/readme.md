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
#### 0. Set up dummy user: 
Set up a dummy user for demonstration. You must have admin rights to access this user. This user was already created with your stack. 
```bash
$ python setup_user.py
 ```
 You can manually create a user using IAM. [Create an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html "Create AWS IAM user guide") and change your [local AWS config](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html "Configuring the AWS CLI"). 


#### 1. CloudTrail stopped by user: 
If a user shuts down any CloudTrail instance, the user will be blocked by attaching <b>AWSDenyAll</b> policy to the user.
To simulate with a wizard
```bash
$ python cloudtrail_ir.py
 ```
:warning: You can block yourself from AWS account if you did not follow step 0. 


#### 2. Honeyrecord accessed by website user:
in progress

Explanation

Note that the honeyrecord generation script serves as part of the deployment stack, intended to be run after cdk deploy. The relevant lambdas (patients_get and patients_delete) will also need to be run once before the script is executed, to create the log groups that will be monitored. The lambdas could be run through the website/API or the API Gateway test console.

Running simulation:
1. <b>Generate honeyrecords</b>  
Honeyrecords can be generated and set up with the honeyrecordgen.py script:
    ```bash
    $ python honeyrecordgen.py $numberOfHoneyTokens $tablename $subscriptionFilterdestinationArn $sourceLogGroupName $sourceLogGroupName2 ...
    ```
    Or, to run honeyrecordgen.py with intended inputs generated from the stack name, run runhoneygen.py (script in progress, bash version available):
    ```bash
    $ python runhoneygen.py $numberOfHoneyTokens $stackName
    ```
2. <b>Retrieve auth token for API access</b>  
in progress.  
First: Create a cognito user. This can be done through the aws cli, for example with:
    !! check these inputs they might be old
    ```bash
    $ aws cognito-idp admin-create-user \
    --user-pool-id $USERPOOLID \
    --username honeytestuser \
    --user-attributes Name=email,Value=$EMAIL Name=phone_number,Value="+1212555123" Name=custom:type,Value=doctor Name=email_verified,Value=True Name=phone_number_verified,Value=True \
    --temporary-password $PASSWORD
    ```
    Then: Retrieve token and prepend with 'Bearer ' using one of these methods:  
    a) Login using hosted ui with the following query parameters after client_id:
    ```
    response_type=token&scope=doqutore/application&redirect_uri=http://localhost
    ! CHECK THIS
    ```
    and extract access_token from the redirect url, for example with
    ```bash
    $ python -c 'print("Bearer " + YOUR_URL.split("access_token=", 1)[1].split("&")[0])'
    ```
    b) Login using website, and copy config:token from localstorage  
    c) Somehow get cognito initiate-auth to work in AWS cli
 
 3. <b>Simulate</b>  
Run honeyrecordsim.py.
The API endpoint can be retrieved from cdk deploy output.
    ```bash
    $ python honeyrecordsim.py $APIEndpoint "$AuthToken"
    ```


#### 3. Illegal write into Patient table
Data that is assumed to be unmodifiable (in this case _insurance_id_) is rolled back if an administrator makes changes to that field

Wizard and demo of the incident can be executed using below command.
```bash
$ python ddb_access_ir.py
```
