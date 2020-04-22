# Doqutore CRM AWS Infrastructure


We are using Typescript and Python throughout the code base. 
* Typescript: AWS infrastructure deployment
* Python 3: AWS Lambda

To follow the installations steps, you require 
* Node 12.13.0+
* NPM 6.12.0+
* Python 3.7+

To get started with deploying the complete stack follow the steps below.
The stacks is divided into two parts:
* <b>Infrastructure Stack</b>: contains all infrastructure for CRM. 
* <b>Monitoring Stack</b>: contains active monitoring for different components.

Steps:
1. Make a new virtual environment for python.
Type <br/> 
```python -m venv ./venv``` 
2. Activate virtual environment. <br/>
Windows : ```venv\Scripts\activate.bat``` 
<br/>
Linux/Mac : ```venv/Scripts/activate```<br/>
3. Change directory to js-infra and install requirements. <br/>
```pip install -r requirements.txt```
4. Install Node modules. <br/>
```npm install```
5. Transpile TypeScript to js. <br/>
```npm run build```
6. Now deploy the AWS stack. We customize the stack name with your OS username. We have two stacks, you can deploy them separately or else use regex style *. But "infrastructure stack" must be created first as "monitoring stack" requires some inputs from "infrastructure stack".<br/>
```cdk deploy stack-name```
<br/>OR<br/>
```cdk deploy *```<br/>
