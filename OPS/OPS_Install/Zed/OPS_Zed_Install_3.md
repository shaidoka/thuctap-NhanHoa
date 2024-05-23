# Cài đặt OpenStack (Phần 3)

Mô hình tổng quan của bài lab này sẽ như sau:

```sh
------------+-----------------------------+-----------------------------+------------
            |                             |                             |
    eth0|172.16.10.11             eth0|172.16.10.13             eth0|172.16.10.12
+-----------+-----------+     +-----------+-----------+     +-----------+-----------+
| openstack.baotrung.xyz|     | network.baotrung.xyz  |     |  [       com1       ] |
|     (Control Node)    |     |     (Network Node)    |     |     (Compute Node)    |
|                       |     |                       |     |                       |
|  MariaDB    RabbitMQ  |     |      Open vSwitch     |     |        Libvirt        |
|  Memcached  Nginx     |     |     Neutron Server    |     |      Nova Compute     |
|  Keystone   httpd     |     |      OVN-Northd       |     |      Open vSwitch     |
|  Glance     Nova API  |     |         Nginx         |     |   OVN Metadata Agent  |
|                       |     |                       |     |     OVN-Controller    |
+-----------------------+     +-----------------------+     +-----------------------+
                                eth1|(UP with no IP)          eth1|(UP with no IP)
```

### 18. Cấu hình Heat (Control Node)

Thêm user, service, và endpoint cho Heat

```sh
openstack user create --domain default --project service --password Welcome123 heat
openstack role add --project service --user heat admin
openstack role create heat_stack_owner
openstack role create heat_stack_user
openstack role add --project admin --user admin heat_stack_owner
openstack service create --name heat --description "Openstack Orchestration" orchestration
openstack service create --name heat-cfn --description "Openstack Orchestration" cloudformation
heat_api=network.baotrung.xyz
openstack endpoint create --region RegionOne orchestration public https://$heat_api:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne orchestration internal https://$heat_api:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne orchestration admin https://$heat_api:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne cloudformation public https://$heat_api:8000/v1
openstack endpoint create --region RegionOne cloudformation internal https://$heat_api:8000/v1
openstack endpoint create --region RegionOne cloudformation admin https://$heat_api:8000/v1
openstack domain create --description "Stack projects and users" heat
openstack user create --domain heat --password Welcome123 heat_domain_admin
openstack role add --domain heat --user heat_domain_admin admin
```

Tạo database cho Heat 

```sh
mysql
create database heat;
grant all privileges on heat.* to heat@'localhost' identified by 'Welcome123';
grant all privileges on heat.* to heat@'%' identified by 'Welcome123';
flush privileges;
exit
```

### 19. Cấu hình Heat (Network Node)

Cài đặt Heat services trên Network Node

```sh
apt -y install heat-api heat-api-cfn heat-engine python3-heatclient python3-vitrageclient python3-zunclient
```

Cấu hình

```sh
mv /etc/heat/heat.conf /etc/heat/heat.conf.bk
```

```sh
cat << EOF >> /etc/heat/heat.conf
# Tạo mới
[DEFAULT]
deferred_auth_method = trusts
trusts_delegated_roles = heat_stack_owner
# Heat API Host
heat_metadata_server_url = https://network.baotrung.xyz:8000
heat_waitcondition_server_url = https://network.baotrung.xyz:8000/v1/waitcondition
heat_stack_user_role = heat_stack_user
# Heat domain name
stack_user_domain_name = heat
# Heat domain admin username
stack_domain_admin = heat_domain_admin
# Heat domain admin's password
stack_domain_admin_password = Welcome123
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

# MariaDB connection info
[database]
connection = mysql+pymysql://heat:Welcome123@openstack.baotrung.xyz/heat

# Keystone connection info
[clients_keystone]
auth_uri = https://openstack.baotrung.xyz:5000

[heat_api]
bind_host = 172.16.10.13
bind_port = 8004
cert_file = /etc/heat/network.chained.crt
key_file = /etc/heat/network.private.key

[heat_api_cfn]
bind_host = 172.16.10.13
bind_port = 8000
cert_file = /etc/heat/network.chained.crt
key_file = /etc/heat/network.private.key

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = heat
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[trustee]
auth_url = https://openstack.baotrung.xyz:5000
auth_type = password
user_domain_name = default
username = heat
password = Welcome123
EOF
```

