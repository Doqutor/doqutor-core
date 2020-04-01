import * as cdk from '@aws-cdk/core';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from '@aws-cdk/aws-cognito';
import { createPythonLambda, createTypeScriptLambda } from './common/lambda';
import {Watchful} from 'cdk-watchful';
import * as cloudtrail from '@aws-cdk/aws-cloudtrail';
import * as events from '@aws-cdk/aws-events';
import { ServicePrincipals } from "cdk-constants";
import * as lambda from '@aws-cdk/aws-lambda';
import * as eventTarget from '@aws-cdk/aws-events-targets';
import { RemovalPolicy } from '@aws-cdk/core';


export class InfraStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    const dynamoDoctorsTable = new dynamodb.Table(this, "doctors", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
        removalPolicy: RemovalPolicy.DESTROY
    });
    
    const dynamoPatientsTable = new dynamodb.Table(this, "patients", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
        removalPolicy: RemovalPolicy.DESTROY
    });
    
    
    /*
     * Cognito and user authentication
     */
    const lambdaCognitoHandler = createPythonLambda(this, 'cognito_postauth_trigger');
    dynamoDoctorsTable.grantReadWriteData(lambdaCognitoHandler);
    dynamoPatientsTable.grantReadWriteData(lambdaCognitoHandler);
    lambdaCognitoHandler.addEnvironment("DOCTOR_TABLE", dynamoDoctorsTable.tableName);
    lambdaCognitoHandler.addEnvironment("PATIENT_TABLE", dynamoPatientsTable.tableName);
    
    const authPool = new cognito.UserPool(this, 'crm-users', {
      customAttributes: {
        type: new cognito.StringAttribute()
      },
      requiredAttributes: {
        email: true,
        phoneNumber: true
      },
      lambdaTriggers: {
        postAuthentication: lambdaCognitoHandler
      }
    });
    const cfnAuthPool = authPool.node.defaultChild as cognito.CfnUserPool;
    cfnAuthPool.userPoolAddOns = {
      advancedSecurityMode: 'ENFORCED'
    };
    cfnAuthPool.usernameConfiguration = { caseSensitive: false };
    // (authPool.node.defaultChild as cognito.CfnUserPool).emailConfiguration = {
    //   sourceArn: "arn:aws:ses:us-west-2:018904123317:identity/z5122502.cs9447@cse.unsw.edu.au"
    // };

    new cognito.CfnUserPoolDomain(this, 'crm-users-login', {
      domain: `login-${this.stackName}`,
      userPoolId: authPool.userPoolId
    });
    
    const authClient = new cognito.UserPoolClient(this, 'app_client', {
      userPool: authPool,
      enabledAuthFlows: [cognito.AuthFlow.USER_PASSWORD],
      generateSecret: true
    });
    const cfnAuthClient = authClient.node.defaultChild as cognito.CfnUserPoolClient;
    cfnAuthClient.readAttributes = ['email', 'email_verified', 'phone_number', 'phone_number_verified', 'custom:type'];
    cfnAuthClient.preventUserExistenceErrors = "ENABLED";
    cfnAuthClient.supportedIdentityProviders = ['COGNITO'];
    cfnAuthClient.allowedOAuthFlows = ['implicit', 'code'];
    cfnAuthClient.allowedOAuthScopes = ['openid', 'phone'];
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
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorUpdate);

    /*
     * Lambdas for IR
     */
    const lambdaCloudtrailLogging = createTypeScriptLambda(this, 'cloudTrail_stopped_logging');
    
  
    /*
     * API Gateway
     */
    const api = new apigateway.RestApi(this, 'application', {
      defaultCorsPreflightOptions: {

        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: ['GET', 'POST', 'PUT', 'DELETE']
      }
    });
    const apiAuth = new apigateway.CfnAuthorizer(this, 'cognito-auth', {
      name: 'cognito-auth',
      identitySource: 'method.request.header.Authorization',
      restApiId: api.restApiId,
      type: apigateway.AuthorizationType.COGNITO,
      providerArns: [authPool.userPoolArn]
    });
    const resourceDoctors = api.root.addResource('doctors');
    resourceDoctors.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorList), {
      authorizer: {
        authorizationType: apigateway.AuthorizationType.COGNITO,
        authorizerId: apiAuth.ref
      }
    });
    resourceDoctors.addMethod('POST', new apigateway.LambdaIntegration(lambdaDoctorCreate), {
      authorizer: {
        authorizationType: apigateway.AuthorizationType.COGNITO,
        authorizerId: apiAuth.ref
      }
    });

    
    const resourceDoctorId = resourceDoctors.addResource('{id}');
    resourceDoctorId.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorGet));
    resourceDoctorId.addMethod('PUT', new apigateway.LambdaIntegration(lambdaDoctorUpdate));
    resourceDoctorId.addMethod('DELETE', new apigateway.LambdaIntegration(lambdaDoctorDelete));

    /*
     * Monitoring
     */
    const wf = new Watchful(this, 'watchful', {
      alarmEmail: '747b13b7.groups.unsw.edu.au@apac.teams.ms'
    });
    wf.watchApiGateway('Watcher API Gateway', api);
    wf.watchDynamoTable('Watcher Db Doctors', dynamoDoctorsTable);
    wf.watchDynamoTable('Watcher Db Patients', dynamoPatientsTable);

    /*
     * CloudTrail
     */
    const trail = new cloudtrail.Trail(this, 'cloudwatch', {
      sendToCloudWatchLogs: true
    });

    /*
    * Infrastructure for cloudTrail IR
     */
    const eventPattern: events.EventPattern = {
        source: ["aws.cloudtrail"],
        detail: {
          eventSource: [
            ServicePrincipals.CLOUD_TRAIL
          ],
          eventName: [
            "StopLogging"
          ]
        }
    };
    const rule = new events.Rule(this, 'ruleFromCDKForStoppedLogging', {
      eventPattern: eventPattern,
      description: "If CloudTrail logging is stopped this event will fire"
    });
    rule.addTarget(new eventTarget.LambdaFunction(lambdaCloudtrailLogging));
  }
}
