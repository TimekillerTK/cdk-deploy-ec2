#!/usr/bin/env python3
import os
import sys
import aws_cdk as cdk
from cdk.deploy_ec2 import DeployEc2Stack

#TODO: Move this check to a function, cleaner that way
# check for project name being set
project_name_env = os.getenv("PROJECT_NAME")
if not project_name_env:
    project_name = ("PROJECT_NAME", "cdk-deploy-ec2")
else:
    project_name = ("PROJECT_NAME", project_name_env)

# required environment variables
vpc_id          = ("VPC_ID", os.getenv("VPC_ID"))
aws_region      = ("AWS_REGION", os.getenv("AWS_REGION"))
aws_account     = ("AWS_ACCOUNT", os.getenv("AWS_ACCOUNT"))

required_variables = [  aws_account, 
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


stack_name = f'{project_name[1]}-stack' 

cdk_env = cdk.Environment(account=aws_account[1], region=aws_region[1])

app = cdk.App()
DeployEc2Stack(app, stack_name, env=cdk_env, project_name=project_name[1], vpc_id=vpc_id[1])

app.synth()
