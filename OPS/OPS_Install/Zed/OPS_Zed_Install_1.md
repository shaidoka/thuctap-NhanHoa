# Cài đặt OpenStack Zed

Mô hình tổng quan của bài lab này sẽ như sau:

```sh
------------+-----------------------------+-----------------------------+------------
            |                             |                             |
    eth0|172.16.10.11             eth0|172.16.10.13             eth0|172.16.11.12
+-----------+-----------+     +-----------+-----------+     +-----------+-----------+
|   [ dlp.srv.world ]   |     | [ network.srv.world ] |     |  [ node01.srv.world ] |
|     (Control Node)    |     |     (Network Node)    |     |     (Compute Node)    |
|                       |     |                       |     |                       |
|  MariaDB    RabbitMQ  |     |      Open vSwitch     |     |        Libvirt        |
|  Memcached  Nginx     |     |     Neutron Server    |     |      Nova Compute     |
|  Keystone   httpd     |     |      OVN-Northd       |     |      Open vSwitch     |
|  Glance     Nova API  |     |         Nginx         |     |   OVN Metadata Agent  |
|                       |     |                       |     |     OVN-Controller    |
+-----------------------+     +-----------------------+     +-----------------------+
```


### 1. Cài đặt các thành phần cơ bản

Cấu hình IP, tắt selinux

Update

```sh
apt-get update -y && apt-get upgrade -y
```

Cấu hình các mode sysctl: chỉnh sửa trong file ```/etc/sysctl.conf```

```sh
cat << EOF >> /etc/sysctl.conf
net.ipv4.conf.all.arp_ignore = 1
net.ipv4.conf.all.arp_announce = 2
net.ipv4.conf.all.rp_filter = 2
net.netfilter.nf_conntrack_tcp_be_liberal = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.tcp_keepalive_time = 6
net.ipv4.tcp_keepalive_intvl = 3
net.ipv4.tcp_keepalive_probes = 6
net.ipv4.ip_forward = 1
net.ipv4.conf.default.rp_filter = 0
EOF
```

Kiểm tra:

```sh
sysctl -p
```

Khai báo các host

```sh
cat << EOF > /etc/hosts
172.16.10.11 ctl1
172.16.10.12 com1
172.16.10.13 com2
EOF
```

Tạo SSH key và copy sang các node compute khác:

```sh
ssh-keygen
ssh-copy-id root@172.16.10.12
ssh-copy-id root@172.16.10.13
scp /root/.ssh/id_rsa root@172.16.10.12:/root/.ssh/
scp /root/.ssh/id_rsa root@172.16.10.13:/root/.ssh/
```

Đứng từ node control ssh sang node com không cần password là ok

### 2. Đồng bộ thời gian

```sh
apt-get -y install chrony
```

Đồng bộ thời gian

```sh
systemctl enable chronyd.service
systemctl start chronyd.service
chronyc sources
```

### 3. Cài đặt và cấu hình MariaDB

Add repo MariaDB

```sh
apt-get -y install mariadb-server mariadb-client mariadb-backup
```

Cấu hình MariaDB

```sh
cp /etc/mysql/mariadb.conf.d/50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf.bk
rm -f /etc/mysql/mariadb.conf.d/50-server.cnf
```

```sh
cat << EOF > /etc/mysql/mariadb.conf.d/50-server.cnf
[mysqld]
bind-address = 172.16.10.11
default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
EOF
```

Restart service

```sh
systemctl enable mariadb
systemctl restart mariadb
```

Đặt password cho user mysql

```sh
mariadb-secure-installation
```

### 4. Cấu hình OpenStack Zed repository

```sh
apt-get -y install software-properties-common
add-apt-repository cloud-archive:zed
apt-get -y update && apt-get -y upgrade
```

### 4. Cài đặt RabbitMQ và Memcached

Cài đặt RabbitMQ, Memcached, Nginx

```sh
apt -y install rabbitmq-server memcached python3-pymysql nginx libnginx-mod-stream
```

Cấu hình rabbitmq

```sh
systemctl enable rabbitmq-server --now
rabbitmq-plugins enable rabbitmq_management
systemctl restart rabbitmq-server
curl -O http://localhost:15672/cli/rabbitmqadmin
chmod a+x rabbitmqadmin
mv rabbitmqadmin /usr/sbin/
rabbitmqadmin list users
```

