#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.classes import EC2OS, EC2Instance, WindowsEC2Instance, LinuxEC2Instance
from cdk.deploy_ec2linux import DeployEc2LinuxStack
from cdk.deploy_ec2windows import DeployEc2WindowsStack
from cdk.functions import get_env_vars

# required environment variables
env_vars = get_env_vars()

app = cdk.App()

if env_vars.ec2_os == EC2OS.LINUX:
    stack_name = f"{env_vars.project_name}-linux-stack"
    ec2_data = EC2Instance(
        os_type=LinuxEC2Instance(),
        key_name=env_vars.key_name,
        vpc_id=env_vars.vpc_id
    )

    DeployEc2LinuxStack(
        app,
        stack_name,
        env=cdk.Environment(account=env_vars.aws_account, region=env_vars.aws_region),
        project_name=env_vars.project_name,
        vpc_id=env_vars.vpc_id,
        termination_protection=True,
    )


elif env_vars.ec2_os == EC2OS.WINDOWS:
    stack_name = f"{env_vars.project_name}-windows-stack"
    ec2_data = EC2Instance(
        os_type=WindowsEC2Instance(), 
        key_name=env_vars.key_name, 
        vpc_id=env_vars.vpc_id
    )

    DeployEc2WindowsStack(
        app,
        stack_name,
        env=cdk.Environment(account=env_vars.aws_account, region=env_vars.aws_region),
        ec2_data=ec2_data,
    )


app.synth()
