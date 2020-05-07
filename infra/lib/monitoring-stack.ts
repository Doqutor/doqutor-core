import * as cloudtrail from "@aws-cdk/aws-cloudtrail";
import * as events from "@aws-cdk/aws-events";
import * as cdk from "@aws-cdk/core";
import * as sns from "@aws-cdk/aws-sns";
import * as subscriptions from "@aws-cdk/aws-sns-subscriptions";
import { ServicePrincipals } from "cdk-constants";
import * as targets from "@aws-cdk/aws-events-targets";
import { createPythonLambda } from "./common/lambda";
import * as iam from "@aws-cdk/aws-iam";
import * as cloudwatch from "@aws-cdk/aws-cloudwatch";
import * as cw_actions from "@aws-cdk/aws-cloudwatch-actions";
import { Duration } from "@aws-cdk/core";
import * as wafv2 from "@aws-cdk/aws-wafv2";
import { Config } from "../bin/infra";

export class MonitoringStack extends cdk.Stack {
  constructor(
    scope: cdk.Construct,
    id: string,
    config: Config,
    props?: cdk.StackProps
  ) {
    super(scope, id, props);

    /*
     * CloudTrail and sns
     */
    const trail = new cloudtrail.Trail(this, "cloudtrail", {
      sendToCloudWatchLogs: true,
    });
    
    const snsTopic = new sns.Topic(this, "CloudtrailAlert", {
      displayName: "Cloudtrail Alert",
    });
    const user = new iam.User(this, "testUser");
    user.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName("AdministratorAccess")
    );
    const emailSubscription = new subscriptions.EmailSubscription(config.email);
    snsTopic.addSubscription(emailSubscription);

    /*
     * Events for detecting that cloudtrail was turned off
     */
    const eventPattern: events.EventPattern = {
      source: ["aws.cloudtrail"],
      detail: {
        eventSource: [ServicePrincipals.CLOUD_TRAIL],
        eventName: [
          "StopLogging",
          "StartLogging",
          "DeleteTrail",
          "CreateTrail",
        ],
      },
    };
    const rule = new events.Rule(this, "ruleFromCDKForStoppedLogging", {
      eventPattern: eventPattern,
      description: "If CloudTrail logging is stopped this event will fire",
    });
    const lambdaCloudtrailLogging = createPythonLambda(
      this,
      "util",
      "cloudtrail_restartlog"
    );
    lambdaCloudtrailLogging.addEnvironment("TRAIL_ARN", trail.trailArn);
    lambdaCloudtrailLogging.addEnvironment("SNS_ARN", snsTopic.topicArn);
    snsTopic.grantPublish(lambdaCloudtrailLogging);

