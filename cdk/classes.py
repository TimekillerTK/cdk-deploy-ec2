from dataclasses import dataclass
from enum import Enum


class EC2OS(Enum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"

@dataclass
class EnvVars:
    vpc_id: str
    aws_region: str
    aws_account: str
    key_name: str | None
    ec2_os: EC2OS = EC2OS.LINUX
    project_name: str = "cdk-deploy-ec2"


@dataclass
class LinuxEC2Instance:
    instance_type: str = "t3a.micro"
    machine_image: str = "amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2"


@dataclass
class WindowsEC2Instance:
    instance_type: str = "t3a.medium"
    machine_image: str = "Windows_Server-2022-English-Full-Base-2023.08.10"


@dataclass
class EC2Instance:
    os_type: LinuxEC2Instance | WindowsEC2Instance
    key_name: str | None
    vpc_id: str
    associate_public_ip_address: bool = True
    user_data: str | None = None
    name: str = "cdk-deploy-ec2"
