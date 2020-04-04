import * as cloudtrail from '@aws-cdk/aws-cloudtrail';
import * as events from '@aws-cdk/aws-events';
import * as cdk from '@aws-cdk/core';
import * as sns from '@aws-cdk/aws-sns';
import * as subscriptions from '@aws-cdk/aws-sns-subscriptions';
import {ServicePrincipals} from 'cdk-constants';
import * as targets from '@aws-cdk/aws-events-targets';
import {createPythonLambda} from './common/lambda';
import * as iam from '@aws-cdk/aws-iam';

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
      resources: [trail.trailArn]
    }));
    rule.addTarget(new targets.LambdaFunction(lambdaCloudtrailLogging));
    rule.addTarget(new targets.SnsTopic(snsTopic));
  }
}