    // allow lambda to access cloudtrail
    lambdaCloudtrailLogging.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["cloudtrail:StartLogging"],
        effect: iam.Effect.ALLOW,
        resources: ["*"],
      })
    );

    // allow lambda to attach policies to user
    lambdaCloudtrailLogging.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["iam:AttachUserPolicy"],
        effect: iam.Effect.ALLOW,
        resources: ["*"],
        conditions: {
          ArnEquals: { "iam:PolicyARN": "arn:aws:iam::aws:policy/AWSDenyAll" },
        },
      })
    );

    rule.addTarget(new targets.LambdaFunction(lambdaCloudtrailLogging));
    rule.addTarget(new targets.SnsTopic(snsTopic));

    

    /*
     * CloudWatch rulesets here
     */

    const stackName = this.stackName.replace("monitoring", "infrastructure"); // to correctly refrence other stack
    const snsTopicCw = new sns.Topic(this, "CloudwatchAlert", {
      displayName: "Cloudwatch Alert",
    });
    snsTopicCw.addSubscription(emailSubscription);

    const ddbMetric = new cloudwatch.Metric({
      metricName: "ConsumedReadCapacityUnits",
      namespace: "AWS/DynamoDB",
      statistic: "Sum",
      dimensions: { TableName: cdk.Fn.importValue(stackName + "-DoctorTable") },
    });
    const ddbExcessReadAlarmDoc = new cloudwatch.Alarm(
      this,
      "ddbExcessReadAlarmDoc",
      {
        metric: ddbMetric,
        threshold: 1200,
        period: Duration.seconds(60),
        evaluationPeriods: 1,
        datapointsToAlarm: 1,
      }
    );

    const ddbMetricPat = new cloudwatch.Metric({
      metricName: "ConsumedReadCapacityUnits",
      namespace: "AWS/DynamoDB",
      statistic: "Sum",
      dimensions: {
        TableName: cdk.Fn.importValue(stackName + "-PatientTable"),
      },
    });
    const ddbExcessReadAlarmPat = new cloudwatch.Alarm(
      this,
      "ddbExcessReadAlarmPat",
      {
        metric: ddbMetricPat,
        threshold: 1200,
        period: Duration.seconds(60),
        evaluationPeriods: 1,
        datapointsToAlarm: 1,
      }
    );

    // binding sns topic to cloudwatch alarm
    ddbExcessReadAlarmDoc.addAlarmAction(new cw_actions.SnsAction(snsTopicCw));
    ddbExcessReadAlarmPat.addAlarmAction(new cw_actions.SnsAction(snsTopicCw));



    /*
     * Events for detecting that s3 was tampered with
     */

    trail.addS3EventSelector(
      [
        cdk.Fn.join("", [
          "arn:aws:s3:::",
          cdk.Fn.importValue("doqutore-frontend-S3Bucket"),
          "/",
        ]),
      ],
      {
        readWriteType: cloudtrail.ReadWriteType.WRITE_ONLY,
      }
    );
    
    const frontendPattern: events.EventPattern = {
      source: ["aws.s3"],
      detail: {
        eventSource: [ServicePrincipals.S3],
        eventName: ["DeleteObject", "PutObject"],
        requestParameters: {
          bucketName: [
            cdk.Fn.importValue(config.prefix + "-frontend-S3Bucket"),
          ],
        },
      },
    };

    const frontendSnsTopic = new sns.Topic(this, "FrontendAlert", {
      displayName: "Frontend Alert",
    });
    frontendSnsTopic.addSubscription(emailSubscription);

    const frontendRule = new events.Rule(this, "s3Modified", {
      eventPattern: frontendPattern,
      description:
        "If the frontend S3 bucket is modified then this event will fire",
    });

    const lambdaFrontendCloudtrailLogging = createPythonLambda(
      this,
      "util",
      "cloudtrail_retrigger_pipeline",
      1
    );
    lambdaFrontendCloudtrailLogging.addEnvironment(
      "SNS_ARN",
      frontendSnsTopic.topicArn
    );
    lambdaFrontendCloudtrailLogging.addEnvironment(
      "GITHUB_KEY",
      config.githubKey
    );
    frontendSnsTopic.grantPublish(lambdaFrontendCloudtrailLogging);

    frontendRule.addTarget(
      new targets.LambdaFunction(lambdaFrontendCloudtrailLogging)
    );
   
    // WAF
    // only allow 128 requests per 5 minutes, a pretty generous limit for a small practice
    // assuming that a clinic is located at the same ip address
    const wafAPI = new wafv2.CfnWebACL(this, "waf-api", {
      defaultAction: {
        allow: {},
      },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "waf-apigateway",
        sampledRequestsEnabled: true,
      },
      scope: "REGIONAL",
      rules: [
        {
          name: "AWS-AWSManagedRulesAmazonIpReputationList",
          priority: 0,
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesAmazonIpReputationList",
            },
          },
          overrideAction: {
            none: {},
          },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: "waf-apigateway-ipreputation",
          },
        },
        {
          name: "AWS-AWSManagedRulesCommonRuleSet",
          priority: 1,
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesCommonRuleSet",
            },
          },
          overrideAction: {
            none: {},
          },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: "waf-apigateway-commonattacks",
          },
        },
        {
          name: "ratelimit",
          priority: 2,
          statement: {
            rateBasedStatement: {
              limit: 128,
              aggregateKeyType: "IP",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "waf-apigateway-ratelimit",
            sampledRequestsEnabled: true,
          },
          action: {
            block: {},
          },
        },
      ],
    });
    new wafv2.CfnWebACLAssociation(this, "waf-assoc-apigateway", {
      resourceArn: `arn:aws:apigateway:${
        this.region
      }::/restapis/${cdk.Fn.importValue(
        stackName + "-APIGateway"
      )}/stages/prod`,
      webAclArn: wafAPI.attrArn,
    });

    // grab cloudwatch metric and crate alarm
    const wafMetric = new cloudwatch.Metric({
      metricName: "BlockedRequests",
      namespace: "AWS/WAFV2",
      statistic: "Sum",
      dimensions: {
        Rule: "waf-apigateway-ratelimit",
        WebACL: cdk.Fn.select(
          0,
          cdk.Fn.split("|", cdk.Fn.ref(wafAPI.logicalId))
        ),
        Region: "ap-southeast-2",
      },
    });

    const wafAlarm = new cloudwatch.Alarm(
      this,
      "waf-apigateway-ratelimit-breached",
      {
        metric: wafMetric,
        threshold: 128,
        period: Duration.seconds(60),
        evaluationPeriods: 1,
        datapointsToAlarm: 1,
      }
    );
    const snsTopicWAF = new sns.Topic(this, "WAFAlert", {
      displayName: "WAF Alert",
    });
    snsTopicWAF.addSubscription(emailSubscription);
    wafAlarm.addAlarmAction(new cw_actions.SnsAction(snsTopicWAF));
  }
}
