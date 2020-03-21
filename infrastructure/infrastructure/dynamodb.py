from aws_cdk import core, aws_dynamodb

class DynamoDB:
    def __init__(self, stack: core.Stack):
        self.doctors = aws_dynamodb.Table(stack, "doctors",
            partition_key=aws_dynamodb.Attribute(
            name="id",
            type=aws_dynamodb.AttributeType.STRING))
