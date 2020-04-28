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

Honeyrecords can be generated and set up with the honeyrecordgen.py script.
To generate the required inputs for honeyrecordgen.py from the stack name, and then run honeyrecordgen, run runhoneygen.sh
To simulate, run honeyrecordsim.py. You will need a cognito user and a current access token.
A user can be created with addcognitouser.sh.

Two ways to get an API token:
1. Launch cognito hosted ui and change the following query parameters before logging in, then extract access_token from the redirect url:

            response_type=token
            scope=doqutore/application
2. Login using website, and retrieve config:token from cookies

Then prepend 'bearer '. If using option 1, the token can be generated from the redirect url with following python:
```python
print("Bearer " + (url.split("access_token=", 1)[1]).split("&")[0])
```
The API endpoint can be retrieved from cdk deploy output.
Then run
```bash
$ python honeyrecordsim.py APIEndpoint AuthToken
```
eg
```bash
$ python honeyrecordsim.py APIEndpoint "$(python -c 'print("Bearer " + url.split("access_token=", 1)[1].split("&")[0])')"
```


