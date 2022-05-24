import os
import sys
import requests
from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2,
    aws_iam
)
from constructs import Construct

class DeployEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.instance_name = 'my-ec2-instance'
        self.instance_type = 't2.micro'
        self.ami_name      = os.getenv("AMI_NAME")
        self.vpc_name      = os.getenv("VPC_ID")
        self.key_name      = os.getenv("KEY_NAME")
        self.file_path     = os.getenv("USER_DATA")
        self.bucket_name   = os.getenv("BUCKET_NAME")


        print(f'Importing User Data...')
        with open(self.file_path, "r") as file:
            shell_script = file.read()
            
        print(f'USER DATA:\n{shell_script}\n')

        user_data = aws_ec2.UserData.for_linux()
        user_data.add_commands(shell_script)
        print(user_data)
        if not user_data:
            print('Failed setting user data...')
            sys.exit(1)

        print(f'Checking name of key pair...')
        if not self.key_name:
            print('Failed getting key pair. Not set?')
            sys.exit(1)

        print(f'Looking up local public IP...')
        local_ip = (requests.get('http://icanhazip.com')).text.split()[0]
        print(f'--> Local IP: {local_ip}')
        if not local_ip:
            print(f'Failed getting local public IP ')
            sys.exit(1)

        print(f'Creating Inline Policy for access to S3 Bucket')
        inline_policy = aws_iam.PolicyDocument(
            statements=[aws_iam.PolicyStatement(
                actions=["s3:PutObject","s3:GetObjectAcl","s3:GetObject","s3:ListBucket","s3:DeleteObject","s3:PutObjectAcl"],
                resources=[f"arn:aws:s3:::{self.bucket_name}"]
            )])
        if not inline_policy:
            print('Failed setting inline policy')
            sys.exit(1)

        print(f'Setting up Instance Role...')
        role = aws_iam.Role(
            self, 'EC2InstanceRole',
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
            inline_policies=[inline_policy])

        print (f'Looking up AMI: {self.ami_name}')
        ami_image = aws_ec2.MachineImage().lookup(name=self.ami_name)
        if not ami_image:
            print ('Failed finding AMI image')
            sys.exit(1)

        print (f'Looking up instance type: {self.instance_type}')
        instance_type = aws_ec2.InstanceType(self.instance_type)
        if not instance_type:
            print ('Failed finding instance')
            sys.exit(1)

        print (f'Using VPC: {self.vpc_name}')
        vpc = aws_ec2.Vpc.from_lookup(self, 'vpc', vpc_id=self.vpc_name)
        if not vpc:
            print ('Failed finding VPC')
            sys.exit(1)

        print ('Creating security group')
        sec_grp= aws_ec2.SecurityGroup(self, 'ec2-sec-grp', vpc=vpc, allow_all_outbound=True)
        if not sec_grp:
            print ('Failed finding security group')
            sys.exit(1)

        print ('Creating inbound firewall rule')
        sec_grp.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4(f'{local_ip}/32'), 
            description='Inbound SSH', 
            connection=aws_ec2.Port.tcp(22))

        if not sec_grp:
            print ('Failed creating security group')
            sys.exit(1)

        print (f'Creating EC2 Instance: {self.instance_name} using {self.instance_type} with ami: {self.ami_name}')
        ec2_inst = aws_ec2.Instance(
            self, 'ec2_inst', 
            instance_name=self.instance_name,
            instance_type=instance_type,
            machine_image=ami_image,
            vpc=vpc,
            security_group=sec_grp,
            key_name=self.key_name,
            user_data=user_data,
            role=role) 

        if not ec2_inst:
            print ('Failed creating ec2 instance')
            sys.exit(1)

        CfnOutput(self, "MyInstanceIp", value=ec2_inst.instance_public_ip)
