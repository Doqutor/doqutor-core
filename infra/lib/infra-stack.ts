import * as cdk from '@aws-cdk/core';
import dynamodb from './dynamodb';
import cognito from './cognito';

export class InfraStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    cognito(this);
    dynamodb(this);
  }
}
