import * as cloudtrail from '@aws-cdk/aws-cloudtrail';
import * as events from '@aws-cdk/aws-events';
import * as cdk from '@aws-cdk/core';
import * as sns from '@aws-cdk/aws-sns';
import * as subscriptions from '@aws-cdk/aws-sns-subscriptions';
import {ServicePrincipals} from 'cdk-constants';
import * as targets from '@aws-cdk/aws-events-targets';
import {createPythonLambda} from './common/lambda';
import * as iam from '@aws-cdk/aws-iam';
import * as cloudwatch from '@aws-cdk/aws-cloudwatch';
import * as cw_actions from '@aws-cdk/aws-cloudwatch-actions';
import * as wafv2 from '@aws-cdk/aws-wafv2';
import { Duration } from '@aws-cdk/core';


export class MonitoringStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /*
    * CloudTrail and sns
    */
    const trail = new cloudtrail.Trail(this, 'cloudwatch', {
      sendToCloudWatchLogs: true
    });
    const snsTopic = new sns.Topic(this, 'CloudtrailAlert', {
      displayName: 'Cloudtrail Alert'
    });
    const user = new iam.User(this, 'testUser');
    user.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'));

    snsTopic.addSubscription(new subscriptions.EmailSubscription('747b13b7.groups.unsw.edu.au@apac.teams.ms'));

    /*
    * Events for detecting that cloudtrail was turned off
    */
    const eventPattern: events.EventPattern = {
      source: ['aws.cloudtrail'],
      detail: {
        eventSource: [
          ServicePrincipals.CLOUD_TRAIL
        ],
        eventName: [
          "StopLogging",
          "StartLogging",
          "DeleteTrail",
          "CreateTrail"
        ]
      }
    };
    const rule = new events.Rule(this, 'ruleFromCDKForStoppedLogging', {
      eventPattern: eventPattern,
      description: "If CloudTrail logging is stopped this event will fire"
    });
    const lambdaCloudtrailLogging = createPythonLambda(this, 'util', 'cloudtrail_restartlog');
    lambdaCloudtrailLogging.addEnvironment('TRAIL_ARN', trail.trailArn);
    lambdaCloudtrailLogging.addEnvironment('SNS_ARN', snsTopic.topicArn);
    snsTopic.grantPublish(lambdaCloudtrailLogging);

    // allow lambda to access cloudtrail
    lambdaCloudtrailLogging.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'cloudtrail:StartLogging'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*']
    }));

    // allow lambda to attach policies to user
    lambdaCloudtrailLogging.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'iam:AttachUserPolicy'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*'],
      conditions: {ArnEquals: {"iam:PolicyARN" : "arn:aws:iam::aws:policy/AWSDenyAll"}}
    }));

    rule.addTarget(new targets.LambdaFunction(lambdaCloudtrailLogging));
    rule.addTarget(new targets.SnsTopic(snsTopic));

    /*
    * CloudWatch rulesets here
    */

    const stackName = this.stackName.replace("monitoring", "infrastructure"); // to correctly refrence other stack
    const snsTopicCw = new sns.Topic(this, 'CloudwatchAlert', {
      displayName: 'Cloudwatch Alert'
    });
    snsTopicCw.addSubscription(new subscriptions.EmailSubscription('747b13b7.groups.unsw.edu.au@apac.teams.ms'));

    const ddbMetric = new cloudwatch.Metric({
      metricName: "ConsumedReadCapacityUnits",
      namespace: "AWS/DynamoDB",
      statistic: "Sum",
      dimensions: {TableName: cdk.Fn.importValue(stackName+"-DoctorTable")},
    });
    const ddbExcessReadAlarmDoc = new cloudwatch.Alarm(this, 'ddbExcessReadAlarmDoc', {
      metric: ddbMetric,
      threshold: 1200,
      period: Duration.seconds(60),
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
    });

    const ddbMetricPat = new cloudwatch.Metric({
      metricName: "ConsumedReadCapacityUnits",
      namespace: "AWS/DynamoDB",
      statistic: "Sum",
      dimensions: {TableName: cdk.Fn.importValue(stackName+"-PatientTable")},
    });
    const ddbExcessReadAlarmPat = new cloudwatch.Alarm(this, 'ddbExcessReadAlarmPat', {
      metric: ddbMetricPat,
      threshold: 1200,
      period: Duration.seconds(60),
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
    });

    // binding sns topic to cloudwatch alarm
    ddbExcessReadAlarmDoc.addAlarmAction(new cw_actions.SnsAction(snsTopicCw));
    ddbExcessReadAlarmPat.addAlarmAction(new cw_actions.SnsAction(snsTopicCw));

    // creating a lambda triggered by sns topic notification
    //const debugLambda = createPythonLambda(this, 'util', 'dummy_lambda');
    //snsTopicCw.addSubscription(new subscriptions.LambdaSubscription(debugLambda));

    /* Deny administrator access to sensitive medical info */
    const ddbEventPattern: events.EventPattern = {
      source: ['aws.dynamodb'],
      detail: {
        eventSource: [
          ServicePrincipals.CLOUD_TRAIL
        ],
        eventName: [
          "CreateBackup",
          "CreateGlobalTable",
          "CreateTable",
          "DeleteBackup",
          "DeleteTable",
          "DescribeBackup",
          "DescribeContinuousBackups",
          "DescribeGlobalTable",
          "DescribeLimits",
          "DescribeTable",
          "DescribeTimeToLive",
          "ListBackups",
          "ListTables",
          "ListTagsOfResource",
          "ListGlobalTables",
          "RestoreTableFromBackup",
          "RestoreTableToPointInTime",
          "TagResource",
          "UntagResource",
          "UpdateGlobalTable",
          "UpdateTable",
          "UpdateTimeToLive",
          "DescribeReservedCapacity",
          "DescribeReservedCapacityOfferings",
          "DescribeScalableTargets",
          "RegisterScalableTarget",
          "PurchaseReservedCapacityOfferings"
        ]
      }
    };
    const ddbRule = new events.Rule(this, 'illegalAccessDatabase', {
      eventPattern: eventPattern,
      description: "If non-lambda roles access database, they will be blocked"
    });
    // CHECK EVENT, THEN CHECK USER'S ROLE, THEN BLOCK 
    const lambdaDdbAccess = createPythonLambda(this, 'util', 'cloudtrail_ddb_access');
    const snsTopicDdb = new sns.Topic(this, 'DynamoDBAlert', {
      displayName: 'DynamoDB illegal access alert'
    });
    snsTopicDdb.addSubscription(new subscriptions.EmailSubscription('747b13b7.groups.unsw.edu.au@apac.teams.ms'));
    lambdaDdbAccess.addEnvironment('TRAIL_ARN', trail.trailArn);
    lambdaDdbAccess.addEnvironment('SNS_ARN', snsTopicDdb.topicArn);
    snsTopicDdb.grantPublish(lambdaDdbAccess);
    ddbRule.addTarget(new targets.LambdaFunction(lambdaDdbAccess));
    ddbRule.addTarget(new targets.SnsTopic(snsTopicDdb));

    lambdaDdbAccess.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'cloudtrail:*'
      ],
      effect: iam.Effect.ALLOW,
      resources: [trail.trailArn]
    }));

    lambdaDdbAccess.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'iam:*'
      ],
      effect: iam.Effect.ALLOW,
      resources: ['*'],
    }));

        // WAF
    // only allow 128 requests per 5 minutes, a pretty generous limit for a small practice
    // assuming that a clinic is located at the same ip address
    const wafAPI = new wafv2.CfnWebACL(this, 'waf-api', {
      defaultAction: {
        allow: {}
      },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: 'waf-apigateway',
        sampledRequestsEnabled: true
      },
      scope: 'REGIONAL',
      rules: [
        {
          name: 'ratelimit',
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 128,
              aggregateKeyType: 'IP'
            }
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'waf-apigateway-ratelimit',
            sampledRequestsEnabled: true
          },
          action: {
            block: {}
          }
        }
      ]
    });
    new wafv2.CfnWebACLAssociation(this, 'waf-assoc-apigateway', {
      resourceArn: `arn:aws:apigateway:${this.region}::/restapis/${cdk.Fn.importValue(stackName+"-APIGateway")}/stages/prod`,
      webAclArn: wafAPI.attrArn
    });


  }
}
