
# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

import uuid
import json
import boto3

from aws_cdk import (
    core as cdk, 
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    custom_resources as cr
)


from aws_cdk.core import CustomResource


class CdkLexBotStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, lambda_arn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs, )

        # The code that defines your stack goes here

        on_event_es = _lambda.Function(
            self, "burnout_bot_event", runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler", timeout=cdk.Duration.seconds(300),
            memory_size=1024, code=_lambda.Code.asset("./lexbot_custom_resource/provider"),
            description='[BURNOUT] Lexbot resource provider',
            environment={
                'BOT_FULFILLMENT_LAMBDA_ARN': lambda_arn, 
                'BOT_NAME': 'BURNOUT_DETECTOR',
                'BOT_JSON_FILE': 'bot_definitions/burnout_detector.json'}
            )


        on_event_es.add_to_role_policy(iam.PolicyStatement(actions=["lex:*"],resources=['*']))

        my_provider_es = cr.Provider(self, "lex_provider_burnout",on_event_handler=on_event_es, log_retention=logs.RetentionDays.ONE_DAY)

        CustomResource(self, "burnout_lex_bot", service_token=my_provider_es.service_token)
