#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

# Needs to be fixed to deploy more than 1 EC2 instance if we want for testing!
# Currently BRRRROOOOOOKEEEEEEN
# print("===================================")
# project_name = os.getenv("PROJECT_NAME")
# if project_name == "":
#     print('PROJECT_NAME not set, exiting...')
#     sys.exit(1)
project_name = os.getenv("PROJECT_NAME")

if not project_name:
    print('PROJECT_NAME not set, using cdk-deploy-ec2.')
    project_name = "cdk-deploy-ec2"

stack_name = f'{project_name}-stack' 

cdk_env = cdk.Environment(account=os.getenv('AWS_ACCOUNT'), region=os.getenv('AWS_REGION'))

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env, word="dfghdfghdfgh")

app.synth()
