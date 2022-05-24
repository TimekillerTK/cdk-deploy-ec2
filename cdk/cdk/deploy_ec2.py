import os
import sys
import requests
from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2
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

        print(f'Checking name of key pair...')
        if not self.key_name:
            print('Failed getting key pair. Not set?')
            sys.exit(1)

        print(f'Looking up local public IP...')
        local_ip = (requests.get('http://icanhazip.com')).text.split()[0]
        print(f'Local IP: {local_ip}')
        if not local_ip:
            print(f'Failed getting local public IP ')
            return

        print (f'Looking up AMI: {self.ami_name}')
        ami_image = aws_ec2.MachineImage().lookup(name=self.ami_name)
        if not ami_image:
            print ('Failed finding AMI image')
            return

        print (f'Looking up instance type: {self.instance_type}')
        instance_type = aws_ec2.InstanceType(self.instance_type)
        if not instance_type:
            print ('Failed finding instance')
            return

        print (f'Using VPC: {self.vpc_name}')
        vpc = aws_ec2.Vpc.from_lookup(self, 'vpc', vpc_id=self.vpc_name)
        if not vpc:
            print ('Failed finding VPC')
            return

        print ('Creating security group')
        sec_grp= aws_ec2.SecurityGroup(self, 'ec2-sec-grp', vpc=vpc, allow_all_outbound=True)
        if not sec_grp:
            print ('Failed finding security group')
            return

        print ('Creating inbound firewall rule')
        sec_grp.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4(f'{local_ip}/32'), 
            description='Inbound SSH', 
            connection=aws_ec2.Port.tcp(22))

        if not sec_grp:
            print ('Failed creating security group')
            return

        print (f'Creating EC2 Instance: {self.instance_name} using {self.instance_type} with ami: {self.ami_name}')
        ec2_inst = aws_ec2.Instance(
            self, 'ec2_inst', 
            instance_name=self.instance_name,
            instance_type=instance_type,
            machine_image=ami_image,
            vpc=vpc,
            security_group=sec_grp,
            key_name=self.key_name)

        if not ec2_inst:
            print ('Failed creating ec2 instance')
            return

        CfnOutput(self, "MyInstanceIp", value=ec2_inst.instance_public_ip)
