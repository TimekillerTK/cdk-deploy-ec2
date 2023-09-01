from os import environ, getenv

from urllib3 import PoolManager

from cdk.classes import EC2OS, EnvVars


def get_env_vars() -> EnvVars:
    try:
        vpc_id = environ["VPC_ID"]
        aws_region = environ["AWS_REGION"]
        aws_account = environ["AWS_ACCOUNT"]

    except KeyError as err:
        print(f"Environment Variable missing:: {err}")
        raise SystemExit(1) from err

    env_vars = EnvVars(
        vpc_id=vpc_id,
        aws_region=aws_region,
        aws_account=aws_account,
        key_name=getenv("KEY_NAME"),
    )

    project_name = getenv("PROJECT_NAME")
    ec2_os = getenv("EC2_OS")

    if project_name:
        env_vars.project_name = project_name
    if ec2_os:
        env_vars.ec2_os = EC2OS(ec2_os.upper())

    return env_vars


def get_local_ip() -> str:
    http = PoolManager()
    response = http.request("GET", "http://icanhazip.com")
    print(response)
    return response.data.decode("utf-8").split()[0]
