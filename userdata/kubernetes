# shebang is added automatically by deploy_ec2.py
# this will install prerequesites for kubernetes
# Documentation: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/ 

# NOTE: built for AMI: amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2

# add sysctl settings to a .conf file for load on boot
cat <<EOF | tee /etc/sysctl.d/kubernetes.conf
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

# peristently load required containerd modules on boot & load with command
cat <<EOF | tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
modprobe br_netfilter && modprobe overlay
sysctl --system

# install some packages 
# iproute-tc: command 'tc' is expected when kubeadm is running
yum install iproute-tc nmap jq -y

# Download and install containerd 
TARFILE=containerd-1.6.5-linux-amd64.tar.gz
wget https://github.com/containerd/containerd/releases/download/v1.6.5/${TARFILE}
wget https://github.com/containerd/containerd/releases/download/v1.6.5/${TARFILE}.sha256sum
sha256sum -c ${TARFILE}.sha256sum # this needs to be checked later
tar Cxzvf /usr/local $TARFILE

# Systemd unit file for containerd
cat <<EOF | tee /etc/systemd/system/containerd.service
[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5
# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity
# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
EOF

# generate default containerd config file 
mkdir -p /etc/containerd
/usr/local/bin/containerd config default > /etc/containerd/config.toml

# use systemd cgroup driver 
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

# Reload systemd daemon to take new unit file into account & start the service
systemctl daemon-reload
systemctl enable --now containerd

# download & install runc for containerd
wget https://github.com/opencontainers/runc/releases/download/v1.1.2/runc.amd64
wget https://github.com/opencontainers/runc/releases/download/v1.1.2/runc.sha256sum
sha256sum -c runc.sha256sum # fix later, too much spam
install -m 755 runc.amd64 /usr/local/sbin/runc

# download & install CNI plugins for containerd
CNIPLUGINS=cni-plugins-linux-amd64-v1.1.1.tgz
wget https://github.com/containernetworking/plugins/releases/download/v1.1.1/${CNIPLUGINS}
wget https://github.com/containernetworking/plugins/releases/download/v1.1.1/${CNIPLUGINS}.sha256
sha256sum -c ${CNIPLUGINS}.sha256
mkdir -p /opt/cni/bin && tar Cxzvf /opt/cni/bin ${CNIPLUGINS}

# Add kubernetes repository to yum.repos
# repo_gpgcheck disabled due to issue: https://github.com/kubernetes/kubernetes/issues/60134
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF

# # Not required for Amazon Linux 2
# # sudo setenforce 0
# # sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

# install kubelet, kubeadm and kubectl
yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

# start/enable kublet 
# NOTE: this will immediatly start crashing/restarting until kubeadm init is run
systemctl enable --now kubelet

# Bootstrap new k8s cluster, must be run as root
# NOTE: Flannel requires 10.244.0.0/16 pod network cidr BY DEFAULT
kubeadm init --pod-network-cidr=10.244.0.0/16 > /home/ec2-user/k8soutput && chown 1000:1000 /home/ec2-user/k8soutput

# .kube/config section should go here (add later!)
mkdir -p /home/ec2-user/.kube
cp -i /etc/kubernetes/admin.conf /home/ec2-user/.kube/config
chown -R 1000:1000 /home/ec2-user/.kube

# Install a pod network add-on
# https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/#pod-network
# Here we choose Flannel: https://github.com/flannel-io/flannel#getting-started-on-kubernetes
# NOTE: Run as a normal user ec2-user
mkdir -p /opt/bin && \
    curl -L https://github.com/flannel-io/flannel/releases/download/v0.18.0/flanneld-amd64 -o /opt/bin/flanneld && \
    chmod +x /opt/bin/flanneld
runuser -l ec2-user -c "kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml"

#### WARNING: https://github.com/containerd/containerd/issues/6921 Issue with containerd & weave ####
### Fixed in version 1.6.5
# Here we choose Weave Net: https://www.weave.works/docs/net/latest/kubernetes/kube-addon/
# NOTE: Run as a normal user ec2-user
# SCRIPT_PATH=/home/ec2-user/k8s_networking.sh
# cat <<'EOF' | tee /home/ec2-user/k8s_networking.sh
# #!/bin/bash
# kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
# EOF
# chown ec2-user:ec2-user ${SCRIPT_PATH} && chmod +x ${SCRIPT_PATH}
# su -c "${SCRIPT_PATH}" ec2-user
####

# In order to be able to schedule pods on the control-plane / master node
# NOTE: Run as normal user ec2-user
# runuser -l ec2-user -c "kubectl taint nodes --all node-role.kubernetes.io/control-plane-"
# runuser -l ec2-user -c "kubectl taint nodes --all node-role.kubernetes.io/master-"

# Install an Nginx ingress controller
# Docs: https://kubernetes.github.io/ingress-nginx/deploy/
# runuser -l ec2-user -c "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.0/deploy/static/provider/cloud/deploy.yaml"

# Install Helm
# Source: https://github.com/helm/helm/releases
# <insert command here>