```sh
chmod 640 /etc/heat/heat.conf
chgrp heat /etc/heat/heat.conf
```

Sync DB và khởi động dịch vụ

```sh
su -s /bin/bash heat -c "heat-manage db_sync"
systemctl restart heat-api heat-api-cfn heat-engine
```

**Lưu ý:** Hãy chắc chắn user ```heat``` có quyền đọc chứng chỉ SSL (có thể sử dụng ```adduser <username> <groupname>``` để add user openstack vào chung 1 group)

### 20. Cách sử dụng Heat cơ bản

```sh
apt-get -y install python3-heatclient
# Tạo 1 stack test
cat << EOF >> sample-stack.yaml
heat_template_version: 2021-04-16

description: Heat Sample Template

parameters:
  ImageID:
    type: string
    description: Image used to boot a server
  NetID:
    type: string
    description: Network ID for the server

resources:
  server1:
    type: OS::Nova::Server
    properties:
      name: "Heat_Deployed_Server"
      image: { get_param: ImageID }
      flavor: "m1.small"
      networks:
      - network: { get_param: NetID }

outputs:
  server1_private_ip:
    description: IP address of the server in the private network
    value: { get_attr: [ server1, first_address ] }
EOF
```

```sh
Int_Net_ID=$(openstack network list | grep private | awk '{ print $2 }')
openstack stack create -t sample-stack.yaml --parameter "ImageID=Ubuntu2204;NetID=$Int_Net_ID" Sample-Stack
```

![](./images/Zed_6.png)

### 21. Cài đặt và cấu hình Octavia (Control Node)

Thêm users và services cho Octavia trên Keystone

```sh
openstack user create --domain default --project service --password Welcome123 octavia
openstack role add --project service --user octavia admin
openstack service create --name octavia --description "OpenStack LBaaS" load-balancer
export octavia_api=network.baotrung.xyz
openstack endpoint create --region RegionOne load-balancer public https://$octavia_api:9876
openstack endpoint create --region RegionOne load-balancer internal https://$octavia_api:9876
openstack endpoint create --region RegionOne load-balancer admin https://$octavia_api:9876
```

Thêm user và database cho Octavia

```sh
mysql
```

```sh
create database octavia;
grant all privileges on octavia.* to octavia@'localhost' identified by 'Welcome123';
grant all privileges on octavia.* to octavia@'%' identified by 'Welcome123';
flush privileges;
exit
```

### 22. Cài đặt và cấu hình Octavia (Network Node)

Cài đặt Octavia services. Nếu có câu hỏi nào trong quá trình cài đặt, hãy trả lời ```No```

```sh
apt-get -y install octavia-api octavia-health-manager octavia-housekeeping octavia-worker python3-ovn-octavia-provider
```

Tạo certificates mà sử dụng giữa LoadBlanacer và Octavia

```sh
mkdir -p /etc/octavia/certs/private
mkdir ~/work
cd ~/work
git clone https://opendev.org/openstack/octavia.git
cd octavia/bin
./create_dual_intermediate_CA.sh
cp -p ./dual_ca/etc/octavia/certs/server_ca.cert.pem /etc/octavia/certs
cp -p ./dual_ca/etc/octavia/certs/server_ca-chain.cert.pem /etc/octavia/certs
cp -p ./dual_ca/etc/octavia/certs/server_ca.key.pem /etc/octavia/certs/private
cp -p ./dual_ca/etc/octavia/certs/client_ca.cert.pem /etc/octavia/certs
cp -p ./dual_ca/etc/octavia/certs/client.cert-and-key.pem /etc/octavia/certs/private
chown -R octavia /etc/octavia/certs
```

Cấu hình Octavia

