
# Doqutore CRM AWS Infrastructure


We are using Typescript and Python throughout the code base. 
* Typescript: AWS infrastructure deployment
* Python 3: AWS Lambda

To follow the installations steps, you require

* JavaScript, TypeScript ([Node.js ≥ 10.12.0](https://nodejs.org/download/release/latest-v10.x/))
* Python ([Python ≥ 3.6](https://www.python.org/downloads/))
* NPM 6.12.0+
-------

To get started with deploying the complete stack follow the steps below.
The stacks is divided into two parts:
* <b>Infrastructure Stack</b>: contains all infrastructure for CRM. 
* <b>Monitoring Stack</b>: contains active monitoring for different components.

Steps:
1. Make a new virtual environment for python.
 
```bash
$ python -m venv ./venv
```

2. Activate virtual environment. <br/>
Windows | Linux/Mac
```bash 
$ venv\Scripts\activate.bat | $ ./venv/bin/activate
```
3. Change directory to js-infra and install requirements.
```bash 
$ pip install -r requirements.txt
```
4. Install Node modules.
```bash 
$ npm install
```
5. Transpile TypeScript to js. 
```bash
$ npm run build
```
6. Now deploy the AWS stack. We customize the stack name with your OS username. We have two stacks, you can deploy them separately or else use regex style *. But "infrastructure stack" must be created first as "monitoring stack" requires some inputs from "infrastructure stack". 
```bash
$ cdk deploy *stack-name*
```

To destroy the stack
```bash
$ cdk destroy *stack-name*
```


-------
More information on AWS CDK

[Developer Guide](https://docs.aws.amazon.com/cdk/latest/guide) |
[CDK Workshop](https://cdkworkshop.com/) |
[Getting Started](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) |
[API Reference](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html) |
[Examples](https://github.com/aws-samples/aws-cdk-examples) |
