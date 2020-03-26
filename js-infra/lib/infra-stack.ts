import * as cdk from '@aws-cdk/core';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from '@aws-cdk/aws-cognito';
import { createPythonLambda } from './common/lambda';

export class InfraStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    
    const dynamoDoctorsTable = new dynamodb.Table(this, "doctors", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }
    });
    
    const dynamoPatientsTable = new dynamodb.Table(this, "patients", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }
    });
    
    
    /*
     * Cognito and user authentication
     */
    const lambdaCognitoHandler = createPythonLambda(this, 'cognito_trigger');
    dynamoDoctorsTable.grantReadWriteData(lambdaCognitoHandler);
    dynamoPatientsTable.grantReadWriteData(lambdaCognitoHandler);
    lambdaCognitoHandler.addEnvironment("DOCTOR_TABLE", dynamoDoctorsTable.tableName)
    lambdaCognitoHandler.addEnvironment("PATIENT_TABLE", dynamoPatientsTable.tableName)
    
    const authPool = new cognito.UserPool(this, 'crm-users', {
      customAttributes: {
        type: new cognito.StringAttribute()
      },
      requiredAttributes: {
        email: true,
        phoneNumber: true,
        fullname: true,
        birthdate: true
      },
      lambdaTriggers: {
        postConfirmation: lambdaCognitoHandler
      },
    });
    (authPool.node.defaultChild as cognito.CfnUserPool).userPoolAddOns = {advancedSecurityMode: 'YES'}; 
    new cognito.CfnUserPoolDomain(this, 'crm-users-login', {
      domain: `login-${this.stackName}`,
      userPoolId: authPool.userPoolId
    });
    
    const authClient = new cognito.UserPoolClient(this, 'app_client', {
      userPool: authPool,
      enabledAuthFlows: [cognito.AuthFlow.USER_PASSWORD]
    });
    const cfnAuthClient = authClient.node.defaultChild as cognito.CfnUserPoolClient;
    cfnAuthClient.supportedIdentityProviders = ['COGNITO'];
    cfnAuthClient.allowedOAuthFlows = ['implicit'];
    cfnAuthClient.allowedOAuthScopes = ['openid'];
    cfnAuthClient.callbackUrLs = ['http://localhost'];
    
    
    
    /*
     * Lambdas for doctor CRUD
     */
    const lambdaDoctorCreate = createPythonLambda(this, 'doctors_create');
    const lambdaDoctorUpdate = createPythonLambda(this, 'doctors_update');
    const lambdaDoctorGet = createPythonLambda(this, 'doctors_get');
    const lambdaDoctorList = createPythonLambda(this, 'doctors_list');
    const lambdaDoctorDelete = createPythonLambda(this, 'doctors_delete');
    
    lambdaDoctorCreate.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorUpdate.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorGet.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorList.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorDelete.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorCreate);
    dynamoDoctorsTable.grantReadData(lambdaDoctorGet);
    dynamoDoctorsTable.grantReadData(lambdaDoctorList);
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorDelete);
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorUpdate)

    
  
    /*
     * API Gateway
     */
    const api = new apigateway.RestApi(this, 'application');
    
    const resourceDoctors = api.root.addResource("doctors");
    resourceDoctors.addCorsPreflight({
      // TODO: specific allow origins
      allowOrigins: apigateway.Cors.ALL_ORIGINS,
      allowMethods: ['GET', 'POST']
    })
    resourceDoctors.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorList));
    resourceDoctors.addMethod('POST', new apigateway.LambdaIntegration(lambdaDoctorCreate));
    
    const resourceDoctorId = resourceDoctors.addResource('{id}');
    resourceDoctorId.addCorsPreflight({
      // TODO: specific allow origins
      allowOrigins: apigateway.Cors.ALL_ORIGINS,
      allowMethods: ['GET', 'PUT', 'DELETE']
    });
    resourceDoctorId.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorGet));
    resourceDoctorId.addMethod('PUT', new apigateway.LambdaIntegration(lambdaDoctorUpdate));
    resourceDoctorId.addMethod('DELETE', new apigateway.LambdaIntegration(lambdaDoctorDelete));
  }
}