```sh
mv /etc/octavia/octavia.conf /etc/octavia/octavia.conf.bk
cat << EOF >> /etc/octavia/octavia.conf
# create new
[DEFAULT]
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[api_settings]
bind_host = 127.0.0.1
bind_port = 9876
auth_strategy = keystone
api_base_uri = https://network.baotrung.xyz:9876

# MariaDB connection info
[database]
connection = mysql+pymysql://octavia:Welcome123@openstack.baotrung.xyz/octavia

[health_manager]
bind_ip = 172.16.10.13
bind_port = 5555

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = octavia
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

# specify certificates created on [2]
[certificates]
ca_private_key = /etc/octavia/certs/private/server_ca.key.pem
ca_certificate = /etc/octavia/certs/server_ca.cert.pem
server_certs_key_passphrase = insecure-key-do-not-use-this-key
ca_private_key_passphrase = not-secure-passphrase

# specify certificates created on [2]
[haproxy_amphora]
server_ca = /etc/octavia/certs/server_ca-chain.cert.pem
client_cert = /etc/octavia/certs/private/client.cert-and-key.pem

# specify certificates created on [2]
[controller_worker]
client_ca = /etc/octavia/certs/client_ca.cert.pem

[oslo_messaging]
topic = octavia_prov

# Keystone auth info
[service_auth]
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = octavia
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true
EOF
```

```sh
cat << EOF >> /etc/octavia/policy.yaml
"context_is_admin": "role:admin or role:load-balancer_admin"
"admin_or_owner": "is_admin:True or project_id:%(project_id)s"
"load-balancer:read": "rule:admin_or_owner"
"load-balancer:read-global": "is_admin:True"
"load-balancer:write": "rule:admin_or_owner"
"load-balancer:read-quota": "rule:admin_or_owner"
"load-balancer:read-quota-global": "is_admin:True"
"load-balancer:write-quota": "is_admin:True"
EOF
```

```sh
chmod 640 /etc/octavia/{octavia.conf,policy.yaml}
chgrp octavia /etc/octavia/{octavia.conf,policy.yaml}
```

Cấu hình Nginx proxy:

```sh
# Thêm đoạn cấu hình sau vào phần [stream]
    upstream octavia-api {
        server 127.0.0.1:9876;
    }
    server {
        listen 172.16.10.13:9876 ssl;
        proxy_pass octavia-api;
    }
```

Sync DB và khởi động dịch vụ

```sh
su -s /bin/bash octavia -c "octavia-db-manage --config-file /etc/octavia/octavia.conf upgrade head"
systemctl restart octavia-api octavia-health-manager octavia-housekeeping octavia-worker nginx
```

### 24. Tạo Amphora image

Tạo 1 LoadBalancer image và thêm nó vào Glance

```sh
snap install octavia-diskimage-retrofit --beta --devmode
cd /var/snap/octavia-diskimage-retrofit/common/tmp
wget https://cloud-images.ubuntu.com/minimal/releases/focal/release/ubuntu-20.04-minimal-cloudimg-amd64.img
octavia-diskimage-retrofit ubuntu-20.04-minimal-cloudimg-amd64.img ubuntu-amphora-haproxy-amd64.qcow2
openstack image create "Amphora" --tag "Amphora" --file ubuntu-amphora-haproxy-amd64.qcow2 --disk-format qcow2 --container-format bare --private --project service
openstack flavor create --id 100 --vcpus 1 --ram 1024 --disk 5 m1.octavia --private --project service
openstack security group create lb-mgmt-sec-group --project service
openstack security group rule create --protocol icmp --ingress lb-mgmt-sec-group
openstack security group rule create --protocol tcp --dst-port 22:22 lb-mgmt-sec-group
openstack security group rule create --protocol tcp --dst-port 80:80 lb-mgmt-sec-group
openstack security group rule create --protocol tcp --dst-port 443:443 lb-mgmt-sec-group
openstack security group rule create --protocol tcp --dst-port 9443:9443 lb-mgmt-sec-group
```

