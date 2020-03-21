from aws_cdk import core
from cdk_watchful import Watchful
from dynamodb import DynamoDB
from lambdas import Lambdas
from cognito import Cognito
from api_gateway import Api

class InfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.dynamodb = DynamoDB(self)
        self.lambdas = Lambdas(self, self.dynamodb)
        self.cognito = Cognito(self, self.lambdas.cognito_lambda)
        self.api = Api(self, self.lambdas)

        ###
        # Monitoring
        ###
        wf = Watchful(self, 'monitoring', alarm_email='747b13b7.groups.unsw.edu.au@apac.teams.ms')
        wf.watch_scope(self)