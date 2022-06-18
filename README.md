- [Deploy EC2 with CDK (Python)](#deploy-ec2-with-cdk-python)
  - [UserData](#userdata)
    - [docker](#docker)
    - [kubernetes](#kubernetes)
  - [Prequisites](#prequisites)
  - [How to use](#how-to-use)
  - [Environment Variables (Required)](#environment-variables-required)
  - [Environment Variables (Optional)](#environment-variables-optional)
  - [Setting Environment Variables](#setting-environment-variables)
    - [Example 1](#example-1)
    - [Example 2](#example-2)
    - [Example 3](#example-3)
- [Known Issues](#known-issues)

# Deploy EC2 with CDK (Python)
Simple AWS CDK Python project to deploy EC2 Instance(s) (will deploy a free tier `t2.micro` by default). Also can optionally have the following set up and ready to use:
* `docker` (plus `docker-compose`)
* `kubernetes` (using `containerd` & `flannel`)

Plus some diagnostic tools I find useful, such as `nmap`. The deployed EC2 instances will also **OPTIONALLY** copy all contents of a specified S3 bucket in SSM parameter `/cdk-deploy-ec2/s3bucketname` to `/home/ec2-user` on the deployed instances.

Once the deployment is finished, it will spit out the IP Addresses of the instances being created for SSH connections (but Session Manager connections are also available):
```sh
✨  Deployment time: 34.9s

Outputs:
DeployEc2Stack.MyInstanceIp = xxx.xxx.xxx.xxx
Stack ARN:
arn:aws:cloudformation:${AWS_REGION}:${AWS_ACCOUNT}:stack/DeployEc2Stack/${RANDOMUUID}
```
## UserData
There are two kinds of userdata that can be deployed with the EC2 instance in question:

### docker
Will deploy docker engine & docker compose, ready to use on the EC2 instance.

```
[ec2-user@ip-172-31-22-63 ~]$ docker container ls
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

```

### kubernetes
> **NOTE: Not intended for use with `AWS Elastic Kubernetes Services (EKS)` in any way!**
> 
This will deploy a fully functional **single node** kubernetes cluster control plane for testing/playing around. Container engine is `containerd` and networking CNI used is `flannel`.


If you want to deploy pods on the control plane, you'll need to get rid of the taint on the master node by running:
* `kubectl taint nodes --all node-role.kubernetes.io/control-plane-`
* `kubectl taint nodes --all node-role.kubernetes.io/master-`

> NOTE: Currently deploying multiple EC2 instances will not join them to the cluster, each one will be it's own individual control plane/cluster!
```sh
NAMESPACE     NAME                                                        READY   STATUS    RESTARTS   AGE
kube-system   pod/coredns-6d4b75cb6d-6xlnd                                1/1     Running   0          94s
kube-system   pod/coredns-6d4b75cb6d-rrcwq                                1/1     Running   0          94s
kube-system   pod/etcd-ip-172-31-28-175.ec2.internal                      1/1     Running   0          108s
kube-system   pod/kube-apiserver-ip-172-31-28-175.ec2.internal            1/1     Running   0          108s
kube-system   pod/kube-controller-manager-ip-172-31-28-175.ec2.internal   1/1     Running   0          108s
kube-system   pod/kube-flannel-ds-bq9vl                                   1/1     Running   0          94s
kube-system   pod/kube-proxy-txvwj                                        1/1     Running   0          94s
kube-system   pod/kube-scheduler-ip-172-31-28-175.ec2.internal            1/1     Running   0          108s

NAMESPACE     NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
default       service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  110s
kube-system   service/kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   108s

NAMESPACE     NAME                             DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-system   daemonset.apps/kube-flannel-ds   1         1         1       1            1           <none>                   106s
kube-system   daemonset.apps/kube-proxy        1         1         1       1            1           kubernetes.io/os=linux   108s

NAMESPACE     NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
kube-system   deployment.apps/coredns   2/2     2            2           108s

NAMESPACE     NAME                                 DESIRED   CURRENT   READY   AGE
kube-system   replicaset.apps/coredns-6d4b75cb6d   2         2         2       94s
```


## Prequisites
Install the following required prequisites for AWS CDK:
* [npm & Node.js](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* [aws-cdk](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
* [pip & python3](https://realpython.com/installing-python/)
* [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

For managing this project, you'll also need [poetry](https://github.com/python-poetry/poetry) and probably also [pyenv](https://github.com/pyenv/pyenv) to manage your environments.

> Don't forget to set up your [AWS Credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for a target AWS account using aws cli!

## How to use
Once you meet the prequisites, to deploy an EC2 instance:
1. Clone this repository
   * `git clone https://github.com/TimekillerTK/cdk-deploy-ec2.git`
2. Install the project python requirements
   * `pip install -r requirements.txt` 
3. Set the required environment variables (see below)
4. run `cdk deploy`


## Environment Variables (Required)
These are the following **required** environment variables:
* `AWS_ACCOUNT` - AWS account to deploy EC2 instance(s)
* `AWS_REGION` - AWS region to deploy EC2 instance(s)
* `VPC_ID` - VPC to deploy EC2 instance(s)

## Environment Variables (Optional)
Additionally, you can set the following optional environment variables, most of which have defaults - to customize the deployment:
* `PROJECT_NAME` - name of the project, resources in the stack will inherit the name.
  * default: `cdk-ec2-deploy`
* `AMI_NAME` - AMI used by EC2 instance(s)
  * default: `amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2`
* `KEY_NAME` - name of keypair created in your AWS account, used for SSH access to instances
  * default: None
* `ALLOW_PORTS` - space delimited list of ports allowed to the EC2 instance. By default it will open up an inbound ssh (TCP/22) firewall rule, allowing the EC2 instance to be only reachable *via your local public IP Address*.
  * default: `22`
  * example: `ALLOW_PORTS="22 80 443"`
* `GLOBAL_ALLOW_PORTS` - space delimited list of ports which will be opened up to `0.0.0.0/0`. *By default all ports are allowed only via your local public IP*
  * default: None
  * example: `GLOBAL_ALLOW_PORTS="80 443"`
* `INSTANCE_TYPE` - instance type to deploy.
  * default: `t2.micro`
* `INSTANCE_NAMES` - space delimited list of names for EC2 instances. Each name will deploy another EC2 instance.
  * default: None
  * example: `INSTANCE_NAMES="instance1 instance2 instance3`
* `USER_DATA` - name of user data to apply to EC2 instance. To use UserData, place file in the `userdata/` directory or use one of the provided ones.
  * default: None
  * example: `USER_DATA="kubernetes"`
* `BUCKET_NAME` - defining this environment variable will set an S3 bucket the EC2 instance has access to. Will also automatically copy data from S3 bucket to EC2 instnace on launch for cheap data persistence.
  * default: None
  > Make sure to set an SSM parameter `/cdk-deploy-ec2/s3bucketname` with the value being the same as the `BUCKET_NAME` environment variable set above!

## Setting Environment Variables
To make things easy, you can set up a shell script file `example.sh` that will export all your env vars for you (or use whatever method you want to set the env vars). Then you just need to run:
* `source ./example.sh`
* `cdk deploy`

### Example 1
Create a `t2.micro` EC2 Instance in the `us-east-1` region with Amazon Linux 2, which allows ports `80` `443` and for `0.0.0.0/0` and allows access from port `22` from your local public IP.

Since `USER_DATA` is not set, therefore no userdata will be processed on the EC2 instance
```sh
#!/bin/bash
## Required Variables
export AWS_ACCOUNT="123456789"
export AWS_REGION="us-east-1"  
export VPC_ID="vpc-xxxxxxxxxxxx" 

## Optional Variables
export PROJECT_NAME="my-ec2-test1" 
export KEY_NAME="mykeyname"
export AMI_NAME="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2" 
export ALLOW_PORTS="22 80 443"  
export GLOBAL_ALLOW_PORTS="80 443" 
```

### Example 2
Create three `t3a.small` EC2 instances in the `eu-west-1` region with Amazon Linux 2 which allows ports `8080` for `0.0.0.0/0` and allows access from ports `22 80 443` from your local public IP.

The instances will be called `instance1`, `instance2` and `instance3`. 

Since `USER_DATA` is set to `docker`, the `userdata/docker` userdata will be processed on all 3 EC2 instances
```sh
#!/bin/bash
## Required Variables
export AWS_ACCOUNT="123456789"
export AWS_REGION="eu-west-1"  
export VPC_ID="vpc-xxxxxxxxxxxx" 

## Optional Variables
export PROJECT_NAME="my-ec2-test2" 
export KEY_NAME="mykeyname"
export AMI_NAME="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2" 
export USER_DATA="docker"
export INSTANCE_TYPE="t3a.small"
export ALLOW_PORTS="22 80 443 8080"
export GLOBAL_ALLOW_PORTS="8080"
export INSTANCE_NAMES="instance1 instance2 instance3"
```

### Example 3
Create one `t3a.small` EC2 instance in the `eu-west-1` region with Amazon Linux 2 which only allows the default port of `22` from your local public IP. The instance will be called `instance1`.

Since `USER_DATA` is now set to `kubernetes`, the `userdata/kubernetes` will be processed on the EC2 instance.

Since `BUCKET_NAME` is now set, data from bucket `super-bucket-1234555666` will be copied to the EC2 instance.

```sh
#!/bin/bash
## Required Variables
export AWS_ACCOUNT="123456789"
export AWS_REGION="eu-west-1"  
export VPC_ID="vpc-xxxxxxxxxxxx" 

## Optional Variables
export PROJECT_NAME="my-ec2-test3" 
export KEY_NAME="mykeyname"
export AMI_NAME="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2" 
export USER_DATA="kubernetes"
export INSTANCE_TYPE="t3a.small"
export INSTANCE_NAMES="instance1"
export BUCKET_NAME="super-bucket-1234555666"
```

# Known Issues
* when using docker userdata, on first connection user doesn't have access to docker - restarting ssh session fixes this (prolly still not ready)
* CI/CD pipeline is experimental, don't use!