*Lưu ý: Thời gian tạo image có thể kéo dài đến 1h tùy thuộc vào máy chủ*

Cấu hình Octavia để thiết lập instance ID và security group ID

```sh
vi /etc/octavia/octavia.conf
# Thêm phần [controller_worker]
[controller_worker]
client_ca = /etc/octavia/certs/client_ca.cert.pem
amp_image_tag = Amphora
# specify [flavor] ID for Amphora instance
amp_flavor_id = 100
# specify security group ID Amphora instance
amp_secgroup_list = <loadbalancer-security-group-id>
# specify network ID to boot Amphora instance (example below specifies public network [public])
amp_boot_network_list = <public-network-id>
network_driver = allowed_address_pairs_driver
compute_driver = compute_nova_driver
amphora_driver = amphora_haproxy_rest_driver
```

Khởi động lại dịch vụ

```sh
systemctl restart octavia-api \
octavia-health-manager \
octavia-housekeeping \
octavia-worker
```

### 25. Sử dụng Octavia cơ bản

Đầu tiên, hãy tạo loadbalancer

```sh
apt -y install python3-octaviaclient
openstack subnet list
```

```sh
openstack loadbalancer create --name lb01 --vip-subnet-id private-subnet
```

Kiểm tra lại

```sh
openstack loadbalancer list
```

![](./images/Zed_7.png)

Thêm listener và pool cho LB và cấu hình LB sử dụng 2 backend là 2 webserver

```sh
openstack loadbalancer listener create --name listener01 --protocol TCP --protocol-port 80 lb01
openstack loadbalancer pool create --name pool01 --lb-algorithm ROUND_ROBIN --listener listener01 --protocol TCP
openstack server list --all
openstack loadbalancer member create --subnet-id private-subnet --address 192.168.100.21 --protocol-port 80 pool01
openstack loadbalancer member create --subnet-id private-subnet --address 192.168.100.153 --protocol-port 80 pool01
openstack loadbalancer member list pool01
```

Cấp IP cho LB

```sh
openstack floating ip create public
VIPPORT=$(openstack loadbalancer show lb01 | grep vip_port_id | awk {'print $4'})
openstack floating ip set --port $VIPPORT <floating-ip>
```

Kiểm tra:

```sh
curl <floating-ip>
```

![](./images/Zed_8.png)

### 26. Cài đặt và cấu hình Barbican (Control node)

Thêm user và endpoint cho Barbican

```sh
openstack user create --domain default --project service --password Welcome123 barbican
openstack role add --project service --user barbican admin
openstack service create --name barbican --description "OpenStack Key Manager" key-manager
export controller=openstack.baotrung.xyz
openstack endpoint create --region RegionOne key-manager public https://$controller:9311
openstack endpoint create --region RegionOne key-manager internal https://$controller:9311
openstack endpoint create --region RegionOne key-manager admin https://$controller:9311
```

Thêm user và database cho Barbican

```sh
mysql
```

```sh
create database barbican;
grant all privileges on barbican.* to barbican@'localhost' identified by 'Welcome123';
grant all privileges on barbican.* to barbican@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cài đặt Barbican

```sh
apt -y install barbican-api
```

Cấu hình Barbican

```sh
mv /etc/barbican/barbican.conf /etc/barbican/barbican.conf.bk
cat << EOF >> /etc/barbican/barbican.conf
[DEFAULT]
bind_host = 127.0.0.1
bind_port = 9311
host_href = https://openstack.baotrung.xyz:9311
log_file = /var/log/barbican/api.log
# MariaDB connection info
sql_connection = mysql+pymysql://barbican:Welcome123@openstack.baotrung.xyz/barbican
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[oslo_policy]
policy_file = /etc/barbican/policy.json
policy_default_rule = default

[secretstore]
namespace = barbican.secretstore.plugin
enabled_secretstore_plugins = store_crypto

[crypto]
namespace = barbican.crypto.plugin
enabled_crypto_plugins = simple_crypto

