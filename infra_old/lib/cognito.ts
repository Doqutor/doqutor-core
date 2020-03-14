import {CfnUserPool, UserPoolAttribute} from '@aws-cdk/aws-cognito';
import { Stack } from '@aws-cdk/core';

export default function(stack: Stack) {
  const pool = new CfnUserPool(stack, 'users', {
    userPoolName: 'doqutorue-users',
    adminCreateUserConfig: {
      allowAdminCreateUserOnly: false
    },
    schema: [
      {
          attributeDataType: 'String',
          name: UserPoolAttribute.EMAIL,
          mutable: true,
          required: true
      }
  ]
  });
  return pool;
}
