from aws_cdk import core, aws_dynamodb, aws_lambda, aws_apigateway, aws_cognito
from cdk_watchful import Watchful


class InfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # table create
        table = aws_dynamodb.Table(self, "doctors",
                                    partition_key=aws_dynamodb.Attribute(
                                    name="id",
                                    type=aws_dynamodb.AttributeType.STRING))

        # Create doctor lambda
        doctors_create = aws_lambda.Function(self, "doctors_create",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_create.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_create)
        doctors_create.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_create", handler=doctors_create)
        
        # Update doctor lambda
        doctors_update = aws_lambda.Function(self, "doctors_update",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_update.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_update)
        doctors_update.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_update", handler=doctors_update)

        # Get doctor lambda
        doctors_get = aws_lambda.Function(self, "doctors_get",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_get.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_get)
        doctors_get.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_get", handler=doctors_get)

        # List doctor lambda
        doctors_list = aws_lambda.Function(self, "doctors_list",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_list.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_list)
        doctors_list.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_list", handler=doctors_list)

        # Delete doctor lambda
        doctors_delete = aws_lambda.Function(self, "doctors_delete",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_delete.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_delete)
        doctors_delete.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_delete", handler=doctors_delete)


        # Cognito lambda (on successful creation of doctor in cognito, write to db)
        cognito_lambda = aws_lambda.Function(self, "cognito_trigger",
                                       runtime=aws_lambda.Runtime.PYTHON_3_7,
                                       handler="cognito.main",
                                       code=aws_lambda.Code.asset('./lambda')
        )
        table.grant_read_write_data(cognito_lambda)
        cognito_trigger = aws_cognito.UserPoolTriggers(post_confirmation=cognito_lambda)
        api = aws_apigateway.LambdaRestApi(self, "api_cognito_doctors_create", handler=cognito_lambda)


        # create cognito instance attach ddb/cognito write lambda
        userpool = aws_cognito.UserPool(self, "doc_userpool",
            user_pool_name="doctor-userpool",
            lambda_triggers=cognito_trigger,
        )

        # defining a userpool client
        userpool_client = aws_cognito.UserPoolClient(self, "doc_userpool_client", user_pool=userpool, user_pool_client_name="doctor-userpool-client")

        # Monitoring system
        wf = Watchful(self, 'monitoring', alarm_email='747b13b7.groups.unsw.edu.au@apac.teams.ms')
        wf.watch_scope(self)

        # Combined API attempt
        apiC = aws_apigateway.RestApi(self, "api_CRUD")
        doctors_list_integration = aws_apigateway.LambdaIntegration(doctors_list)
        doctors_create_integration = aws_apigateway.LambdaIntegration(doctors_create)
        doctors_get_integration = aws_apigateway.LambdaIntegration(doctors_get)
        doctors_delete_integration = aws_apigateway.LambdaIntegration(doctors_delete)
        doctors_update_integration = aws_apigateway.LambdaIntegration(doctors_update)

        apiC.root.add_method("GET", doctors_list_integration)
        apiC.root.add_method("POST", doctors_create_integration)
        doctor_id = apiC.root.add_resource("{id}")
        doctor_id.add_method("GET", doctors_get_integration)
        doctor_id.add_method("PUT", doctors_update_integration)
        doctor_id.add_method("DELETE", doctors_delete_integration)
