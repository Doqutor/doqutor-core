from aws_cdk import core, aws_lambda, aws_apigateway
from dynamodb import DynamoDB

class Lambdas:
    def __init__(self, stack: core.Stack, dynamodb: DynamoDB):
        self.doctors_create = aws_lambda.Function(stack, "doctors_create",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="doctors_create.main",
            code=aws_lambda.Code.asset('./lambda'))

        dynamodb.doctors.grant_read_write_data(self.doctors_create)
        self.doctors_create.add_environment("TABLE_NAME", dynamodb.doctors.table_name)
        aws_apigateway.LambdaRestApi(stack, "api_doctors_create", handler=self.doctors_create)
        


        # Update doctor lambda
        self.doctors_update = aws_lambda.Function(stack, "doctors_update",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="doctors_update.main",
            code=aws_lambda.Code.asset('./lambda'))

        dynamodb.doctors.grant_read_write_data(self.doctors_update)
        self.doctors_update.add_environment("TABLE_NAME", dynamodb.doctors.table_name)
        aws_apigateway.LambdaRestApi(stack, "api_doctors_update", handler=self.doctors_update)



        # Get doctor lambda
        self.doctors_get = aws_lambda.Function(stack, "doctors_get",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="doctors_get.main",
            code=aws_lambda.Code.asset('./lambda'))

        dynamodb.doctors.grant_read_write_data(self.doctors_get)
        self.doctors_get.add_environment("TABLE_NAME", dynamodb.doctors.table_name)
        aws_apigateway.LambdaRestApi(stack, "api_doctors_get", handler=self.doctors_get)



        # List doctor lambda
        self.doctors_list = aws_lambda.Function(stack, "doctors_list",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="doctors_list.main",
            code=aws_lambda.Code.asset('./lambda'))

        dynamodb.doctors.grant_read_write_data(self.doctors_list)
        self.doctors_list.add_environment("TABLE_NAME", dynamodb.doctors.table_name)
        aws_apigateway.LambdaRestApi(stack, "api_doctors_list", handler=self.doctors_list)



        # Delete doctor lambda
        self.doctors_delete = aws_lambda.Function(stack, "doctors_delete",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="doctors_delete.main",
            code=aws_lambda.Code.asset('./lambda'))

        dynamodb.doctors.grant_read_write_data(self.doctors_delete)
        self.doctors_delete.add_environment("TABLE_NAME", dynamodb.doctors.table_name)
        aws_apigateway.LambdaRestApi(stack, "api_doctors_delete", handler=self.doctors_delete)



        # lambda for interfacing with cognito
        self.cognito_lambda = aws_lambda.Function(stack, "cognito_trigger",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="cognito.main",
            code=aws_lambda.Code.asset('./lambda')
        )
        dynamodb.doctors.grant_read_write_data(self.cognito_lambda)