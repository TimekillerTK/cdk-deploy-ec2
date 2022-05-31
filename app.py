#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

project_name = os.getenv("PROJECT_NAME")
if project_name == "":
    print('PROJECT_NAME not set, exiting...')
    sys.exit(1)

stack_name = f'{project_name}-stack' 

cdk_env = cdk.Environment(account=os.getenv('AWS_ACCOUNT'), region=os.getenv('AWS_REGION'))

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env)

app.synth()
