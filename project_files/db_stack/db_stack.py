from aws_cdk import (
    aws_dynamodb as db,
    core
)

class Database_Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # initalising that database
        doc_table = db.Table(self, "mapping-table",
                partition_key=db.Attribute(name="doctor_id", type=db.AttributeType.STRING)
        )

