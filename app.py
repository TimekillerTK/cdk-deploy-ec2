#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

project_name = os.getenv("PROJECT_NAME")
if not project_name:
    print('PROJECT_NAME not set, using cdk-deploy-ec2 by default.')
    project_name = "cdk-deploy-ec2"

aws_account = os.getenv("AWS_ACCOUNT") 
if not aws_account:
    print('AWS_ACCOUNT not set, exiting...')
    sys.exit(1)

aws_region = os.getenv("AWS_REGION")
if not aws_region:
    print('AWS_REGION not set, exiting...')
    sys.exit(1)

stack_name = f'{project_name}-stack' 

cdk_env = cdk.Environment(account=aws_account, region=aws_region)

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env, project_name=project_name)

app.synth()