Tiếp tục cấu hình RabbitMQ

```sh
rabbitmqctl add_user openstack Welcome123
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
rabbitmqctl set_user_tags openstack administrator
```

Cấu hình memcached

```sh
sed -i "s/-l 127.0.0.1,::1/-l 172.16.10.11/g" /etc/memcached.conf

systemctl enable memcached.service
systemctl restart memcached.service
```

Tắt web mặc định của nginx

```sh
unlink /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx
```

### 5. Cài đặt Keystone

Thêm user và database cho Keystone

```sh
mysql
```

```sh
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'Welcome123';
flush privileges;
exit
```

Cài đặt Keystone

```sh
apt-get -y install keystone python3-openstackclient apache2 libapache2-mod-wsgi-py3 python3-oauth2client
```

Cấu hình Keystone

```sh
cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.bk
```

```sh
vi /etc/keystone/keystone.conf
```

```sh
# Tại dòng 444: chỉnh sửa memcached server
memcache_servers = 172.16.10.11:11211
# Tại dòng 661: chỉnh sửa thông tin mariadb
connection = mysql+pymysql://keystone:Welcome123@172.16.10.11/keystone
# Dòng 2641: bỏ comment
provider = fernet
```

Sync db

```sh
su -s /bin/bash keystone -c "keystone-manage db_sync"
```

Khởi tạo fernet key

```sh
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
```

Boostrap Keystone

```sh
export controller=openstack.baotrung.xyz
keystone-manage bootstrap --bootstrap-password Welcome123 \
--bootstrap-admin-url https://$controller:5000/v3/ \
--bootstrap-internal-url https://$controller:5000/v3/ \
--bootstrap-public-url https://$controller:5000/v3/ \
--bootstrap-region-id RegionOne
```

Tạo SSL self-signed với openssl

Tạo private key cho CA:

```sh
openssl genrsa -des3 -out rootCA.key 2048
```

Tạo file pem từ private key:

```sh
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1825 -out rootCA.pem
```

Tạo 1 file ```openssl.cnf``` để cấu hình thêm thông tin SAN như sau:

```sh
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
[req_distinguished_name]
countryName = VN
countryName_default = VN
stateOrProvinceName = HN
stateOrProvinceName_default = HN
localityName = HN
localityName_default = HN
organizationalUnitName = NhanHoa
organizationalUnitName_default = IT
commonName = *.baotrung.xyz
commonName_max = 64
[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = *.baotrung.xyz
DNS.2 = *.prod.baotrung.xyz
DNS.3 = *.monitor.baotrung.xyz
```

Tạo file key:

```sh
sudo openssl genrsa -out app.key 2048
```

Tạo CSR từ file key và config trên:

```sh
sudo openssl req -new -out app.csr -key app.key -config openssl.cnf
```

Giờ đóng dấu cho file CSR vừa tạo:

```sh
sudo openssl x509 -req -days 3650 -in app.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out app.crt -extensions v3_req -extfile openssl.cnf
```

Cấu hình Apache

```sh
sed -i '70s/^/ServerName openstack.baotrung.xyz/g' /etc/apache2/apache2.conf
```

```sh
vi /etc/apache2/sites-available/keystone.conf
```

```sh
Listen 5000

<VirtualHost *:5000>
# Thêm đoạn cấu hình SSL/TLS
    SSLEngine on
    SSLHonorCipherOrder on
    SSLCertificateFile /root/ssl/app.crt
    SSLCertificateKeyFile /root/ssl/app.key
    WSGIScriptAlias / /usr/bin/keystone-wsgi-public

```

```sh
a2enmod ssl
a2dissite 000-default.conf
sed -i '70s/Include ports.conf/#Include ports.conf/g' /etc/apache2/apache2.conf
systemctl restart apache2
```

Khai báo biến môi trường

```sh
cat << EOF >> ~/keystonerc
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=https://openstack.baotrung.xyz:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export PS1='\u@\h \W(keystone)\$ '
EOF
```

```sh
chmod 600 ~/keystonerc
source ~/keystonerc
echo "source ~/keystonerc " >> ~/.bashrc
```

Tạo Service Project

