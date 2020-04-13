import * as cdk from '@aws-cdk/core';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from '@aws-cdk/aws-cognito';
import { createPythonLambda, createTypeScriptLambda } from './common/lambda';
import { RemovalPolicy } from '@aws-cdk/core';
import getModels, { Models } from './api-schema';
//import {Watchful} from 'cdk-watchful';
//import * as cloudtrail from '@aws-cdk/aws-cloudtrail';
//import * as events from '@aws-cdk/aws-events';
//import { ServicePrincipals } from "cdk-constants";
//import * as targets from '@aws-cdk/aws-events-targets';
//import * as SubscriptionFilter from '@aws-cdk/aws-logs.SubscriptionFilter';

// for honeytoken only, presumably to be removed when moved to monitoring-stack
import * as subscriptions from '@aws-cdk/aws-sns-subscriptions';
import * as iam from '@aws-cdk/aws-iam';
import * as LogGroup from '@aws-cdk/aws-logs';
import * as sns from '@aws-cdk/aws-sns';
import * as LogsDestinations from '@aws-cdk/aws-logs-destinations';


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
      /*lambdaTriggers: {
        postAuthentication: lambdaCognitoHandler
      }*/
      // this is commented out because of problems when I deploy lambdas in util folder
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
    new cognito.CfnUserPoolResourceServer(this, 'doqutore-application', {
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
    cfnAuthClient.readAttributes = ['email', 'email_verified', 'phone_number', 'phone_number_verified', 'custom:type'];
    cfnAuthClient.preventUserExistenceErrors = "ENABLED";
    cfnAuthClient.supportedIdentityProviders = ['COGNITO'];
    //cfnAuthClient.allowedOAuthFlows = ['implicit', 'code'];
    cfnAuthClient.allowedOAuthFlows = ['implicit']; // for me to use API
    cfnAuthClient.allowedOAuthScopes = ['openid', 'phone', 'email', 'doqutore/application'];
    cfnAuthClient.callbackUrLs = ['http://localhost', 'https://dev.aws9447.me/login'];
    
    
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
      },
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true
        // add custom access logs maybe
      }
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



    /*
    * Honeytoken IR
    * left this in infra-stack for the moment because it needs access to the lambdas
    */
    // Cloudwatch logs
    const logGroup = new LogGroup.LogGroup(this, 'LogGroup', {
      retention: Infinity
    });

   // sns topic
   /*
    const snsTopicCW = new sns.Topic(this, 'CloudwatchAlert', {
      displayName: 'Cloudwatch Alert'
    });
    snsTopicCW.addSubscription(new subscriptions.EmailSubscription('747b13b7.groups.unsw.edu.au@apac.teams.ms'));
    */

    const snsTopicHT = new sns.Topic(this, 'HoneytokenSNS', {
      displayName: 'Honeytoken SNS'
    });
    snsTopicHT.addSubscription(new subscriptions.EmailSubscription('059aa1ad.groups.unsw.edu.au@apac.teams.ms'));

    // test user
    const user = new iam.User(this, 'testUser');
    user.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'));

    //const lambdaBlockAWSUser = createPythonLambda(this, 'util', 'block_user');
    const lambdaBlockUser = createPythonLambda(this, 'api', 'block_user2');
    // const lambdaBlockUser = createPythonLambda(this, 'api/blockuser2.zip', 'block_user2') 
    const denyAllPolicy = new iam.PolicyStatement({
      actions: [
        'iam:AttachUserPolicy'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*'],
      conditions: {ArnEquals: {"iam:PolicyARN" : "arn:aws:iam::aws:policy/AWSDenyAll"}}
    });
    const cognitoPolicy = new iam.PolicyStatement({
      actions: [
        'cognito-idp:AdminDisableUser',
        'cognito-idp:AdminUserGlobalSignOut'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*'] // change this
    });
    const snsPolicy = new iam.PolicyStatement({
      actions: [
        'SNS:Publish'
      ],
      effect: iam.Effect.ALLOW,
      resources: [snsTopicHT.topicArn]
    });
    lambdaBlockUser.addToRolePolicy(denyAllPolicy);
    lambdaBlockUser.addToRolePolicy(cognitoPolicy);
    lambdaBlockUser.addToRolePolicy(snsPolicy)
    lambdaBlockUser.addEnvironment('SNS_TOPIC_ARN', snsTopicHT.topicArn)
    // what about mistakes. prob want to make sure it doesn't block the root account or smth

    const dirtytokensTable = new dynamodb.Table(this, "dirtyTokens", {
      partitionKey: { name: 'token', type: dynamodb.AttributeType.STRING },
      removalPolicy: RemovalPolicy.DESTROY,
      timeToLiveAttribute: 'expiry'
    });
    dirtytokensTable.grantWriteData(lambdaBlockUser);
    dirtytokensTable.grantReadData(lambdaDoctorGet);
    lambdaBlockUser.addEnvironment('TABLE_NAME', dirtytokensTable.tableName);
    lambdaDoctorGet.addEnvironment('TOKENS_TABLE_NAME', dirtytokensTable.tableName);


    // "\"path\": \"/doctors/5555\""
    // [type=INFO, timestamp, somecode, label=*id*, id=5555, ...]
    // [type=INFO, timestamp=*Z, request_id="*-*", event=*reqid*5555*]
    // the block_user2.py function is based on the above filter pattern, added using AWS console
    // filter pattern was added using aws console because stack deployment freezes when I try to deploy it
    
    /*
    lambdaDoctorGet.logGroup.addSubscriptionFilter('getsubscription', {
      destination: new LogsDestinations.LambdaDestination(lambdaBlockAWSUser),
      filterPattern: LogGroup.FilterPattern.allTerms('doctors_get', '5555')
    })
    */

    /*
    new LogGroup.SubscriptionFilter(this, 'Subscription', {
      logGroup: lambdaDoctorGet.logGroup,
      destination: new LogsDestinations.LambdaDestination(lambdaBlockAWSUser),
      filterPattern: LogGroup.FilterPattern.allTerms('doctors_get', '5555')
    });
    */

    /*
    new LogGroup.SubscriptionFilter(this, 'Subscription', {
      logGroup,
      destination: new LogsDestinations.LambdaDestination(lambdaDoctorGet),
      filterPattern: LogGroup.FilterPattern.allTerms('doctors_get', '5555') // replace with pattern below
    });
    */
    
    /*
    const pattern = LogGroup.FilterPattern.anyGroup(
      ['doctors_get', '5555'],
      ['doctors_delete', '5555'],
      );
    */
    // const pattern1 = FilterPattern.allTerms('doctors_get', '5555'); // reaplce with the actual id of the honey token
    // const pattern2 = FilterPattern.allTerms('doctors_delete', '5555'); // reaplce with the actual id of the honey token

    // Search for lines that either contain both "doctors_get" and honey token id, or
    // both "doctors_delete" and honey token id.  
    
    // allow lambda to attach policies to user
    /*
    lambdaCloudtrailLogging.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'iam:AttachUserPolicy'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*'],
      conditions: {ArnEquals: {"iam:PolicyARN" : "arn:aws:iam::aws:policy/AWSDenyAll"}}
    }));
    */
    
    //rule.addTarget(new targets.LambdaFunction(lambdaDoctorGet));
    //rule.addTarget(new targets.SnsTopic(snsTopic));
  }
}
