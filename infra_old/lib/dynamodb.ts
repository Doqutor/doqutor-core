import * as dynamodb from '@aws-cdk/aws-dynamodb';
import { Stack } from '@aws-cdk/core';

export default function(stack: Stack) {
  const doctors = new dynamodb.Table(stack, 'doctors', {
    partitionKey: {name: 'id', type: dynamodb.AttributeType.STRING },
    billingMode: dynamodb.BillingMode.PROVISIONED
  });

  const patients = new dynamodb.Table(stack, 'patients', {
    partitionKey: {name: 'id', type: dynamodb.AttributeType.STRING },
    billingMode: dynamodb.BillingMode.PROVISIONED
  });

  return { doctors, patients };
}
