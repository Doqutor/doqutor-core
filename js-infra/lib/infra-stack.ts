import * as cdk from '@aws-cdk/core';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from '@aws-cdk/aws-cognito';
import { createPythonLambda } from './common/lambda';
import { RemovalPolicy, CfnOutput } from '@aws-cdk/core';
import * as iam from "@aws-cdk/aws-iam";
import getModels, { Models } from './api-schema';
import * as sns from '@aws-cdk/aws-sns';
import * as subs from '@aws-cdk/aws-sns-subscriptions';
import * as lambda from '@aws-cdk/aws-lambda';
import { DynamoEventSource } from '@aws-cdk/aws-lambda-event-sources';
import { Config } from '../bin/infra';


export class InfraStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, config: Config, props?: cdk.StackProps) {
    super(scope, id, props);

    const dynamoDoctorsTable = new dynamodb.Table(this, "doctors", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
        removalPolicy: RemovalPolicy.DESTROY
    });
    const dynamoPatientsTable = new dynamodb.Table(this, "patients", {
        partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
        stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        removalPolicy: RemovalPolicy.DESTROY
    });

    /* export physical id value for table for use in monitoring stack
    * exportName is what's visible to other stacks
    */
    new cdk.CfnOutput(this, 'DoctorTable', {
      value: dynamoDoctorsTable.tableName,
      exportName: this.stackName + "-DoctorTable"
    });
    
    new cdk.CfnOutput(this, 'PatientTable', {
      value: dynamoPatientsTable.tableName,
      exportName: this.stackName + "-PatientTable"
    });
    new cdk.CfnOutput(this, 'PatientTableArn', {
      value: dynamoPatientsTable.tableArn,
      exportName: this.stackName + "-PatientTableArn"
    });

    /*
    * Setup rollback operations for patients table
    */
    /* Deny administrator access to sensitive medical info */
    const lambdaDdbAccess = createPythonLambda(this, 'util', 'cloudtrail_ddb_access');
    const snsTopicDdb = new sns.Topic(this, 'DynamoDBAlert', {
      displayName: 'DynamoDB illegal access alert'
    });
    snsTopicDdb.addSubscription(new subs.EmailSubscription(config.email));
    snsTopicDdb.grantPublish(lambdaDdbAccess);
    lambdaDdbAccess.addEnvironment('SNS_ARN', snsTopicDdb.topicArn);
    lambdaDdbAccess.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName); 
    lambdaDdbAccess.addEventSource(new DynamoEventSource(dynamoPatientsTable, {
        startingPosition: lambda.StartingPosition.TRIM_HORIZON,
        batchSize: 1,
        bisectBatchOnError: true,
        retryAttempts: 10
    }))

    lambdaDdbAccess.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        "dynamodb:DeleteItem",
        "dynamodb:PutItem",
        "dynamodb:DescribeStream",
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:ListStreams",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      effect: iam.Effect.ALLOW,
      resources: ["*"]
    }));

      
    /*
    * Cognito and user authentication
    */
    const lambdaCognitoHandler = createPythonLambda(this, 'util', 'cognito_postauth_trigger');
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
    // export
    new CfnOutput(this, 'DoqutoreCognitoPool', {
      value: authPool.userPoolId,
      exportName: this.stackName + '-CognitoPool'
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
      domain: `login-${this.stackName}-${config.env}`,
      userPoolId: authPool.userPoolId
    });
    
    const authClient = new cognito.UserPoolClient(this, 'app_client', {
      userPool: authPool,
      enabledAuthFlows: [cognito.AuthFlow.USER_PASSWORD],
      generateSecret: true
    });
    const cfnResourceServer = new cognito.CfnUserPoolResourceServer(this, 'doqutore-application', {
      identifier: 'doqutore',
      userPoolId: authPool.userPoolId,
      name: 'doqutore',
      scopes: [
        {
          scopeName: 'application',
          scopeDescription: 'our app'
        }
      ]
    });
    const cfnAuthClient = authClient.node.defaultChild as cognito.CfnUserPoolClient;
    cfnAuthClient.addDependsOn(cfnResourceServer);
    cfnAuthClient.readAttributes = ['email', 'email_verified', 'phone_number', 'phone_number_verified', 'custom:type'];
    cfnAuthClient.preventUserExistenceErrors = "ENABLED";
    cfnAuthClient.supportedIdentityProviders = ['COGNITO'];
    cfnAuthClient.allowedOAuthFlows = ['implicit', 'code'];
    cfnAuthClient.allowedOAuthScopes = ['openid', 'phone', 'email', `doqutore/application`];
    cfnAuthClient.callbackUrLs = ['http://localhost', `https://${config.env}.aws9447.me/login`];
    
    
    const lambdaCognitoPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      sid: 'cognitoadminlambda'
    });
    lambdaCognitoPolicy.addResources(authPool.userPoolArn);
    lambdaCognitoPolicy.addActions("cognito-idp:*");

    /*
     * Lambdas for doctor CRUD
     */
    const lambdaCurrentUser = createPythonLambda(this, 'api', 'current_user');
    const lambdaDoctorCreate = createPythonLambda(this, 'api', 'doctors_create');
    const lambdaDoctorUpdate = createPythonLambda(this, 'api', 'doctors_update');
    const lambdaDoctorGet = createPythonLambda(this, 'api', 'doctors_get');
    const lambdaDoctorList = createPythonLambda(this, 'api', 'doctors_list');
    const lambdaDoctorDelete = createPythonLambda(this, 'api', 'doctors_delete');
    
    lambdaDoctorCreate.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorUpdate.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorGet.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorList.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);
    lambdaDoctorDelete.addEnvironment('TABLE_NAME', dynamoDoctorsTable.tableName);

    lambdaCurrentUser.addToRolePolicy(lambdaCognitoPolicy);
    lambdaDoctorCreate.addToRolePolicy(lambdaCognitoPolicy);
    lambdaDoctorUpdate.addToRolePolicy(lambdaCognitoPolicy);
    lambdaDoctorGet.addToRolePolicy(lambdaCognitoPolicy);
    lambdaDoctorList.addToRolePolicy(lambdaCognitoPolicy);
    lambdaDoctorDelete.addToRolePolicy(lambdaCognitoPolicy);

    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorCreate);
    dynamoDoctorsTable.grantReadData(lambdaDoctorGet);
    dynamoDoctorsTable.grantReadData(lambdaDoctorList);
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorDelete);
    dynamoDoctorsTable.grantReadWriteData(lambdaDoctorUpdate);

    /*
     * Lambdas for patients CRUD
     */
    const lambdaPatientCreate = createPythonLambda(this, 'api', 'patients_create');
    const lambdaPatientUpdate = createPythonLambda(this, 'api', 'patients_update');
    const lambdaPatientGet = createPythonLambda(this, 'api', 'patients_get');
    const lambdaPatientList = createPythonLambda(this, 'api', 'patients_list');
    const lambdaPatientDelete = createPythonLambda(this, 'api', 'patients_delete');
    
    lambdaPatientCreate.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName);
    lambdaPatientUpdate.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName);
    lambdaPatientGet.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName);
    lambdaPatientList.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName);
    lambdaPatientDelete.addEnvironment('TABLE_NAME', dynamoPatientsTable.tableName);
    
    lambdaPatientCreate.addToRolePolicy(lambdaCognitoPolicy);
    lambdaPatientUpdate.addToRolePolicy(lambdaCognitoPolicy);
    lambdaPatientGet.addToRolePolicy(lambdaCognitoPolicy);
    lambdaPatientList.addToRolePolicy(lambdaCognitoPolicy);
    lambdaPatientDelete.addToRolePolicy(lambdaCognitoPolicy);

    dynamoPatientsTable.grantReadWriteData(lambdaPatientCreate);
    dynamoPatientsTable.grantReadData(lambdaPatientGet);
    dynamoPatientsTable.grantReadData(lambdaPatientList);
    dynamoPatientsTable.grantReadWriteData(lambdaPatientDelete);
    dynamoPatientsTable.grantReadWriteData(lambdaPatientUpdate);

  
    /*
     * API Gateway
     */
    const api = new apigateway.RestApi(this, 'application', {
      defaultCorsPreflightOptions: {

        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: ['GET', 'POST', 'PUT', 'DELETE']
      }
    });

    // export
    new CfnOutput(this, 'DoqutoreAPIGateway', {
      value: api.restApiId,
      exportName: this.stackName + '-APIGateway'
    });
    
    const apiSchemas = getModels(this, api);
    const apiAuth = new apigateway.CfnAuthorizer(this, 'cognito-auth', {
      name: 'cognito-auth',
      identitySource: 'method.request.header.Authorization',
      restApiId: api.restApiId,
      type: apigateway.AuthorizationType.COGNITO,
      providerArns: [authPool.userPoolArn]
    });
    const requestValidator = api.addRequestValidator('DefaultValidator', {
      validateRequestBody: true
    });

    const authOptions: apigateway.MethodOptions = {
      authorizer: {
        authorizationType: apigateway.AuthorizationType.COGNITO,
        authorizerId: apiAuth.ref
      },
      requestValidator: requestValidator,
      authorizationScopes: ['doqutore/application']
    };
    const resourceUser = api.root.addResource('user');
    resourceUser.addMethod('GET', new apigateway.LambdaIntegration(lambdaCurrentUser), authOptions);

    // Doctor
    const resourceDoctors = api.root.addResource('doctors');
    resourceDoctors.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorList), authOptions);
    resourceDoctors.addMethod('POST', new apigateway.LambdaIntegration(lambdaDoctorCreate), {...authOptions, requestModels: {'application/json': apiSchemas[Models.doctor]}});

    const resourceDoctorId = resourceDoctors.addResource('{id}');
    resourceDoctorId.addMethod('GET', new apigateway.LambdaIntegration(lambdaDoctorGet), authOptions);
    resourceDoctorId.addMethod('PUT', new apigateway.LambdaIntegration(lambdaDoctorUpdate), {...authOptions, requestModels: {'application/json': apiSchemas[Models.doctor]}});
    resourceDoctorId.addMethod('DELETE', new apigateway.LambdaIntegration(lambdaDoctorDelete), authOptions);

    // Patient
    const resourcePatients = api.root.addResource('patients');
    resourcePatients.addMethod('GET', new apigateway.LambdaIntegration(lambdaPatientList), authOptions);
    resourcePatients.addMethod('POST', new apigateway.LambdaIntegration(lambdaPatientCreate), {...authOptions, requestModels: {'application/json': apiSchemas[Models.patient]}});

    const resourcePatientId = resourcePatients.addResource('{id}');
    resourcePatientId.addMethod('GET', new apigateway.LambdaIntegration(lambdaPatientGet), authOptions);
    resourcePatientId.addMethod('PUT', new apigateway.LambdaIntegration(lambdaPatientUpdate), {...authOptions, requestModels: {'application/json': apiSchemas[Models.patient]}});
    resourcePatientId.addMethod('DELETE', new apigateway.LambdaIntegration(lambdaPatientDelete), authOptions);
  }
}
