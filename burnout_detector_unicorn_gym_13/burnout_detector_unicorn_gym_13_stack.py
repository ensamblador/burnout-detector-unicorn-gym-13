from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    core,
    aws_lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_dynamodb as dynamodb)


INSTANCE_ID  = '4061ae9c-11a9-468c-a298-318842091902'
CONTACT_FLOW_ID = '6f023411-9715-4936-ad58-ee8367581b5b'
SOURCE_PHONE= '+56800914991'



class BurnoutDetectorUnicornGym13Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table_employee = dynamodb.Table(self, "Employee",
            table_name='Employee', 
            partition_key=dynamodb.Attribute(name="EmployeeID", type=dynamodb.AttributeType.STRING)
        )

        ''' 
        ejemplo de item
        {
            "EmployeeID": "82a9b509-0a9b-4ed4-adf6-3ae8846b747d",
            "FirstName": "Enrique",
            "LastName": "Rodriguez",
            "CallWindowStart": "2021-05-07T00:05:00+00:00",
            "CallWindowEnd": "2021-05-07T00:05:00+00:00",
            "Calling": false,
            "Completed": false,
            "PhoneNumber": "+56974769647"
        }
        '''
        table_respuestas = dynamodb.Table(self, "EmployeeResponses",
            table_name='EmployeeResponses',
            partition_key=dynamodb.Attribute(name="EmployeeID", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="ResponseDate", type=dynamodb.AttributeType.STRING)
        )
        
        lambda_call = aws_lambda.Function (self, "call", memory_size=256, 
            timeout= core.Duration.seconds(10),
            runtime=aws_lambda.Runtime.PYTHON_3_8, 
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.asset("./lambdas/call"),
            environment={
                'TABLE_NAME': table_employee.table_name,
                'INSTANCE_ID': INSTANCE_ID,
                'CONTACT_FLOW_ID': CONTACT_FLOW_ID,
                'SOURCE_PHONE': SOURCE_PHONE
                
            }
        )

        lambda_call.add_to_role_policy(iam.PolicyStatement(
            actions=["Connect:StartOutboundVoiceContact"],resources=["*"]))

        table_employee.grant_read_write_data(lambda_call)


        event_rule = events.Rule(self, "burnout-cada-5-min", schedule=events.Schedule.cron(minute='*/5'))
        event_rule.add_target(targets.LambdaFunction(lambda_call))

        # The code that defines your stack goes here

        lambda_fulfillment = aws_lambda.Function (self, "fulfillment", memory_size=256, 
            timeout= core.Duration.seconds(10),
            runtime=aws_lambda.Runtime.PYTHON_3_8, 
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.asset("./lambdas/fulfillment"),
            environment={
                'DynamoDB_Table': table_respuestas.table_name,
                
            }
        )
        table_respuestas.grant_read_write_data(lambda_fulfillment)

        self.lambda_fulfillment_arn = lambda_fulfillment.function_arn