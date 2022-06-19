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

    def __init__(self, scope: Construct, construct_id: str, project_name: str, vpc_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required ENV vars set by user
        self.vars               = kwargs.items()
        self.aws_account        = dict(self.vars)['env'].account
        self.aws_region         = dict(self.vars)['env'].region
        self.vpc_name           = os.getenv("VPC_ID")
        
        # Optional ENV Vars set by user
        self.project_name       = project_name
        self.vpc_name           = vpc_id

        # Optional ENV Vars set by user
        self.instance_names     = os.getenv("INSTANCE_NAMES")
        self.instance_type      = os.getenv("INSTANCE_TYPE")
        self.ami_name           = os.getenv("AMI_NAME")
        self.key_name           = os.getenv("KEY_NAME")
        self.env_user_data      = os.getenv("USER_DATA")
        self.bucket_name        = os.getenv("BUCKET_NAME")
        self.allow_ports        = os.getenv("ALLOW_PORTS")
        self.global_allow_ports = os.getenv("GLOBAL_ALLOW_PORTS")
        self.allow_ip           = os.getenv("ALLOW_IP")

        # Other vars
        self.check_ci           = os.getenv("CI")

        if not self.instance_names:
            print('INSTANCE_NAMES not set, creating 1 EC2 instance by default.')
            self.instance_names = f'{self.project_name}'

        if not self.instance_type:
            print('INSTANCE_TYPE not set, using t2.micro by default.')
            self.instance_type = "t2.micro"

        if not self.ami_name:
            print('AMI_NAME not set, using amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2 by default.')
            self.ami_name = "amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2"

        if not self.key_name:
            # Should just only use session manager, if that is the case
            print('KEY_NAME not set, session manager access to EC2 instance only.')
            self.key_name = None

        # automatic lookup of public ip if not in CI environment
        if not self.check_ci == "true":
            print(f'Not running in github CI environment, looking up local public IP...')
            #TODO: Add retry, and find fallback in case it doesn't work
            local_ip = (requests.get('http://icanhazip.com')).text.split()[0]
            print(f'--> Local IP: {local_ip}')
            if not local_ip:
                print(f'Failed getting local public IP ')
                sys.exit(1)
        else:
            print(f'Running in CI environment, using ALLOW_IP environment variable...')
            local_ip = self.allow_ip

        # imports shell commands from file (for user data)
        if self.env_user_data:
            try:
                with open(f"userdata/{self.env_user_data}.sh", "r") as file:
                    shell_script = file.read()
            except:
                print('File in path does not exist:')
                print(f' - userdata/{self.env_user_data}.sh')
                sys.exit(1)
            
            if self.bucket_name:
                # if bucket name is set, create PolicyStatements allowing access to S3 bucket & SSM parameter
                #TODO: s3bucket.sh MUST get region dynamically (!) (instance metadata?)
                print(f'Creating Inline Policy for access to S3 Bucket')
                inline_policy = [aws_iam.PolicyDocument(statements=[
                aws_iam.PolicyStatement(
                    actions=["s3:PutObject","s3:GetObjectAcl","s3:GetObject","s3:ListBucket","s3:DeleteObject","s3:PutObjectAcl"],
                    resources=[f"arn:aws:s3:::{self.bucket_name}",f"arn:aws:s3:::{self.bucket_name}/*"]
                ),
                aws_iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    resources=[f"arn:aws:ssm:{self.aws_region}:{self.aws_account}:parameter/cdk-deploy-ec2/s3bucketname"]
                )])]

                if not inline_policy:
                    print('Failed setting inline policy')
                    sys.exit(1)

                # if bucketname is set, also insert s3bucket userdata commands
                try:
                    with open(f"userdata/s3bucket.sh", "r") as file:
                        s3_userdata = file.read()
                except:
                    print('File in path does not exist:')
                    print(f' - userdata/s3bucket')
                    sys.exit(1)

                shell_script = s3_userdata + shell_script
            # Runs in case userdata is set, but bucket name is not
            else:
                inline_policy = None
            
            print(f'Importing commands for EC2 UserData...')
            user_data = aws_ec2.UserData.for_linux()
            user_data.add_commands(shell_script)
            print(user_data)
            if not user_data:
                print('Failed setting user data...')
                sys.exit(1)

            print('\n===================================')
            print(f'USER DATA:\n{shell_script}\n')
            print('===================================\n')

        else:
            print('USER_DATA not set, using none.')
            inline_policy = None
            user_data = None
        
        print(f'Setting up Instance Role...')
        role = aws_iam.Role(
            self, f"{self.project_name}-role",
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
            inline_policies=inline_policy)

        print('Adding Session Manager permissions to Instance role...')
        role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

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

        #TODO: Will return None if ENV VAR isn't set, needs to be fixed
        print(f'Using VPC: {self.vpc_name}')
        vpc = aws_ec2.Vpc.from_lookup(self, 'vpc', vpc_id=self.vpc_name)
        if not vpc:
            print ('Failed finding VPC')
            sys.exit(1)

        print ('Creating security group')
        sec_grp = aws_ec2.SecurityGroup(self, f'{self.project_name}-security-group', vpc=vpc, allow_all_outbound=True)
        if not sec_grp:
            print ('Failed finding security group')
            sys.exit(1)

        if not self.allow_ports:
            #TODO: This default should not happen if we don't have a provided keypair name
            print('[DEFAULT] Creating inbound firewall rule for port 22:')
            if not self.global_allow_ports:                    
                print(f' - {local_ip}/32')
                sec_grp.add_ingress_rule(
                    peer=aws_ec2.Peer.ipv4(f'{local_ip}/32'), 
                    description=f'Inbound Allow 22', 
                    connection=aws_ec2.Port.tcp(22))
            else:
                print(f' - 0.0.0.0/0')
                sec_grp.add_ingress_rule(
                    peer=aws_ec2.Peer.ipv4(f'0.0.0.0/0'), 
                    description=f'Global Inbound Allow 22', 
                    connection=aws_ec2.Port.tcp(22))
        else:
            print ('Creating inbound firewall rules for ports:')
            if not self.global_allow_ports:  
                for port in self.allow_ports.split(' '):
                    print(f' - {port}')
                    sec_grp.add_ingress_rule(
                        peer=aws_ec2.Peer.ipv4(f'{local_ip}/32'), 
                        description=f'Inbound Allow {port}', 
                        connection=aws_ec2.Port.tcp(int(port)))
            else:
                for port in self.allow_ports.split(' '):
                    if port in self.global_allow_ports.split(' '):
                        print(f' - {port}')
                        sec_grp.add_ingress_rule(
                            peer=aws_ec2.Peer.ipv4(f'0.0.0.0/0'), 
                            description=f'Global Inbound Allow {port}', 
                            connection=aws_ec2.Port.tcp(int(port)))
                    else:   
                        print(f' - {port}')
                        sec_grp.add_ingress_rule(
                            peer=aws_ec2.Peer.ipv4(f'{local_ip}/32'), 
                            description=f'Inbound Allow {port}', 
                            connection=aws_ec2.Port.tcp(int(port)))

        if not sec_grp:
            print ('Failed creating security group')
            sys.exit(1)

        print (f'Creating EC2 Instances:')

        # will create multiple instances, if names are provided
        for name in self.instance_names.split(' '):
            instance_name = f'{name}'
            print(f' - {instance_name} using {self.instance_type} with ami: {self.ami_name}')
            ec2_inst = aws_ec2.Instance(
                self, instance_name,
                instance_name=instance_name,
                instance_type=instance_type,
                machine_image=ami_image,
                vpc=vpc,
                security_group=sec_grp,
                key_name=self.key_name,
                user_data=user_data,
                role=role) 

            if not ec2_inst:
                print ('ERROR: Failed creating ec2 instance')
                sys.exit(1)

            #TODO: Should return a nice, user friendly command in the terminal like:
            #  - aws ssm start-session --target instance-id-from-cfnoutput
            # Export created EC2 instance IP Address & Instance ID as CFN Output!
            CfnOutput(self, f"{instance_name}-pubip", value=ec2_inst.instance_public_ip)
            CfnOutput(self, f"{instance_name}-id", value=ec2_inst.instance_id)
