from aws_cdk import core, aws_apigateway
from lambdas import Lambdas

class Api:
    def __init__(self, stack: core.Stack, lambdas: Lambdas):
        # Combined API attempt
        self.gateway = aws_apigateway.RestApi(stack, "api_CRUD")

        doctors = self.gateway.root.add_resource("doctors")
        doctors.add_cors_preflight(
            allow_origins=aws_apigateway.Cors.ALL_ORIGINS, # TODO: change allowed origin to specific
            allow_methods=["GET", "POST"]
        )
        doctors.add_method("GET", aws_apigateway.LambdaIntegration(lambdas.doctors_list))
        doctors.add_method("POST", aws_apigateway.LambdaIntegration(lambdas.doctors_create))
        doctor_id = doctors.add_resource("{id}")
        doctor_id.add_cors_preflight(
            allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
            allow_methods=["GET", "PUT", "DELETE"]
        )
        doctor_id.add_method("GET", aws_apigateway.LambdaIntegration(lambdas.doctors_get))
        doctor_id.add_method("PUT", aws_apigateway.LambdaIntegration(lambdas.doctors_update))
        doctor_id.add_method("DELETE", aws_apigateway.LambdaIntegration(lambdas.doctors_delete))

        patients = self.gateway.root.add_resource("patients")
        patients.add_method("GET")
        patients.add_method("POST")
        patient_id = patients.add_resource("{id}")
        patient_id.add_method("GET")
        patient_id.add_method("PUT")
        patient_id.add_method("DELETE")