```sh
openstack project create --domain default --description "Service Project" service --insecure
```

### 6. Cài đặt Glance

Thêm user và endpoint cho Glance

```sh
openstack user create --domain default --project service --password Welcome123 glance
openstack role add --project service --user glance admin
openstack service create --name glance --description "OpenStack Image service" image
openstack endpoint create --region RegionOne image public https://$controller:9292
openstack endpoint create --region RegionOne image internal https://$controller:9292
openstack endpoint create --region RegionOne image admin https://$controller:9292
```

Tạo database Glance

```sh
mysql
```

```sh
create database glance;
grant all privileges on glance.* to glance@'localhost' identified by 'Welcome123';
grant all privileges on glance.* to glance@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cài đặt Glance

```sh
apt-get -y install glance
```

Cấu hình Glance

```sh
mv /etc/glance/glance-api.conf /etc/glance/glance-api.conf.bk
```

```sh
cat << EOF >> /etc/glance/glance-api.conf
[DEFAULT]
bind_host = 127.0.0.1
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/

[database]
# MariaDB connection info
connection = mysql+pymysql://glance:Welcome123@openstack.baotrung.xyz/glance

# keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[paste_deploy]
flavor = keystone
EOF
```

```sh
chmod 640 /etc/glance/glance-api.conf
chown root:glance /etc/glance/glance-api.conf
su -s /bin/bash glance -c "glance-manage db_sync"
systemctl restart glance-api
systemctl enable glance-api
```

Cấu hình nginx proxy

```sh
cat << EOF >> /etc/nginx/nginx.conf
stream {
    upstream glance-api {
        server 127.0.0.1:9292;
    }
    server {
        listen 172.16.10.11:9292 ssl;
        proxy_pass glance-api;
    }
    ssl_certificate "/root/ssl/app.crt";
    ssl_certificate_key "/root/ssl/app.key";
}
```

Để kiểm tra, ta thử tạo 1 VM image ubuntu

```sh
wget http://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64.img
```

```sh
modprobe nbd
qemu-nbd --connect=/dev/nbd0 ubuntu-22.04-server-cloudimg-amd64.img
```

```sh
mount /dev/nbd0p1 /mnt
```

```sh
vi /mnt/etc/cloud/cloud.cfg

# Thêm vào dòng 13
ssh_pwauth: True
chpasswd: { expire: False }
```

```sh
umount /mnt
qemu-nbd --disconnect /dev/nbd0p1
```

Thêm image vào Glance

```sh
openstack image create "Ubuntu2204" --file ubuntu-22.04-server-cloudimg-amd64.img --disk-format qcow2 --container-format bare --public
```

### 7. Cài đặt Nova

Thêm user và endpoint cho Nova

```sh
openstack user create --domain default --project service --password Welcome123 nova
openstack role add --project service --user nova admin
openstack user create --domain default --project service --password Welcome123 placement
openstack role add --project service --user placement admin
openstack service create --name nova --description "OpenStack Compute service" compute
openstack service create --name placement --description "OpenStack Compute Placement service" placement
openstack endpoint create --region RegionOne compute public https://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute internal https://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute admin https://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne placement public https://$controller:8778
openstack endpoint create --region RegionOne placement internal https://$controller:8778
openstack endpoint create --region RegionOne placement admin https://$controller:8778
```

Thêm database và user database cho Nova

```sh
mysql
create database nova;
grant all privileges on nova.* to nova@'localhost' identified by 'Welcome123';
grant all privileges on nova.* to nova@'%' identified by 'Welcome123';
create database nova_api;
grant all privileges on nova_api.* to nova@'localhost' identified by 'Welcome123';
grant all privileges on nova_api.* to nova@'%' identified by 'Welcome123';
create database placement;
grant all privileges on placement.* to placement@'localhost' identified by 'Welcome123';
grant all privileges on placement.* to placement@'%' identified by 'Welcome123';
create database nova_cell0;
grant all privileges on nova_cell0.* to nova@'localhost' identified by 'Welcome123';
grant all privileges on nova_cell0.* to nova@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cài đặt Nova

```sh
apt-get -y install nova-api nova-conductor nova-scheduler nova-novncproxy placement-api python3-novaclient
```

Cấu hình Nova

