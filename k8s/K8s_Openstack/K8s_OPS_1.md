# Kuberentes - OpenStack - Helm

## Before starting

OpenStack-Helm charts được đăng tải tại [openstack-helm](https://tarballs.opendev.org/openstack/openstack-helm) và [openstack-helm-infra](https://tarballs.opendev.org/openstack/openstack-helm-infra) helm repositories. Hãy bật nó lên với lệnh:

```sh
helm repo add openstack-helm https://tarballs.opendev.org/openstack/openstack-helm
helm repo add openstack-helm-infra https://tarballs.opendev.org/openstack/openstack-helm-infra
```

Openstack-Helm plugins cung cấp 1 vài trợ giúp lệnh mà chúng ta có thể sử dụng. Hãy cài đặt nó với:

```sh
helm plugin install https://opendev.org/openstack/openstack-helm-plugin
```

OpenStack-Helm cung cấp charts mà có thể được deploy trên bất kỳ k8s cluster nào nếu nó thỏa mãn yêu cầu về [phiên bản](https://docs.openstack.org/openstack-helm/latest/readme.html). Tuy vậy, triển khai k8s cluster nằm ngoài phạm vi của OpenStack-Helm.

Bạn có thể sử dụng bất kỳ công cụ triển khai K8s nào cũng được. Trong hướng dẫn này, chúng ta sẽ không đi chi tiết vào việc cài đặt k8s cluster sử dụng Kubeadm hay Ansible.

Tất cả OpenStack projects đều kiểm thử trên 1 hạ tầng được quản lý bởi 1 công cụ CI là Zuul, thứ mà thực thi các Ansible playbooks trên 1 hoặc nhiều nodes. Theo đó, chúng ta sẽ sử dụng Ansible roles/playbooks để cài đặt các packages cần thiết, triển khai k8s, và chạy kiểm thử trên nó.

Để khởi tạo môi trường kiểm thử, Ansible role deploy-env sẽ được sử dụng. Role này triển khai 1 cụm k8s single/multi-node cơ bản, thường dùng để chứng minh hoạt động của các cấu hình triển khai thông dụng. Role này phù hợp với Ubuntu Focal (20.04) và Ubuntu Jammy (22.04).

## Deploy Kubernetes

### Clone roles git repositories

Trước khi bắt đầu bước tiếp theo, hãy đảm bảo là bạn đã clone git repositories chứa các Ansible roles/playbooks:

```sh
mkdir ~/osh
cd ~/osh
git clone https://opendev.org/openstack/openstack-helm-infra.git
git clone https://opendev.org/zuul/zuul-jobs.git
```

### Install Ansible

```sh
pip install ansible
```

### Set roles lookup path

Giờ hãy thiết lập biến môi trường ```ANSIBLE_ROLES_PATH``` thứ mà chỉ định nơi Ansible sẽ tìm kiếm roles:

```sh
export ANSIBLE_ROLES_PATH=~/osh/openstack-helm-infra/roles:~/osh/zuul-jobs/roles
```

Để tránh phải thiết lập nó mỗi khi bật terminal, bạn có thể định nghĩa biến môi trường này trong tệp cấu hình của Ansible.

### Prepare inventory

Ví dụ dưới đây giả định rằng có 4 nodes mà cần phải khả dụng thông qua SSH sử dụng xác thực public key và 1 ssh user (ví dụ là ubuntu) phải có quyền sudo không cần password trên node đó.

```sh
cat > ~/osh/inventory.yaml <<EOF
---
all:
  vars:
    ansible_port: 22
    ansible_user: ubuntu
    ansible_ssh_private_key_file: /home/ubuntu/.ssh/id_rsa
    ansible_ssh_extra_args: -o StrictHostKeyChecking=no
    # The user and group that will be used to run Kubectl and Helm commands.
    kubectl:
      user: ubuntu
      group: ubuntu
    # The user and group that will be used to run Docker commands.
    docker_users:
      - ubuntu
    # The MetalLB controller will be installed on the Kubernetes cluster.
    metallb_setup: true
    # Loopback devices will be created on all cluster nodes which then can be used
    # to deploy a Ceph cluster which requires block devices to be provided.
    # Please use loopback devices only for testing purposes. They are not suitable
    # for production due to performance reasons.
    loopback_setup: false
    loopback_device: /dev/loop100
    loopback_image: /var/lib/openstack-helm/ceph-loop.img
    loopback_image_size: 12G
  children:
    # The primary node where Kubectl and Helm will be installed. If it is
    # the only node then it must be a member of the groups k8s_cluster and
    # k8s_control_plane. If there are more nodes then the wireguard tunnel
    # will be established between the primary node and the k8s_control_plane node.
    primary:
      hosts:
        primary:
          ansible_host: 10.10.10.10
    # The nodes where the Kubernetes components will be installed.
    k8s_cluster:
      hosts:
        node-1:
          ansible_host: 10.10.10.11
        node-2:
          ansible_host: 10.10.10.12
        node-3:
          ansible_host: 10.10.10.13
    # The control plane node where the Kubernetes control plane components will be installed.
    # It must be the only node in the group k8s_control_plane.
    k8s_control_plane:
      hosts:
        node-1:
          ansible_host: 10.10.10.11
    # These are Kubernetes worker nodes. There could be zero such nodes.
    # In this case the Openstack workloads will be deployed on the control plane node.
    k8s_nodes:
      hosts:
        node-2:
          ansible_host: 10.10.10.12
        node-3:
          ansible_host: 10.10.10.13
EOF
```

### Run the playbook

```sh
cd ~/osh
ansible-playbook -i inventory.yaml deploy-env.yaml
```

Playbook chỉ thay đổi trạng thái của nodes đã liệt kê trong inventory file.

Nó cài đặt các package cần thiết, deploy và cấu hình Containerd và K8s. Bạn có thể xem chi tiết trong playbook.

## Kubernetes prerequisites

### Ingress controller

Ingress controller khi triển khai OpenStack trên k8s là rất quan trọng để đảm bảo khả năng truy cập từ bên ngoài cho các OpenStack services.

Openstack khuyến nghị sử dụng ```ingress-nginx``` vì sự đơn giản và đầy đủ tính năng của nó. Nó tận dụng nginx như 1 reverse proxy backend. Dưới đây là vài bước để deploy nó.

Đầu teien, hãy tạo 1 namespace cho OpenStack workloads. Ingress controller phải được deploy trong cùng namespace vì OpenStack-Helm charts tạo tài nguyên service trỏ đến ingress controller pods, thứ mà sau đó điều hướng traffic đến OpenStack API pods cụ thể.

```sh
kubectl create ns openstack
```

Tiếp đến, hãy deploy ingress controller trong ```openstack``` namespace:

```sh
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --version="4.8.3" \
    --namespace=openstack \
    --set controller.kind=Deployment \
    --set controller.admissionWebhooks.enabled="false" \
    --set controller.scope.enabled="true" \
    --set controller.service.enabled="false" \
    --set controller.ingressClassResource.name=nginx \
    --set controller.ingressClassResource.controllerValue="k8s.io/ingress-nginx" \
    --set controller.ingressClassResource.default="false" \
    --set controller.ingressClass=nginx \
    --set controller.labels.app=ingress-api
```

Bạn có thể triển khai bất kỳ ingress controller nào khác mà phù hợp với bạn nhất. Và hãy đảm bảo rằng ingress controller pods được triển khai với label ```app: ingress-api``` do OpenStack-Helm sẽ sử dụng chúng trong selector của service resource.

VD, OpenStack-Helm ```keystone``` chart mặc định tạo 1 service để điều hướng traffic đến ingress controller pods mà có nhãn ```app: ingress-api```. Sau đó nó cũng tạo 1 tài nguyên ```Ingress``` mà ingress controller sẽ sử dụng để cấu hình reverse proxy backend của nó (nginx), thứ mà cuối cùng điều hướng traffic đến Keystone API service, hay cũng có thể coi là endpoint cho Keystone API pods.

### MetalLB

MetalLB là 1 loadbalancer cho bare metal k8s clusters tận dụng L2/L3 protocols. Đây là 1 cách khá phổ biến để expose ứng dụng web chạy trong k8s ra bên ngoài cluster.

Ta có thể cài đặt MetalLB với các lệnh:

```sh
kubectl create ns metallb
helm repo add metallb https://metallb.github.io/metallb
helm install metallb metallb/metallb -n metallb-system
```

Giờ ta sẽ cần cấu hình Metallb IP address pool và IP address advertisement. MetalLB sử dụng CRD cho các cấu hình này:

```sh
tee > /tmp/metallb_ipaddresspool.yaml <<EOF
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
    name: public
    namespace: metallb-system
spec:
    addresses:
    - "172.24.128.0/24"
EOF

kubectl apply -f /tmp/metallb_ipaddresspool.yaml

tee > /tmp/metallb_l2advertisement.yaml <<EOF
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
    name: public
    namespace: metallb-system
spec:
    ipAddressPools:
    - public
EOF

kubectl apply -f /tmp/metallb_l2advertisement.yaml
```

Tiếp đến, hãy tạo 1 service có type ```Loadbalancer``` mà sẽ công khai endpoint cho tất cả OpenStack services. MetalLB sẽ cấp 1 IP address cho nó (hoặc ta tự cấp bằng cách sử dụng annotations):

```sh
tee > /tmp/openstack_endpoint_service.yaml <<EOF
---
kind: Service
apiVersion: v1
metadata:
  name: public-openstack
  namespace: openstack
  annotations:
    metallb.universe.tf/loadBalancerIPs: "172.24.128.100"
spec:
  externalTrafficPolicy: Cluster
  type: LoadBalancer
  selector:
    app: ingress-api
  ports:
    - name: http
      port: 80
    - name: https
      port: 443
EOF

kubectl apply -f /tmp/openstack_endpoint_service.yaml
```

Service này sẽ chuyển hướng traffic đến ingress controller pods. Openstack-Helm chart tạo ```Ingress``` mà được sử dụng bởi ingress controller để cấu hình reverse proxy backend để cuối cùng traffic sẽ được đưa tới đúng OpenStack API pods.

Mặc định, ```Ingress``` objects sẽ chỉ chứa các rules cho domain ```openstack.svc.cluster.local```. Đây là domain nội bộ của k8s và không hỗ trợ cho việc phân giải bên ngoài cluster.

Bạn có thể sử dụng ```host_fqdn_override``` cho endpoints để thiết lập 1 hostname thay thế sử dụng 1 dịch vụ như sslip.io. Giả sử services của bạn expose ra ở ```172.24.128.100```. Bạn có thể sử dụng ```<service>.172-24-128-100.sslip.io```.

Đây là ví dụ cho ```host_fqdn_override```:

```sh
endpoints:
  identity:
    host_fqdn_override:
      public:
        host: "keystone.172-24-128-100.sslip.io"
```

### Ceph

Ceph là 1 hệ thống lưu trữ dữ liệu phân tán có khả năng chịu lỗi và mở rộng cao. Nó cung cấp 3 loại storage chính là block, object, và file storage, khiến cho Ceph trở thành 1 lựa chọn linh hoạt cho nhiều nhu cầu về lưu trữ.

K8s CSI (Container Storage Interface) cho phép storage provider như Ceph có thể triển khai driver của nó, nhờ đó mà K8s có thể sử dụng CSI driver để cung cấp và quản lý volumes, thứ mà có thể được sử dụng cho stateful applications trên nền K8s. Trong bối cảnh của OpenStack chạy trên K8s, Ceph được sử dụng để cung cấp backend cho các dịch vụ như MariaDB, RabbitMQ và các dịch vụ khác mà cần Persistent storage. Mặc định thì OpenStack-Helm statefulsets sẽ tìm đến 1 storageClass mà có tên là ```general```.

Cùng lúc, Ceph cũng cung cấp RDB API, thứ mà các ứng dụng có thể tận dụng trực tiếp để tạo và mount block devices phân tán giữa Ceph cluster. VD như OpenStack Cinder có thể sử dụng Ceph để cung cấp persistent block device cho VM được quản lý bởi Nova.

Phương thức được khuyến khích để quản lý Ceph trên nền K8s là sử dụng Rook operator. Rook project cung cấp Helm chart để deploy Rook operator, thứ mà mở rộng k8s api bằng cách thêm CRDs mà cho phép quản lý Ceph clusters thông qua K8s custom objects.

Khi Ceph cluster đã được deploy, bước tiếp theo là enable nó với services được deploy bởi OpenStack-Helm charts. ```ceph-adapter-rook``` chart cung cấp các tính năng cần thiết cho việc này. Chart này sẽ chuẩn bị K8s secret chứa Ceph client keys/configs mà sau đó sử dụng để giao tiếp với Ceph Cluster.

Dòng lệnh sau giả định Ceph cluster được deploy ở ```ceph``` namespace:

```sh
helm upgrade --install ceph-adapter-rook openstack-helm-infra/ceph-adapter-rook \
    --namespace=openstack

helm osh wait-for-pods openstack
```

### Node labels

OpenStack-Helm charts phụ thuộc vào K8s node labels để xác định node nào phù hợp cho việc chạy các thành phần OpenStack cụ thể.

Các lệnh sau sẽ thiết lập labels trên tất cả các k8s nodes, tuy vậy, bạn có thể tùy chỉnh để phù hợp với nhu cầu và thiết kế của từng node:

```sh
kubectl label --overwrite nodes --all openstack-control-plane=enabled
kubectl label --overwrite nodes --all openstack-compute-node=enabled
kubectl label --overwrite nodes --all openvswitch=enabled
kubectl label --overwrite nodes --all linuxbridge=enabled
```

**Lưu ý:** Control plane nodes của k8s được taint để ngăn các pods ứng dụng lập lịch trên chúng. Bạn có thể untaint các nodes này bằng lệnh sau:

```sh
kubectl taint nodes -l 'node-role.kubernetes.io/control-plane' node-role.kubernetes.io/control-plane-
```

## Deploy OpenStack

### Check list before deployment

Hãy đảm bảo là cluster đã đáp ứng đủ các yêu cầu sau trước khi thực hiện các bước deploy OpenStack:

- K8s cluster up và running
- ```kubectl``` và ```helm``` đều khả dụng
- OpenStack-Helm repository đã được kích hoạt. OpenStack-Helm đã được cài đặt và các biến môi trường cần thiết đã được thiết lập
- Namespace ```openstack``` đã được tạo
- Ingress controller đã được deploy trong namespace ```openstack```
- MetalLB được deploy và thiết lập. Service có type ```LoadBalancer``` đã được tạo và DNS được thiết lập để phân giải OpenStack endpoint names thành IP address của service
- Ceph được deploy và kích hoạt với OpenStack-Helm

### Environment variables

Đầu tiên hãy thiết lập các biến môi trường sau:

```sh
export OPENSTACK_RELEASE=2024.1
export FEATURES="${OPENSTACK_RELEASE} ubuntu_jammy"
export OVERRIDES_DIR=$(pwd)/overrides
```

### Get values overrides

OpenStack-Helm cung cấp một số file value để định nghĩa trước feature set và nhiều cấu hình khác liên quan đến phiên bản OpenStack. Các tệp này được đặt tại OpenStack-Helm git repositories và OpenStack-Helm plugin cung cấp 1 lệnh để tìm kiếm chúng ở local (và có thể lựa chọn download nếu chưa có sẵn).

Bạn có thể xem qua phần trợ giúp của plugin:

```sh
helm osh get-values-overrides --help
```

VD: nếu bạn truyền vào feature set ```2024.1 ubuntu_jammy```, nó sẽ cố tìm kiếm các files sau:

```sh
2024.1.yaml
ubuntu_jammy.yaml
2024.1-ubuntu_jammy.yaml
```

Hãy tải các file values overrides cho các feature set định nghĩa bên trên:

```sh
INFRA_OVERRIDES_URL=https://opendev.org/openstack/openstack-helm-infra/raw/branch/master
for chart in rabbitmq mariadb memcached openvswitch libvirt; do
    helm osh get-values-overrides -d -u ${INFRA_OVERRIDES_URL} -p ${OVERRIDES_DIR} -c ${chart} ${FEATURES}
done

OVERRIDES_URL=https://opendev.org/openstack/openstack-helm/raw/branch/master
for chart in keystone heat glance cinder placement nova neutron horizon; do
    helm osh get-values-overrides -d -u ${OVERRIDES_URL} -p ${OVERRIDES_DIR} -c ${chart} ${FEATURES}
done
```

Giờ bạn có thể xem các tệp đã tải trong ```${OVERRIDES_DIR}``` và chỉnh sửa chúng nếu cần thiết

### OpenStack backend

Openstack là 1 nền tảng điện toán đám mây bao gồm nhiều dịch vụ, và hầu hết trong số chúng đều phụ thuộc vào các backend services như RabbitMQ, MariaDB, và Memcached. Những backend services này là không thể thiếu trong kiến trúc OpenStack.

#### RabbitMQ

RabbitMQ là 1 message broker mà thường được sử dụng trong OpenStack để xử lý messaging giữa các thành phần và dịch vụ khác nhau. Nó giúp quản lý giao tiếp và định vị giữa nhiều phần của hệ thống OpenStack. Các dịch vụ như Nova, Neutron, Cinder sử dụng RabbitMQ để trao đổi messages và đảm bảo sự điều phối.

Sử dụng các script sau để deploy RabbitMQ service:

```sh
helm upgrade --install rabbitmq openstack-helm-infra/rabbitmq \
    --namespace=openstack \
    --set pod.replicas.server=1 \
    --timeout=600s \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c rabbitmq ${FEATURES})

helm osh wait-for-pods openstack
```

#### MariaDB

CSDL như MariaDB thường được sử dụng làm backend database cho nhiều OpenStack projects. Những CSDL này lưu trữ thông tin nhạy cảm như user credentials, service configuration, và các dữ liệu liên quan đến VM, network, volumes. Dịch vụ như Keystone, Nova, Glance, và Cinder phụ thuộc vào MariaDB cho data storage.

```sh
helm upgrade --install mariadb openstack-helm-infra/mariadb \
    --namespace=openstack \
    --set pod.replicas.server=1 \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c mariadb ${FEATURES})

helm osh wait-for-pods openstack
```

#### Memcached

Memcached là 1 distributed memory objet caching system thường được sử dụng cho OpenStack để cải thiện hiệu năng. OpenStack services cache dữ liệu thường xuyên được truy cập vào trong Memcached, thứ mà giúp dữ liệu có thể được thu thập nhanh hơn, giảm tải cho database backend.

```sh
helm upgrade --install memcached openstack-helm-infra/memcached \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c memcached ${FEATURES})

helm osh wait-for-pods openstack
```

### OpenStack

Giờ chúng ta đã sẵn sàng để deploy OpenStack components. Một vài trong số chúng là bắt buộc, trong khi cũng có những thành phần cho phép tùy chọn.

#### Keystone

OpenStack Keystone là dịch vụ xác thực và định danh của OpenStack. Nó hỗ trợ 1 điểm trung tâm cho xác thực và phân quyền, quản lý định danh người dùng, vai trò, và truy cập vào Openstack resources. Keystone đảm bảo bảo mật và điều khiển truy cập vào nhiều Openstack services, khiến nó là 1 thành phần trọng yếu của Openstack deployments.

Để triển khai Keystone service, chạy lệnh sau:

```sh
helm upgrade --install keystone openstack-helm/keystone \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c keystone ${FEATURES})

helm osh wait-for-pods openstack
```

#### Heat

OpenStack Heat là 1 service điều phối mà cung cấp các templates và automation cho deploying và managing tài nguyên trên cloud. Nó cho phép người dùng định nghĩa infrastructure as code, khiến việc khởi tạo và quản lý các môi trường phức tạp trở nên đơn giản hơn trong OpenStack thông qua scripts.

Đây là 1 vài commands cho việc triển khai Heat service:

```sh
helm upgrade --install heat openstack-helm/heat \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c heat ${FEATURES})

helm osh wait-for-pods openstack
```

#### Glance

OpenStack Glance là 1 image service component của OpenStack. Nó quản lý VM images như OS images hay snapshots, khiến chúng khả dụng cho OpenStack compute instances.

Bạn có thể triển khai Glance với lệnh:

```sh
tee ${OVERRIDES_DIR}/glance/values_overrides/glance_pvc_storage.yaml <<EOF
storage: pvc
volume:
  class_name: general
  size: 10Gi
EOF

helm upgrade --install glance openstack-helm/glance \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c glance glance_pvc_storage ${FEATURES})

helm osh wait-for-pods openstack
```

#### Cinder

OpenStack Cinder là 1 block storage service của OpenStack. Nó quản lý và cung cấp persistent block storage cho VM, cho phép người dùng gắn và tháo persistent storage volumes khi cần thiết.

Để triển khai OpenStack Cinder, chúng ta sử dụng lệnh sau:

```sh
helm upgrade --install cinder openstack-helm/cinder \
    --namespace=openstack \
    --timeout=600s \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c cinder ${FEATURES})

helm osh wait-for-pods openstack
```

#### Compute kit backend: Openvswitch and Libvirt

OpenStack-Helm khuyến khích sử dụng OpenvSwitch cho networking backend. OpenvSwitch là 1 SDN, open source networking solution mà cung cấp virtual switching capabilities.

Để triển khai OpenvSwitch service, sử dụng lệnh sau:

```sh
helm upgrade --install openvswitch openstack-helm-infra/openvswitch \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c openvswitch ${FEATURES})

helm osh wait-for-pods openstack
```

Libvirt là 1 toolkit mà cung cấp 1 API chung cho việc quản lý VMs. Nó sử dụng OpenStack để tương tác với Hypervisors như KVM, QEMU, hay XEN.

Hãy deploy libvirt với lệnh sau:

```sh
helm upgrade --install libvirt openstack-helm-infra/libvirt \
    --namespace=openstack \
    --set conf.ceph.enabled=true \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c libvirt ${FEATURES})
```

*Lưu ý: Ở đây chúng ta không cần phải chạy ```helm osh wait-for-pods``` vì Libvirt pods phụ thuộc vào Neutron OpenvSwitch agent pods, thứ mà chưa được deploy*

#### Compute kit: Placement, Nova, Neutron

OpenStack Placement là 1 service mà giúp quản lý và phân phối tài nguyên trong OpenStack cloud environment. Nó giúp Nova compute tìm và phân phối tài nguyên 1 cách hợp lý cho VM instances.

```sh
helm upgrade --install placement openstack-helm/placement \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c placement ${FEATURES})
```

OpenStack Nova là compute service chịu trách nhiệm cho quản lý và điều phối VM trong OpenStack. Nó cung cấp và lập lịch instances, xử lý vòng đời, và tương tác với underlying hypervisors.

```sh
helm upgrade --install nova openstack-helm/nova \
    --namespace=openstack \
    --set bootstrap.wait_for_computes.enabled=true \
    --set conf.ceph.enabled=true \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c nova ${FEATURES})
```

OpenStack Neutron là networking service mà cung cấp network connectivity và cho phép người dùng tạo và quản lý network resources cho VM và các dịch vụ khác.

```sh
PROVIDER_INTERFACE=<provider_interface_name>
tee ${OVERRIDES_DIR}/neutron/values_overrides/neutron_simple.yaml << EOF
conf:
  neutron:
    DEFAULT:
      l3_ha: False
      max_l3_agents_per_router: 1
  # <provider_interface_name> will be attached to the br-ex bridge.
  # The IP assigned to the interface will be moved to the bridge.
  auto_bridge_add:
    br-ex: ${PROVIDER_INTERFACE}
  plugins:
    ml2_conf:
      ml2_type_flat:
        flat_networks: public
    openvswitch_agent:
      ovs:
        bridge_mappings: public:br-ex
EOF

helm upgrade --install neutron openstack-helm/neutron \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c neutron neutron_simple ${FEATURES})

helm osh wait-for-pods openstack
```

#### Horizon

OpenStack Horizon là 1 web app mà được thiết kế để cung cấp 1 giao diện người dùng cho OpenStack service.

Để deploy Horizon:

```sh
helm upgrade --install horizon openstack-helm/horizon \
    --namespace=openstack \
    $(helm osh get-values-overrides -p ${OVERRIDES_DIR} -c horizon ${FEATURES})

helm osh wait-for-pods openstack
```

#### OpenStack client

Cài đặt OPS Client là điều ko thể thiếu, cách dễ nhất là sử dụng pip

```sh
python3 -m venv ~/openstack-client
source ~/openstack-client/bin/activate
pip install python-openstackclient
```

Cấu hình Endpoint:

```sh
mkdir -p ~/.config/openstack
tee ~/.config/openstack/clouds.yaml << EOF
clouds:
  openstack_helm:
    region_name: RegionOne
    identity_api_version: 3
    auth:
      username: 'admin'
      password: 'password'
      project_name: 'admin'
      project_domain_name: 'default'
      user_domain_name: 'default'
      auth_url: 'http://keystone.openstack.svc.cluster.local/v3'
```

Vậy đó, giờ bạn đã có thể sử dụng OpenStack client:

```sh
openstack --os-cloud openstack_helm endpoint list
```