[simple_crypto_plugin]
kek = 'YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY='

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = barbican
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true
EOF
```

```sh
chmod 640 /etc/barbican/barbican.conf
chgrp barbican /etc/barbican/barbican.conf
vi /etc/apache2/conf-available/barbican-api.conf
```

```sh
# dòng 1,2 đổi thành
Listen 127.0.0.1:9311
Listen 127.0.0.1:9312
```

Chỉnh sửa nginx proxy

```sh
vi /etc/nginx/nginx.conf
```

```sh
# Thêm vào phần stream như mọi khi
    upstream barbican-api {
        server 127.0.0.1:9311;
    }
    server {
        listen 172.16.10.11:9311 ssl;
        proxy_pass barbican-api;
    }
    upstream barbican-api-2 {
        server 127.0.0.1:9312;
    }
    server {
        listen 172.16.10.11:9312 ssl;
        proxy_pass barbican-api-2;
    }
```

Sync DB và khởi động dịch vụ

```sh
su -s /bin/bash barbican -c "barbican-manage db upgrade"
systemctl restart apache2 nginx
```

Kiểm tra bằng cách tạo thử 1 secret key

```sh
openstack secret store --name secret01 --payload secretkey
```

![](./images/Zed_9.png)

### 27. Cài đặt và cấu hình Magnum (Control Node)

Thêm user và endpoint cho Magnum

```sh
openstack user create --domain default --project service --password Welcome123 magnum
openstack role add --project service --user magnum admin
openstack service create --name magnum --description "OpenStack Containers Orchestration" container-infra
export magnum_api=network.baotrung.xyz
openstack endpoint create --region RegionOne container-infra public https://$magnum_api:9511/v1
openstack endpoint create --region RegionOne container-infra internal https://$magnum_api:9511/v1
openstack endpoint create --region RegionOne container-infra admin https://$magnum_api:9511/v1
openstack domain create --description "Containers projects and users" magnum
openstack user create --domain magnum --password Welcome123 magnum_domain_admin
openstack role add --domain magnum --user-domain magnum --user magnum_domain_admin admin
```

Tạo database và user database

```sh
mysql
```

```sh
create database magnum;
grant all privileges on magnum.* to magnum@'localhost' identified by 'Welcome123';
grant all privileges on magnum.* to magnum@'%' identified by 'Welcome123';
flush privileges;
exit
```

### 28. Cài đặt và cấu hình Magnum (Network Node)

Cài đặt Magnum service trên Network node (nếu có câu hỏi nào trong khi cài đặt, hãy trả lời ```No```)

```sh
apt-get -y install magnum-api magnum-conductor python3-magnumclient
```

Cấu hình Magnum

```sh
mv /etc/magnum/magnum.conf /etc/magnum/magnum.conf.bk
cat << EOF >> /etc/magnum/magnum.conf
# create new
[DEFAULT]
state_path = /var/lib/magnum
log_dir = /var/log/magnum
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[api]
host = 127.0.0.1
port = 9511
enabled_ssl = false

[database]
# MariaDB connection info
connection = mysql+pymysql://magnum:Welcome123@openstack.baotrung.xyz/magnum

[certificates]
cert_manager_type = barbican

[cinder]
default_docker_volume_type = lvm-magnum

[cinder_client]
region_name = RegionOne

[magnum_client]
region_name = RegionOne

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
auth_version = v3
project_domain_name = default
user_domain_name = default
project_name = service
username = magnum
password = Welcome123
admin_user = magnum
admin_password = Welcome123
admin_tenant_name = service

[oslo_policy]
enforce_scope = false
enforce_new_defaults = false
policy_file = /etc/magnum/policy.json

[oslo_messaging_notifications]
driver = messagingv2

