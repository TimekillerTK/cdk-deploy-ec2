# Deploy EC2 with CDK Python
Simple AWS CDK Python project to deploy an free tier `t2.micro` EC2 Instance.

To use this, you can set up a shell script file that will export all env vars for you (or use whatever method you want to set the env vars):
```sh
#!/bin/bash
export AWS_ACCOUNT="123456789" # AWS account where the instance will be deployed
export AWS_REGION="us-east-1"  # Region where the instance will be deployed
export VPC_ID="vpc-xxxxxxxxxxxx" # VPC
export AMI_NAME="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2" # Amazon Linux 2 (example)
export KEY_NAME="whatever" # Keypair name which you'll use to connect to the EC2 instance
```

By default it will open up a ssh firewall rule to your local public IP Address.

Will spit out IP Address of the instance being created:
```sh
✨  Deployment time: 34.9s

Outputs:
DeployEc2Stack.MyInstanceIp = xxx.xxx.xxx.xxx
Stack ARN:
arn:aws:cloudformation:${AWS_REGION}:${AWS_ACCOUNT}:stack/DeployEc2Stack/${RANDOMUUID}
```