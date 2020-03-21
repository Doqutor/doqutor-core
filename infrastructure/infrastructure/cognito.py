from aws_cdk import core, aws_lambda, aws_cognito, aws_apigateway

class Cognito:
    def __init__(self, stack: core.Stack, trigger: aws_lambda.Function):

        cognito_trigger = aws_cognito.UserPoolTriggers(post_confirmation=trigger)
        aws_apigateway.LambdaRestApi(stack, "api_cognito_doctors_create", handler=trigger)

        # create cognito instance attach ddb/cognito write lambda
        userpool = aws_cognito.UserPool(stack, "doc_userpool",
            user_pool_name="doctor-userpool",
            lambda_triggers=cognito_trigger,
        )

        # defining a userpool client
        aws_cognito.UserPoolClient(stack, 
            "doc_userpool_client",
            user_pool=userpool,
            user_pool_client_name="doctor-userpool-client"
        )

        # domain name for user pool
        aws_cognito.CfnUserPoolDomain(stack, "login", user_pool_id=userpool.user_pool_id, domain=stack.stack_name)