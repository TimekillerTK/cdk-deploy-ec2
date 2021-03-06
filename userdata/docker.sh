# shebang is added automatically by deploy_ec2.py
# install docker & other packages
yum install docker nmap jq -y

# Docker compose can also be installed with pip, but the one on amazon linux 2 is version v1.29, whereas newest one is v2+
curl -L https://github.com/docker/compose/releases/download/v2.5.1/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod a+x /usr/local/bin/docker-compose

# Adds ec2-user to docker users
usermod -aG docker ec2-user

# Enables automatic startup & starts docker daemon
systemctl enable docker && systemctl start docker