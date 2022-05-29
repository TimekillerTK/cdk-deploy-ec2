# Deploy EC2 with CDK Python
Simple AWS CDK Python project to deploy an free tier `t2.micro` EC2 Instance with docker + some diagnostic tools, mostly for myself.

To use this, you can set up a shell script file that will export all env vars for you (or use whatever method you want to set the env vars):
```sh
#!/bin/bash
export PROJECT_NAME="my-ec2-test" # Name of project, inherited by stack name and stack resources
export AWS_ACCOUNT="123456789" # AWS account where the instance will be deployed
export AWS_REGION="us-east-1"  # Region where the instance will be deployed
export VPC_ID="vpc-xxxxxxxxxxxx" # VPC
export AMI_NAME="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2" # Amazon Linux 2 (example)
export ALLOW_PORTS="22 80 443" # list of inbound allowed ports to be allowed on SG
export GLOBAL_ALLOW_PORTS="80" # list of inbound ports which should be opened up to 0.0.0.0/0
export KEY_NAME="whatever" # Keypair name which you'll use to connect to the EC2 instance
export USER_DATA="userdata" # path to userdata
export BUCKET_NAME="xxxxyyyxxx" # name of S3 bucket EC2 instance will have access to
```
By default it will open up an inbound ssh (TCP/22) firewall rule, allowing the EC2 instance to be only reachable via your local public IP Address.

Additional inbound SG rules are going to be added if the `ALLOWED_PORTS` environment variable is set with a space delimited ports:
* `export ALLOWED_PORTS="22 80 443"` (example)

It will also spit out IP Address of the instance being created:
```sh
✨  Deployment time: 34.9s

Outputs:
DeployEc2Stack.MyInstanceIp = xxx.xxx.xxx.xxx
Stack ARN:
arn:aws:cloudformation:${AWS_REGION}:${AWS_ACCOUNT}:stack/DeployEc2Stack/${RANDOMUUID}
```

Will also copy all contents of a specified S3 bucket in `/cdk-deploy-ec2/s3bucketname` to `/home/ec2-user/docker` on the deployed instance.

> Make sure to set an SSM parameter `/cdk-deploy-ec2/s3bucketname` with the value being the same as the `BUCKET_NAME` environment variable set above!

# Known Issues & Todo
* on first connection user doesn't have access to docker - restarting ssh session fixes this (prolly still not ready)
* when using certbot to use HTTP-01 certificate request, firewall needs to allow http connections from `0.0.0.0/0` otherwise it will fail
* keypair should be dynamically created if it does not exist - should also not be deleted with stack when stack is deleted.
* tag all resources in a uniform way