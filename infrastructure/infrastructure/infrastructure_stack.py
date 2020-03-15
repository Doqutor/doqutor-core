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

        # Get doctor lambda
        doctors_get = aws_lambda.Function(self, "doctors_get",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        handler="doctors_get.main",
                                        code=aws_lambda.Code.asset('./lambda'))

        table.grant_read_write_data(doctors_get)
        doctors_get.add_environment("TABLE_NAME", table.table_name)
        api = aws_apigateway.LambdaRestApi(self, "api_doctors_get", handler=doctors_get)

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

        # Cognito lambda (on successful creation of doctor in cognito, write to db)
        cognito_lambda = aws_lambda.Function(self, "cognito_trigger",
                                       runtime=aws_lambda.Runtime.PYTHON_3_7,
                                       handler="cognito.main",
                                       code=aws_lambda.Code.asset('./lambda')
        )
        cognito_trigger = aws_cognito.UserPoolTriggers(post_confirmation=cognito_lambda)


        # create cognito instance attach ddb/cognito write lambda
        userpool = aws_cognito.UserPool(self, "myuserpool",
            user_pool_name="doctor-userpool",
            lambda_triggers=cognito_trigger,
        )

