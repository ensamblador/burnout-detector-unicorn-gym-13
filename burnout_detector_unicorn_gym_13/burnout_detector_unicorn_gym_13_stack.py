from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core
import aws_cdk.aws_dynamodb as dynamodb


class BurnoutDetectorUnicornGym13Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table_employee = dynamodb.Table(self, "Employee",
            table_name='Employee',
            partition_key=dynamodb.Attribute(name="EmployeeID", type=dynamodb.AttributeType.STRING)
        )
        table_respuestas = dynamodb.Table(self, "EmployeeResponses",
            table_name='EmployeeResponses',
            partition_key=dynamodb.Attribute(name="EmployeeID", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="ResponseDate", type=dynamodb.AttributeType.STRING)

        )
        # The code that defines your stack goes here
