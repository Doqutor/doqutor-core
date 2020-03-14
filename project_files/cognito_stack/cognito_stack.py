from aws_cdk import (
    aws_cognito as cognito,
    core
)

class Cognito_Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str) -> None:
        super().__init__(scope, id)

        userpool = cognito.UserPool(self, "myuserpool",
            user_pool_name="doctor-userpool"
        )

        