# Incident Response

To simulate incident response we must install requirements and additional packages.
<br/>
```bash
 $ pip install -r requirements.txt
 ```
<br/>

1. CloudTrail stopped by user: If a user shuts down any CloudTrail instance, the user will be blocked by attaching <b>AWSDenyAll</b> policy to the user.
To simulate with a wizard
```bash
$ python cloudtrail_ir.py
 ```
!x This is an error message.
  