```sh
mv /etc/nova/nova.conf /etc/nova/nova.conf.bk

cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
osapi_compute_listen = 127.0.0.1
osapi_compute_listen_port = 8774
metadata_listen = 127.0.0.1
metadata_listen_port = 8775
state_path = /var/lib/nova
enabled_apis = osapi_compute,metadata
log_dir = /var/log/nova
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[api]
auth_strategy = keystone

[vnc]
enabled = True
novncproxy_host = 127.0.0.1
novncproxy_port = 6080
novncproxy_base_url = https://openstack.baotrung.xyz:6080/vnc_auto.html

# Glance connection info
[glance]
api_servers = https://openstack.baotrung.xyz:9292

[oslo_concurrency]
lock_path = $state_path/tmp

# MariaDB connection info
[api_database]
connection = mysql+pymysql://nova:Welcome123@openstack.baotrung.xyz/nova_api

[database]
connection = mysql+pymysql://nova:Welcome123@openstack.baotrung.xyz/nova

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[placement]
auth_url = https://openstack.baotrung.xyz:5000
os_region_name = RegionOne
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = placement
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[wsgi]
api_paste_config = /etc/nova/api-paste.ini
EOF
```

```sh
chmod 640 /etc/nova/nova.conf
chgrp nova /etc/nova/nova.conf
```

```sh
mv /etc/placement/placement.conf /etc/placement/placement.conf.bk

cat << EOF >> /etc/placement/placement.conf
[DEFAULT]
debug = false

[api]
auth_strategy = keystone

[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = placement
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[placement_database]
connection = mysql+pymysql://placement:Welcome123@openstack.baotrung.xyz/placement
EOF
```

```sh
sed -i "s/^Listen/Listen 127.0.0.1:8778/g" /etc/apache2/sites-enabled/placement-api.conf
chmod 640 /etc/placement/placement.conf
chgrp placement /etc/placement/placement.conf
```

Cấu hình Nginx proxy

```sh
vi /etc/nginx/nginx.conf
```

```sh
# Thêm vào phần [stream]
stream {
    upstream glance-api {
        server 127.0.0.1:9292;
    }
    server {
        listen 172.16.10.11:9292 ssl;
        proxy_pass glance-api;
    }
    upstream nova-api {
        server 127.0.0.1:8774;
    }
    server {
        listen 172.16.10.11:8774 ssl;
        proxy_pass nova-api;
    }
    upstream nova-metadata-api {
        server 127.0.0.1:8775;
    }
    server {
        listen 172.16.10.11:8775 ssl;
        proxy_pass nova-metadata-api;
    }
    upstream placement-api {
        server 127.0.0.1:8778;
    }
    server {
        listen 172.16.10.11:8778 ssl;
        proxy_pass placement-api;
    }
    upstream novncproxy {
        server 127.0.0.1:6080;
    }
    server {
        listen 172.16.10.11:6080 ssl;
        proxy_pass novncproxy;
    }
    ssl_certificate "/root/ssl/app.crt";
    ssl_certificate_key "/root/ssl/app.key";
}
```

Thêm data vào database và khởi động dịch vụ Nova

```sh
su -s /bin/bash placement -c "placement-manage db sync"
su -s /bin/bash nova -c "nova-manage api_db sync"
su -s /bin/bash nova -c "nova-manage cell_v2 map_cell0"
su -s /bin/bash nova -c "nova-manage db sync"
su -s /bin/bash nova -c "nova-manage cell_v2 create_cell --name cell1"
systemctl restart nova-api nova-conductor nova-scheduler nova-novncproxy
systemctl enable nova-api nova-conductor nova-scheduler nova-novncproxy
systemctl restart apache2 nginx
```

Kiểm tra trạng thái dịch vụ

```sh
openstack compute service list
```

### 8. Cấu hình compute node

Cấu hình các thành phần cơ bản: update os, ssh-key, file hosts, chrony, firewall, selinux,...

Thêm OpenStack Zed repository

```sh
apt-get -y install software-properties-common
add-apt-repository cloud-archive:zed
apt-get -y update && apt-get -y upgrade
```

Cài đặt KVM Hypervisor

```sh
apt-get -y install qemu-kvm libvirt-daemon-system libvirt-daemon virtinst bridge-utils libosinfo-bin
```

