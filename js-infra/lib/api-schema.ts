import * as cdk from '@aws-cdk/core';
import * as apigateway from '@aws-cdk/aws-apigateway';

export enum Models {
    doctor = 'doctorModel',
}

const models: {[key: string]: {description: string, schema: any}} = {};
models[Models.doctor] = {
    description: 'Model representing a doctor',
    schema: {
        type: 'object',
        properties: {
            given_name: {
                type: 'string',
                minLength: 1,
                maxLength: 50
            },
            family_name: {
                type: 'string',
                minLength: 1,
                maxLength: 50
            },
            email: {
                type: 'string',
                format: 'email'
            },
            phone_number: {
                type: 'string',
                pattern: '^\\+[0-9]+$',
                maxLength: 16
            },
            birth_date: {
                type: 'string',
                pattern: '^[0-9]{4}-[0-1][0-9]-[0-3][0-9]$'
            },
            is_active: {
                type: 'boolean'
            }
        },
        required: ['given_name', 'family_name', 'email', 'phone_number', 'birth_date'],
        additionalProperties: false
    }
};

export default function getSchemas(scope: cdk.Stack, restApi: apigateway.RestApi): {[key: string]: apigateway.Model} {
    // I now know what a closure is zzzz
    let _models: {[key: string]: apigateway.Model} = {};
    for (const m in models) {
        _models[m] = new apigateway.Model(scope, m, {
            restApi: restApi,
            schema: models[m].schema,
            description: models[m].description,
            modelName: m
        });
    }

    return _models;
}