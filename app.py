#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

stack_name = f'{os.getenv("PROJECT_NAME")}-stack' 

cdk_env = cdk.Environment(account=os.getenv('AWS_ACCOUNT'), region=os.getenv('AWS_REGION'))

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env)

app.synth()