[trust]
trustee_domain_name = magnum
trustee_domain_admin_name = magnum_domain_admin
trustee_domain_admin_password = Welcome123
trustee_keystone_interface = public
EOF
```

```sh
chmod 640 /etc/magnum/magnum.conf
chgrp magnum /etc/magnum/magnum.conf
mkdir /var/lib/magnum/{tmp,certificates}
chown magnum. /var/lib/magnum/{tmp,certificates}
```

Cấu hình nginx proxy

```sh
vi /etc/nginx/nginx.conf
```

```sh
# Thêm phần sau vào [stream]
stream {
    upstream magnum-api {
        server 127.0.0.1:9511;
    }
    server {
        listen 172.16.10.13:9511 ssl;
        proxy_pass magnum-api;
    }
}
```

Sync DB và khởi động dịch vụ Magnum

```sh
su -s /bin/bash magnum -c "magnum-db-manage upgrade"
systemctl restart magnum-api magnum-conductor nginx
```

Kiểm tra Magnum status trên Control Node và tạo volume type cho Magnum

```sh
apt -y install python3-magnumclient
openstack coe service list
openstack volume type create lvm-magnum --public
```

### 29. Cách sử dụng Magnum cơ bản

Trên Control Node, tải về 1 VM image cho containers (image này sử dụng Fedora CoreOS) và thêm nó vào Glance

```sh
wget https://builds.coreos.fedoraproject.org/prod/streams/stable/builds/35.20220424.3.0/x86_64/fedora-coreos-35.20220424.3.0-openstack.x86_64.qcow2.xz
xz -dv fedora-coreos-35.20220424.3.0-openstack.x86_64.qcow2.xz
openstack image create Fedora-CoreOS --file=fedora-coreos-35.20220424.3.0-openstack.x86_64.qcow2 --disk-format=qcow2 --container-format=bare --property os_distro='fedora-coreos' --public
```

Tạo cluster template

```sh
openstack coe cluster template create k8s-cluster-template \
--image Fedora-CoreOS \
--external-network public \
--fixed-network private \
--fixed-subnet private-subnet \
--network-driver flannel \
--docker-storage-driver overlay2 \
--docker-volume-size 5 \
--master-flavor m1.medium \
--flavor m1.medium \
--dns-nameserver 8.8.8.8 \
--coe kubernetes
```

![](./images/Zed_10.png)

Tạo K8s cluster với 2 node:

```sh
openstack coe cluster create k8s-cluster \
--cluster-template k8s-cluster-template \
--master-count 1 \
--node-count 1 \
--timeout 120 \
--keypair mykey
```

```sh
# Kiểm tra trạng thái cluster
openstack coe cluster list
# Kiểm tra trạng thái stack của Heat
openstack stack list
# Kiểm tra trạng thái khởi tạo của từng thành phần
openstack stack list --nested | grep k8s-cluster
# Kiểm tra các node instance sau khi cluster khởi tạo thành công
openstack server list
```

![](./images/Zed_11.png)

Để truy nhập vào K8s Cluster, hãy thực hiện các bước sau

```sh
snap install kubectl --classic
openstack coe cluster config k8s-cluster
export KUBECONFIG=/root/config
kubectl get nodes
kubectl get pods -n kube-system
```

![](./images/Zed_12.png)

Thử deploy 1 deployment nginx

```sh
kubectl create deployment test-nginx --image=nginx --replicas=2
kubectl get pods -o wide
kubectl expose deployment test-nginx --type="NodePort" --port 80
kubectl get service test-nginx
```

![](./images/Zed_13.png)

Để người dùng bình thường có thể sử dụng được Magnum, ta sẽ phải cấp cho họ role ```heat_stack_owner```

```sh
openstack role add --project <project_name> --user <username> heat_stack_owner
```

Đồng thời, chỉnh sửa 1 chút trên node Network

```sh
vi /etc/neutron/policy.json
```

```sh
{
  "create_port:fixed_ips:subnet_id": "",
  "create_port:allowed_address_pairs": "",
  "create_port:allowed_address_pairs:ip_address": "",
}
```

```sh
systemctl restart neutron-server
```

### 30. Cài đặt magnum-ui và enable trên horizon

Tải source code của Magnum UI

```sh
git clone https://github.com/openstack/magnum-ui
```

Tạo 1 môi trường ảo và cài đặt các phụ thuộc của Horizon

```sh

```