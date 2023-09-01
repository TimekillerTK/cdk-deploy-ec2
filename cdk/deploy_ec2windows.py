from typing import Any

import requests
from aws_cdk import CfnOutput, Stack, aws_ec2, aws_iam
from constructs import Construct

from cdk.classes import EC2Instance
from cdk.functions import get_local_ip


class DeployEc2WindowsStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, ec2_data: EC2Instance, **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get your local IP
        local_ip = get_local_ip()
        if not local_ip:
            print(f"Failed getting local public IP ")
            raise SystemExit(1)
        print(f"--> Local IP: {local_ip}")

        # Check if user data needs to be added
        if ec2_data.user_data:
            try:
                with open(f"userdata/{ec2_data.user_data}.ps1", "r") as file:
                    script = file.read()
            except:
                print("File in path does not exist:")
                print(f" - userdata/{ec2_data.user_data}.ps1")
                raise SystemExit(1)

            user_data = aws_ec2.UserData.for_windows()
            user_data.add_commands(script)
        else:
            user_data = None

        # Setting some variables
        instance_type = aws_ec2.InstanceType(
            instance_type_identifier=ec2_data.os_type.instance_type
        )
        machine_image = aws_ec2.MachineImage().lookup(name=ec2_data.os_type.machine_image)
        vpc = aws_ec2.Vpc.from_lookup(self, "vpc", vpc_id=ec2_data.vpc_id)

        print("Creating security group")
        sec_grp = aws_ec2.SecurityGroup(
            self, f"{ec2_data.name}-security-group", vpc=vpc, allow_all_outbound=True
        )

        print("[DEFAULT] Creating inbound firewall rule for port 3389:")
        print(f" - {local_ip}/32")
        sec_grp.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4(f"{local_ip}/32"),
            description=f"Inbound Allow 3389",
            connection=aws_ec2.Port.tcp(3389),
        )

        print(f"Setting up Instance Role...")
        role = aws_iam.Role(
            self,
            f"{ec2_data.name}-role",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        print("Adding Session Manager permissions to Instance role...")
        role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        print(
            f" - {ec2_data.name} using {ec2_data.os_type.instance_type} with ami: {ec2_data.os_type.machine_image}"
        )

        ec2_instance = aws_ec2.Instance(
            self,
            ec2_data.name,
            instance_name=ec2_data.name,
            instance_type=instance_type,
            associate_public_ip_address=ec2_data.associate_public_ip_address,
            machine_image=machine_image,
            vpc=vpc,
            security_group=sec_grp,
            key_name=ec2_data.key_name,
            user_data=user_data,
            role=role,
        )

        # TODO: Should return a nice, user friendly command in the terminal like:
        #  - aws ssm start-session --target instance-id-from-cfnoutput
        # Export created EC2 instance IP Address & Instance ID as CFN Output!
        # TODO: This export needs to be conditional
        # CfnOutput(self, f"{instance_name}-pubip", value=ec2_inst.instance_public_ip)
        CfnOutput(self, f"{ec2_data.name}-windows-id", value=ec2_instance.instance_id)
