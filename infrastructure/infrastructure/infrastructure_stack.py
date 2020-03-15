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

        # Monitoring system
        wf = Watchful(self, 'monitoring', alarm_email='747b13b7.groups.unsw.edu.au@apac.teams.ms')
        wf.watch_scope(self)

        # create cognito instance
        userpool = aws_cognito.UserPool(self, "myuserpool",
            user_pool_name="doctor-userpool"
        )

  # Lambda create doctors
        # doctor_create = aws_lambda.Function(self, "doctor_create",
        #                                runtime=aws_lambda.Runtime.PYTHON_3_7,
        #                                handler="doctor_create.main",
        #                                code=aws_lambda.Code.asset('./lambda'))

        #  # Lambda get doctor by ID
        # doctor_get = aws_lambda.Function(self, "doctor_get",
        #                                runtime=aws_lambda.Runtime.PYTHON_3_7,
        #                                handler="doctor_get.main",
        #                                code=aws_lambda.Code.asset('./lambda'))