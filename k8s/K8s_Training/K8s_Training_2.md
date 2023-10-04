# Kubernetes - Training buổi 2

Trước khi bắt đầu, hãy chắc chắn là bạn đã đọc và hiểu những gì được truyền tải trong buổi 1

[K8s - Training buổi 1](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Training/K8s_Training_1.md)

## Nội dung

Trong buổi training lần này, chúng ta sẽ tìm hiểu các nội dung sau đây:

I. Mô hình và cách xây dựng 1 cụm k8s HA gồm >=2 node master và >=2 node worker

II. Quy trình triển khai ứng dụng lên k8s

III. Autoscaling

## I. Xây dựng cụm k8s 

### Mô hình tổng quan

![](./images/K8s_4.png)

**Lưu ý:**
- Với mục đích tìm hiểu và kiểm thử thì sử dụng 2 hay 3 worker node đều được
- OS sử dụng trong bài này là Ubuntu 18.04, có thể sử dụng Ubuntu 20.04 cũng được, không khuyến khích 22.04

### Xây dựng hệ thống

#### 1. Cài đặt bộ cân bằng tải sử dụng HAProxy

Thay đổi hostname cho LB

```sh
hostnamectl set-hostname k8s-loadbalancer
```

Chỉnh sửa file hosts (**chỉnh sửa IP cho phù hợp**)

```sh
echo << EOF > /etc/hosts
127.0.0.1       localhost k8s-loadbalancer
103.159.51.184       k8s-master1
103.101.162.38       k8s-master2
103.159.51.229       k8s-worker1
103.159.51.165       k8s-worker2
103.101.162.159      k8s-worker3
103.101.163.198      k8s-loadbalancer
EOF
```

Cài đặt HAProxy

```sh
apt-get update -y && apt-get upgrade -y
apt-get install haproxy
```

Chỉnh sửa file cấu hình HAProxy tại ```/etc/haproxy/haproxy.cfg``` (**chỉnh sửa IP cho phù hợp**)

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
    bind 103.101.163.198:6443
    option tcplog
    mode tcp
    default_backend kubernetes-master-nodes

backend kubernetes-master-nodes
    mode tcp
    balance roundrobin
    option tcp-check
    server k8s-master1 103.159.51.184:6443 check fall 3 rise 2
    server k8s-master2 103.101.162.38:6443 check fall 3 rise 2

listen stats
    bind 103.101.163.198:8080
    mode http
    stats enable
    stats uri /
    stats realm HAProxy\ Statistics
    stats auth admin:haproxy
```

Start dịch vụ

```sh
systemctl start haproxy
```

#### 2. Bước chuẩn bị trên các node

**Các bước sau làm trên cả 5 node (thay đổi IP cho phù hợp)**

- Update và upgrade package của Ubuntu

```sh
apt-get update -y && apt-get upgrade -y
apt-get -y install vim curl wget 
apt-get -y install byobu
```

- Tắt swap

```sh
swapoff -a
```

- Mở ```/etc/fstab``` và đóng dòng mount fstab lại (nếu có)

- Kiểm tra lại bằng lệnh ```free -hm```

- Khai báo các node trong file hosts và đặt hostname cho node

```sh
cat << EOF > /etc/hosts
127.0.0.1       localhost k8s-master1
103.159.51.184       k8s-master1
103.159.51.229       k8s-worker1
103.159.51.165       k8s-worker2
103.101.162.159       k8s-worker3
103.101.162.38       k8s-master2
103.101.163.198       k8s-loadbalancer
EOF
```

```sh
hostnamectl set-hostname k8s-master1
```

- Khởi động lại node

```sh
init 6
```

#### 3. Cài đặt docker và các thành phần cần thiết của K8s

Trên tất cả các node sẽ phải có các thành phần: docker, kubelet, kubeadm và kubectl. Trong đó:
- ```docker```: môi trường chạy các container
- ```kubeadm```: được sử dụng để thiết lập cụm cluster cho K8s. Các tài liệu chuyên môn gọi kubeadm là một bootstrap (bootstrap tạm hiểu là 1 tool đóng gói để tự động làm việc gì đó)
- ```kubelet```: là thành phần chạy trên các host, có nhiệm vụ kích hoạt các pod và container trong cụm cluster của K8s
- ```kubectl```: là công cụ cung cấp CLI để tương tác với K8s

Đầu tiên, cài đặt Docker trên tất cả các node

```sh
apt-get -y install docker.io
```

Cài đặt các thành phần của K8s trên tất cả các node

```sh
apt-get update && apt-get install -y apt-transport-https

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add

cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF

