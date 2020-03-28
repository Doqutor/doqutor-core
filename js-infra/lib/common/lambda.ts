import * as cdk from '@aws-cdk/core'; 
import * as lambda from '@aws-cdk/aws-lambda';
import {AssetCode} from "@aws-cdk/aws-lambda";


export function createPythonLambda(stack: cdk.Stack, name: string): lambda.Function {
    const fn = new lambda.Function(stack, name, {
        runtime: lambda.Runtime.PYTHON_3_7,
        handler: `${name}.main`,
        code: lambda.Code.asset('./lambda')
    });

    return fn;
}

export function createTypeScriptLambda(stack: cdk.Stack, name: string): lambda.Function {
    const fn = new lambda.Function(stack, name, {
        runtime: lambda.Runtime.NODEJS_12_X,
        handler: `${name}.handler`,
        code: new AssetCode('./lambda')
    });

    return fn;
}