Cài đặt Nova

```sh
apt-get -y install nova-compute nova-compute-kvm qemu-system-data
```

Cấu hình Nova

```sh
mv /etc/nova/nova.conf /etc/nova/nova.conf.bk

cat << EOF >> /etc/nova/nova.conf

[DEFAULT]
state_path = /var/lib/nova
enabled_apis = osapi_compute,metadata
log_dir = /var/log/nova
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[api]
auth_strategy = keystone

[vnc]
enabled = True
# IP address compute instances listen
# specify this node's IP
server_listen = 172.16.10.12
server_proxyclient_address = 172.16.10.12
novncproxy_base_url = https://openstack.baotrung.xyz:6080/vnc_auto.html

# Glance connection info
[glance]
api_servers = https://openstack.baotrung.xyz:9292

[oslo_concurrency]
lock_path = $state_path/tmp

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[placement]
auth_url = https://openstack.baotrung.xyz:5000
os_region_name = RegionOne
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = placement
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[wsgi]
api_paste_config = /etc/nova/api-paste.ini
EOF
```

```sh
sed -i 's/virt_type=kvm/virt_type=qemu/g' /etc/nova/nova-compute.conf
```

```sh
chmod 640 /etc/nova/nova.conf
chgrp nova /etc/nova/nova.conf
systemctl restart nova-compute
```

Check trạng thái của service, trên controller node thực hiện lệnh sau:

```sh
su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"
openstack compute service list
```

### 9. Cấu hình Neutron

Thêm user và service cho Neutron

```sh
openstack user create --domain default --project service --password Welcome123 neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking service" network
openstack endpoint create --region RegionOne network public https://openstack.baotrung.xyz:9696
openstack endpoint create --region RegionOne network internal https://openstack.baotrung.xyz:9696
openstack endpoint create --region RegionOne network admin https://openstack.baotrung.xyz:9696
```

Thêm user và database cho Neutron

```sh
mysql
```

```sh
create database neutron_ml2;
grant all privileges on neutron_ml2.* to neutron@'localhost' identified by 'Welcome123';
grant all privileges on neutron_ml2.* to neutron@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cài đặt Neutron

```sh
apt-get -y install neutron-server neutron-metadata-agent neutron-plugin-ml2 python3-neutronclient
```

Cấu hình Neutron

```sh
mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bk

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
bind_host = 127.0.0.1
bind_port = 9696
core_plugin = ml2
service_plugins = ovn-router
auth_strategy = keystone
state_path = /var/lib/neutron
allow_overlapping_ips = True
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

[agent]
root_helper = sudo /usr/bin/neutron-rootwrap /etc/neutron/rootwrap.conf

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[database]
connection = mysql+pymysql://neutron:Welcome123@openstack.baotrung.xyz/neutron_ml2

[nova]
auth_url = https://openstack.baotrung.xyz:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[oslo_concurrency]
lock_path = $state_path/tmp
EOF
```

```sh
chmod 640 /etc/neutron/neutron.conf
chgrp neutron /etc/neutron/neutron.conf
mv /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.bk

cat << EOF >> /etc/neutron/plugins/ml2/ml2_conf.ini
[DEFAULT]
debug = false

[ml2]
type_drivers = flat,geneve
tenant_network_types = geneve
mechanism_drivers = ovn
extension_drivers = port_security
overlay_ip_version = 4

[ml2_type_geneve]
vni_ranges = 1:65536
max_header_size = 38

[ml2_type_flat]
flat_networks = *

