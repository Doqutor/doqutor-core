from aws_cdk import core, aws_dynamodb, aws_lambda, aws_apigateway, aws_cognito
from cdk_watchful import Watchful
from dynamodb import DynamoDB
from lambdas import Lambdas
from cognito import Cognito

class InfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dynamodb = DynamoDB(self)
        self.lambdas = Lambdas(self, self.dynamodb)
        self.cognito = Cognito(self, self.lambdas.cognito_lambda)

        ###
        # Monitoring
        ###
        wf = Watchful(self, 'monitoring', alarm_email='747b13b7.groups.unsw.edu.au@apac.teams.ms')
        wf.watch_scope(self)