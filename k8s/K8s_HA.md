# Triển khai mô hình HA cho master

## Chuẩn bị

Trong bài viết này sẽ sử dụng 1 số máy chủ như sau:
- 1 VM làm HA
- 3 VM làm Master
- 2 VM làm Worker Node

**Các VM trong bài đều sử dụng CentOS 7**

## Cài đặt

### Node Control HA

Thay đổi hostname

```sh
hostnamectl set-hostname haproxy
```

Cài đặt haproxy

```sh
yum install haproxy -y
```

Tạo file cấu hình HAProxy với 3 node master với nội dung như bên dưới

```sh
global
  log /dev/log  local0
  log /dev/log  local1 notice
  stats socket /var/lib/haproxy/stats level admin
  chroot /var/lib/haproxy
  user haproxy
  group haproxy
  daemon

defaults
  log global
  mode  http
  option  httplog
  option  dontlognull
        timeout connect 5000
        timeout client 50000
        timeout server 50000

frontend kubernetes
    bind 172.16.7.156:6443
    option tcplog
    mode tcp
    default_backend kubernetes-master-nodes

backend kubernetes-master-nodes
    mode tcp
    balance roundrobin
    option tcp-check
    server master1 172.16.7.157:6443 check fall 3 rise 2
    server master2 172.16.7.158:6443 check fall 3 rise 2
    server master3 172.16.7.159:6443 check fall 3 rise 2

listen stats 172.16.7.156:8080
    mode http
    stats enable
    stats uri /
    stats realm HAProxy\ Statistics
    stats auth admin:haproxy
```

Tắt SELinux

```sh
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

### Node master

Các bước sau thực hiện trên cả 3 node

```sh
modprobe br_netfilter
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
```

Tiến hành off swap nếu có

Thêm IP của các node vào file /etc/hosts

```sh
echo '172.16.7.156 haproxy' >> /etc/hosts
echo '172.16.7.157 master1' >> /etc/hosts
echo '172.16.7.158 master2' >> /etc/hosts
echo '172.16.7.159 master3' >> /etc/hosts
echo '172.16.7.161 worker1' >> /etc/hosts
echo '172.16.7.162 worker2' >> /etc/hosts
```

Bổ sung repo trên các node master

```sh
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
```

Tiến hành cài đặt kubeadm docker

```sh
yum install kubeadm docker -y
```

Khởi động service

```sh
systemctl enable docker --now
systemctl enable kubelet --now
```

Chọn 1 node master đầu tiên để tiến hành khởi tạo cụm cluster (ở bài này sử dụng master1), chạy lệnh bên dưới ở node master1

```sh
kubeadm init --control-plane-endpoint "172.16.7.156:6443" --upload-certs
```

![]()

Thực hiện cấu hình để có thể thao tác với kubectl (thực hiện trên master1)

```sh
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```

Cài đặt Network cho k8s (thực hiện trên node master1)

```sh
export kubever=$(kubectl version | base64 | tr -d '\n')
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$kubever"
```

Tiến hành thao tác trên 2 node master còn lại

```sh
kubeadm join 172.16.7.156:6443 --token 0tshep.2l5oj9twjsoj9no7 --discovery-token-ca-cert-hash sha256:7e42aad1ddee8c0c1bfaa844de1a16631aaebb075a53213c22c7669672f75b05 --control-plane --certificate-key 99ae0cb8e99970fc0ef39d53020f6d074f497f5c943aa2a8ef4e847c7b1452df
```

### Node worker