apt-get update  -y
apt-get install -y kubelet kubeadm kubectl
```

**Lưu ý:** Trước khi cài đặt ta **có thể** dùng lệnh ```apt-cache madison kubeadm``` để kiểm tra các phiên bản khả dụng trước khi cài đặt nó.

Đánh dấu không update các package liên quan đến kubernetes

```sh
apt-mark hold kubelet
apt-mark hold kubeadm
apt-mark hold kubectl
```

#### 4. Khởi tạo cluster

Thiết lập cluster:
- Đứng trên node ```k8s-master1``` thực hiện lệnh dưới để thiết lập cluster **(thay đổi IP cho phù hợp)**

```sh
kubeadm init --apiserver-advertise-address 103.159.51.184 --pod-network-cidr=10.244.0.0/16 --control-plane-endpoint "103.101.163.198:6443" --upload-certs
```

Trong đó:
- ```103.159.51.184```: là IP của node k8s-master
- ```103.101.163.198```: là IP của loadbalancer
- ```--apiserver-advertise-address```: là địa chỉ của node k8s-master, địa chỉ này cần truyền thông được với các node còn lại của cụm cluster. Trong ví dụ này node k8s master có địa chỉ là 103.159.51.184
- ```--pod-network-cidr```: là dải địa chỉ mạng phụ thuộc mà công nghệ network sẽ sử dụng khi kết hợp với K8s, trong hướng dẫn này sử dụng flannel và flannel sử dụng dải 10.244.0.0/16
- ```--control-plane-endpoint```: khai báo địa chỉ của loadbalancer để các master node kết nối đến

Sau khi thực hiện các bước cài đặt ban đầu, các node sau đó có thể được join vào cluster bằng token và key đã được cấp

![](./images/K8s_5.png)

Lệnh join node thường có dạng như sau: **(LƯU Ý LÀ NÓ CÓ DẠNG NHƯ DƯỚI ĐÂY THÔI, AE PHẢI COPY LỆNH CHÍNH XÁC Ở ĐẦU RA CỦA LỆNH KHỞI TẠO CLUSTER THÌ MỚI ĐƯỢC)**

- Với node master:

```sh
kubeadm join 103.101.163.198:6443 --token psu04g.j7uznrlicyvaekdb \
        --discovery-token-ca-cert-hash sha256:e3941a25564b7e20f80d30046cfd04cd89b7ab5fa5b60e183f5f1c7db781031d \
        --control-plane --certificate-key 79b9ee328abf9f664d02f662adb4a9ba765f709532f1a30b9eff8534f37861c0
```

- Với node worker:

```sh
kubeadm join 103.101.163.198:6443 --token psu04g.j7uznrlicyvaekdb \
        --discovery-token-ca-cert-hash sha256:e3941a25564b7e20f80d30046cfd04cd89b7ab5fa5b60e183f5f1c7db781031d
```

- Tạo user ```ubuntu``` để thực hiện cấu hình cho K8s. Nếu có user trước đó rồi thì không cần thực hiện bước này

```sh
useradd ubuntu
```

- Nhập thông tin và mật khẩu cho user ```ubuntu```, sau đó phân quyền sudoer bằng lệnh dưới

```sh
echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
```

- Chuyển sang user ubuntu để thực hiện

```sh
su ubuntu
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

- Sử dụng thủ thuật dưới để thao tác lệnh trong K8s được thuận lợi hơn nhờ việc tự động hoàn thiện lệnh mỗi khi thao tác

```sh
echo "source <(kubectl completion bash)" >> ~/.bashrc
```

Cài đặt Pod Network
- Đứng trên node K8s-master1 cài đặt Pod network
- K8s có nhiều lựa chọn cho giải pháp network để kết nối các container, trong hướng dẫn này chúng ta sử dụng flannel

```sh
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

#### 5. Cài đặt helm

Helm là một trình quản lý gói và công cụ quản lý ứng dụng cho K8s, nó đóng gói nhiều tài nguyên K8s vào một đơn vị triển khai logic duy nhất được gọi là Chart. Bên trong của Chart sẽ có phần chính là các template, là định nghĩa các tài nguyên sẽ triển khai lên K8s. Nhờ helm ta có thể đơn giản hóa quá trình cài đặt của rất nhiều thành phần trong K8s.

```sh
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
sudo chmod 700 get_helm.sh
./get_helm.sh
```

#### 6. Cài đặt metrics server

Metrics server là một add-ons, chứ nó không có sẵn trong K8s cluster của ta, nếu ta muốn sử dụng được tính năng autoscaling, ta cần phải cài đặt metrics server này vào.

```sh
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Kubelet certificate cần phải được ký bởi cluster CA, hoặc tắt nó đi bằng cách

```sh
kubectl edit deployment metrics-server -n kube-system
```
Sau đó tìm đến ```.spec.template.spec.containers[].args[]``` và thêm tham số sau vào ```--kubelet-insecure-tls```

Kiểm tra đã cài đặt thành công chưa bằng lệnh

```sh
kubectl top node
```

#### 7. Cài đặt nginx ingress controller

Trong các môi trường cloud truyền thống, nơi mà network load balancer là khả dụng, 1 tệp cấu hình trong K8s có thể cung cấp 1 điểm kết nối để giao tiếp đến Ingress-Nginx Controller với client bên ngoài, và, trực tiếp đối với các ứng dụng bên trong cluster. Môi trường bare-metal lại thiếu đi đối tượng này, do đó nó cần được setup khác đi một chút để có thể cung cấp 1 access point hoạt động tương tự ra các client bên ngoài.

Cài đặt nginx ingress controller:

```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
```

Cài đặt metalLB:

```sh
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.9/config/manifests/metallb-native.yaml
```

Lệnh trên sẽ deploy MetalLB vào cluster dưới namespace ```metallb-system```. Các thành phần trong file manifest này bao gồm:
- ```metallb-system/controller``` deployment. Đây là 1 controller toàn cluster sử dụng để xử lý phân phối IP address
- ```metallb-system/speaker``` daemonset. Đây là 1 thành phần mà đưa ra protocol mà bạn sử dụng để giúp service reachable
- Các service account cho controller và speaker, cùng với quyền RBAC mà các thành phần này cần để hoạt động

MetalLB cần 1 pool địa chỉ IP để sử dụng cho ```ingress-nginx``` service. Pool này có thể chỉ định thông qua ```IPAddressPool``` object ở trong cùng namespace với MetalLB controller. 

Tạo 1 object với kind IPAddressPool như sau

```sh
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default
  namespace: metallb-system
spec:
  addresses:
  - 103.159.51.184
  autoAssign: true
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - default
```

```sh
kubectl apply -f ipaddresspool.yaml
```