[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver

[ovn]
ovn_nb_connection = tcp:172.16.10.11:6641
ovn_sb_connection = tcp:172.16.10.11:6642
ovn_l3_scheduler = leastloaded
ovn_metadata_enabled = True
EOF
```

```sh
chmod 640 /etc/neutron/plugins/ml2/ml2_conf.ini
chgrp neutron /etc/neutron/plugins/ml2/ml2_conf.ini
vi /etc/neutron/neutron_ovn_metadata_agent.ini
```

```sh
# Dòng 2: Thêm Nova API host
nova_metadata_host = 172.16.10.11
nova_metadata_protocol = https
metadata_proxy_shared_secret = Welcome123
# Tại dòng 231, đổi thành
[ovs]
ovsdb_connection = tcp:127.0.0.1:6640
# Thêm vào cuối
[agent]
root_helper = sudo neutron-rootwrap /etc/neutron/rootwrap.conf
[ovn]
ovn_sb_connection = tcp:172.16.10.11:6642
```

```sh
vi /etc/default/openvswitch-switch
```

```sh
# Dòng 8: Bỏ comment và chỉnh sửa như sau
OVS_CTL_OPTS="--ovsdb-server-options='--remote=ptcp:6640:127.0.0.1'"
```

```sh
vi /etc/nova/nova.conf
```

```sh
# Thêm đoạn sau vào phần [DEFAULT]
vif_plugging_is_fatal = True
vif_plugging_timeout = 300

# Thêm đoạn sau vào cuối : Neutron auth info
[neutron]
auth_url = https://172.16.10.11:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
service_metadata_proxy = True
metadata_proxy_shared_secret = Welcome123
insecure = true
```

Chỉnh sửa cấu hình Nginx proxy

```sh
vi /etc/nginx/nginx.conf
```

```sh
# Thêm 2 đoạn cấu hình sau cho neutron vào phần [stream]
    upstream neutron-api {
        server 127.0.0.1:9696;
    }
    server {
        listen 172.16.10.11:9696 ssl;
        proxy_pass neutron-api;
    }
```

Khởi động Neutron

```sh
systemctl restart openvswitch-switch
ovs-vsctl add-br br-int
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"
systemctl restart ovn-central ovn-northd ovn-controller ovn-host
ovn-nbctl set-connection ptcp:6641:172.16.10.11 -- set connection . inactivity_probe=60000
ovn-sbctl set-connection ptcp:6642:172.16.10.11 -- set connection . inactivity_probe=60000
ovs-vsctl set open . external-ids:ovn-remote=tcp:172.16.10.11:6642
ovs-vsctl set open . external-ids:ovn-encap-type=geneve
ovs-vsctl set open . external-ids:ovn-encap-ip=172.16.10.11
systemctl restart neutron-server neutron-ovn-metadata-agent nova-api nova-compute nginx
```

Kiểm tra trạng thái dịch vụ

```sh
openstack network agent list
```

```sh
cat << EOF >> /etc/systemd/network/ens8.network
[Match]
Name=ens8

[Network]
LinkLocalAddressing=no
IPv6AcceptRA=no
EOF
```

```sh
ip link set ens8 up
ovs-vsctl add-br br-ens8
ovs-vsctl add-port br-ens8 ens8
ovs-vsctl set open . external-ids:ovn-bridge-mappings=physnet1:br-ens8
```

Tạo virtual network

```sh
projectID=$(openstack project list | grep service | awk '{print $2}')
openstack network create --project $projectID \
  --share --provider-network-type flat --provider-physical-network physnet1 sharednet1
openstack subnet create subnet1 --network sharednet1 \
  --project $projectID --subnet-range 103.28.37.0/24 \
  --allocation-pool start=103.28.37.172,end=103.28.37.175 \
  --gateway 103.28.37.1 --dns-nameserver 8.8.8.8
```

Kiểm tra

```sh
openstack network list
openstack subnet list
```

### 10. Test tạo instance

Tạo project

```sh
openstack project create --domain default --description "TuLA Project" tula_project
```

Tạo user

```sh
openstack user create --domain default --project tula_project --password Welcome123 tula_user
```

Tạo role

```sh
openstack role create CloudUser
```

Add role

```sh
openstack role add --project tula_project --user tula_user CloudUser
```

Tạo flavor

```sh
openstack flavor create --id 0 --vcpus 1 --ram 1024 --disk 10 m1.small
```

Tạo security group

```sh
openstack security group create secgroup01
openstack security group rule create --protocol icmp --ingress secgroup01
openstack security group rule create --protocol tcp --dst-port 22:22 secgroup01
```

Tạo 1 ssh keypair để connect đến instance

```sh
ssh-keygen -q -N ""
```

```sh
openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey
```

Tạo instance

```sh
netID=$(openstack network list | grep sharednet1 | awk '{ print $2 }')
openstack server create --flavor m1.small --image Ubuntu2204 --security-group secgroup01 --nic net-id=$netID --key-name mykey Ubuntu-2204
```