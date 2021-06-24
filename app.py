#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from burnout_detector_unicorn_gym_13.burnout_detector_unicorn_gym_13_stack import BurnoutDetectorUnicornGym13Stack
from lexbot_custom_resource.cdk_lexbot_stack import CdkLexBotStack


app = core.App()
burnout_stack = BurnoutDetectorUnicornGym13Stack(app, "BurnoutDetectorUnicornGym13Stack")
CdkLexBotStack(app, "lexBurnout",burnout_stack.lambda_fulfillment_arn)

app.synth()
