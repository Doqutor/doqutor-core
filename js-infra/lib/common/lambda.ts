import * as cdk from '@aws-cdk/core'; 
import * as lambda from '@aws-cdk/aws-lambda';


export function createPythonLambda(stack: cdk.Stack, folder: string, name: string): lambda.Function {
    const fn = new lambda.Function(stack, name, {
        runtime: lambda.Runtime.PYTHON_3_7,
        handler: `${name}.main`,
        code: new lambda.AssetCode(`./lambda/${folder}/`)
    });

    return fn;
}

export function createTypeScriptLambda(stack: cdk.Stack, folder: string, name: string): lambda.Function {
    const fn = new lambda.Function(stack, name, {
        runtime: lambda.Runtime.NODEJS_12_X,
        handler: `${name}.handler`,
        code: new lambda.AssetCode(`./lambda/${folder}`)
    });

    return fn;
}