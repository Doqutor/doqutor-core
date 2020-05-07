import * as cdk from "@aws-cdk/core";
import * as apigateway from "@aws-cdk/aws-apigateway";

export enum Models {
  doctor = "doctorModel",
  patient = "patientModel",
}

const models: { [key: string]: { description: string; schema: any } } = {};
models[Models.doctor] = {
  description: "Model representing a doctor",
  schema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        minLength: 1,
        maxLength: 50,
      },
      email: {
        type: "string",
        format: "email",
      },
      phone_number: {
        type: "string",
        pattern: "^\\+[0-9]+$",
        maxLength: 16,
      },
      age: {
        type: "number",
      },
      is_active: {
        type: "boolean",
      },
    },
    required: ["name", "email", "phone_number", "age"],
    additionalProperties: false,
  },
};

models[Models.patient] = {
  description: "Model representing a patient",
  schema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        minLength: 1,
        maxLength: 50,
      },
      email: {
        type: "string",
        format: "email",
      },
      phone_number: {
        type: "string",
        pattern: "^\\+[0-9]+$",
        maxLength: 16,
      },
      age: {
        type: "number",
      },
      is_active: {
        type: "boolean",
      },
      insurance_id: {
        type: "string",
        minLength: 1,
        maxLength: 50,
      },
    },
    required: ["name", "email", "phone_number", "age", "insurance_id"],
    additionalProperties: false,
  },
};

export default function getSchemas(
  scope: cdk.Stack,
  restApi: apigateway.RestApi
): { [key: string]: apigateway.Model } {
  // I now know what a closure is zzzz
  let _models: { [key: string]: apigateway.Model } = {};
  for (const m in models) {
    _models[m] = new apigateway.Model(scope, m, {
      restApi: restApi,
      schema: models[m].schema,
      description: models[m].description,
      modelName: m,
    });
  }

  return _models;
}
