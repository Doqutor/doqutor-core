# Doqutore CRM AWS Infrastructure

We are using Typescript and Python throughout the code base.

- Typescript: AWS infrastructure deployment
- Python 3: AWS Lambda

## Prerequisites

- JavaScript, TypeScript ([Node.js ≥ 10.12.0](https://nodejs.org/download/release/latest-v10.x/))
- Python ([Python ≥ 3.6](https://www.python.org/downloads/))
- NPM 6.12.0+

---

## Steps

To get started with deploying the complete stack follow the steps below.
The stacks is divided into threee parts:
* <b>Infrastructure Stack</b>: contains all infrastructure for CRM. 
* <b>Frontend Stack</b>: contains the configurations for cloudfront, API Gateway domains and S3 buckets
* <b>Monitoring Stack</b>: contains active monitoring for different components.

1. You have to be in the root of the project to follow the below steps. i.e. venv should be in the root of the folder.
2. Make a new virtual environment for python.

```bash
$ python -m venv ./venv
```

3. Activate virtual environment. <br/>
   Windows | Linux/Mac

```bash
$ venv\Scripts\activate.bat | $ source ./venv/bin/activate
```

4. Change directory to infra and install requirements.

```bash
$ pip install -r requirements.txt
```

5. Install Node modules.

```bash
$ npm install
```

6. Transpile TypeScript to JavaScript.

```bash
$ npm run build
```

## Deployment 

Deployment of the stack involves deploying three seperate stacks, as the later stacks depend on some of the resources in the earlier stacks.

Before deploying the stack, a config file is needed in order to set up the environment. Copy the example below into `config.json`, making sure the `email` and `githubKey` are set up properly.

```json
{
   "env": "dev",
   "prefix": "doqutor",
   "email": "admin@doqutor.com",
   "githubKey": "<github personal acces token>"
}
```

1. The infrastructure stack has to be deployed first.
```sh
# in this case, the stack name is doqutor infrastructure as the prefix above is doqutor
cdk deploy "doqutor-infrastructure"
```

2. The frontend stack comes after the intrastructure stack. The frontend depends on the API gateway in order to point it to the correct custom domain. The frontend is written in Cloudformation and therefore must be deployed with the AWS SDK. Before running these steps, make sure youe AWS access keys and secrets are set up properly. The frontend also depends on some parameters such as the route53 hosted zone id and the certificate id which must be set up manually. 
```sh
# make sure your --parameter-overrides are set up correctly
aws cloudformation deploy --template-file lib/frontend-stack.json --stack-name doqutor-frontend \
--parameter-overrides \
ParamDomainName=prod.doqutor.me \
ParamCFCertificateARN=<arn of certificate> \
ParamZoneId=<route53 zone id for frontend> \
--capabilities CAPABILITY_NAMED_IAM # required for the creation of the frontend deployment user
```
<sub><sup>If you want to skip installing front end and their infrastructure, comment out the section below the comment "Front-end IR and Infrastructure" in [monitoring-stack.ts](./lib/monitoring-stack.ts)</sup></sub>

3. Finally, we can deploy the monitoring stack. Again, we just use the cdk.
```bash
cdk deploy "doqutor-monitoring"
```

4. Back to step 2, the IAM account created can then be used to set up a GitHub pipeline to redeploy the site in case of modification.

Note: Complete implementation of one of our IRs requires running a python script after deploying. See "Generate honeyrecords" in the [incident-response readme](../incident-response/README.md#2-honeyrecord-accessed-by-website-user).

---

More information on AWS CDK

[Developer Guide](https://docs.aws.amazon.com/cdk/latest/guide) |
[CDK Workshop](https://cdkworkshop.com/) |
[Getting Started](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) |
[API Reference](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html) |
[Examples](https://github.com/aws-samples/aws-cdk-examples)
