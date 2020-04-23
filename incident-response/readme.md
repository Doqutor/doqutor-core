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
  