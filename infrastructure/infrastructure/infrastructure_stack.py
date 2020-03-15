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

        # Lambda create
        function = aws_lambda.Function(self, "backend",
                                       runtime=aws_lambda.Runtime.PYTHON_3_7,
                                       handler="handler.main",
                                       code=aws_lambda.Code.asset('./lambda'))

        # IAM policy
        table.grant_read_write_data(function)
        function.add_environment("TABLE_NAME", table.table_name)

        # api gateway
        api = aws_apigateway.LambdaRestApi(self, "api", handler=function)

        # Monitoring system
        wf = Watchful(self, 'monitoring', alarm_email='747b13b7.groups.unsw.edu.au@apac.teams.ms')
        wf.watch_scope(self)

        # create cognito instance
        userpool = aws_cognito.UserPool(self, "myuserpool",
            user_pool_name="doctor-userpool"
        )
