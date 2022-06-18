#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

# required environment variables
project_name    = ("PROJECT_NAME", os.getenv("PROJECT_NAME"))
vpc_id          = ("VPC_ID", os.getenv("VPC_ID"))
aws_region      = ("AWS_REGION", os.getenv("AWS_REGION"))
aws_account     = ("AWS_ACCOUNT", os.getenv("AWS_ACCOUNT"))

required_variables = [  project_name, 
                        aws_account, 
                        aws_region, 
                        vpc_id]

missing_vars = []
for var in required_variables:
    if not var[1]:
        missing_vars.append(var)
        

if not len(missing_vars) == 0:
    print('ERROR: Missing required environment variables:')
    for var in missing_vars:
        print(f' - {var[0]}')
    sys.exit(1)


stack_name = f'{project_name}-stack' 

cdk_env = cdk.Environment(account=aws_account, region=aws_region)

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env, project_name=project_name, vpc_id=vpc_id)

app.synth()
