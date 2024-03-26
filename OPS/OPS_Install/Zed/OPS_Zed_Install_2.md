# Cài đặt OpenStack Zed (Phần 2)

Mô hình tổng quan của bài lab này sẽ như sau:

```sh
------------+-----------------------------+-----------------------------+------------
            |                             |                             |
    eth0|172.16.10.11             eth0|172.16.10.13             eth0|172.16.11.12
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

### 11. Cấu hình Neutron trên Network node

Cài đặt các thành phần cơ bản của network node: chrony, tắt firewall, tắt selinux, network interface,...

Cấu hình user, endpoints, database cho Neutron trên Control Node

```sh
export netnode=network.baotrung.xyz
openstack user create --domain default --project service --password Welcome123 neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking service" network
openstack endpoint create --region RegionOne network public https://$netnode:9696
openstack endpoint create --region RegionOne network internal https://$netnode:9696
openstack endpoint create --region RegionOne network admin https://$netnode:9696
```

```sh
mysql
```

```sh
create database neutron_ml2;
grant all privileges on neutron_ml2.* to neutron@'localhost' identified by 'Welcome123';
grant all privileges on neutron_ml2.* to neutron@'network' identified by 'Welcome123';
grant all privileges on neutron_ml2.* to neutron@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cấu hình OpenStack Zed repository và cài đặt neutron trên network node:

```sh
apt-get -y install software-properties-common
add-apt-repository cloud-archive:zed
apt-get -y update && apt-get -y upgrade
apt-get -y install neutron-server neutron-plugin-ml2 python3-neutronclient ovn-central openvswitch-switch nginx libnginx-mod-stream
```

Cấu hình Neutron Server

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
connection = mysql+pymysql://neutron:password@openstack.baotrung.xyz/neutron_ml2

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
```

```sh
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
# IP address of this Network node
ovn_nb_connection = tcp:172.16.10.13:6641
ovn_sb_connection = tcp:172.16.10.13:6642
ovn_l3_scheduler = leastloaded
ovn_metadata_enabled = True
EOF
```

```sh
chmod 640 /etc/neutron/plugins/ml2/ml2_conf.ini
chgrp neutron /etc/neutron/plugins/ml2/ml2_conf.ini
```

```sh
vi /etc/default/openvswitch-switch
```

```sh
# Tại dòng 8: bỏ comment và sửa thành
OVS_CTL_OPTS="--ovsdb-server-options='--remote=ptcp:6640:127.0.0.1'"
```

Cấu hình Nginx 

```sh
unlink /etc/nginx/sites-enabled/default
vi /etc/nginx/nginx.conf
```

```sh
# Thêm đoạn sau vào cuối file
stream {
    upstream neutron-api {
        server 127.0.0.1:9696;
    }
    server {
        listen 172.16.10.13:9696 ssl;
        proxy_pass neutron-api;
    }
    ssl_certificate "/root/ssl/app.crt";
    ssl_certificate_key "/root/ssl/app.key";
}
```

Khởi động dịch vụ

```sh
systemctl restart openvswitch-switch
ovs-vsctl add-br br-int
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"
systemctl restart ovn-central ovn-northd
ovn-nbctl set-connection ptcp:6641:172.16.10.13 -- set connection . inactivity_probe=60000
ovn-sbctl set-connection ptcp:6642:172.16.10.13 -- set connection . inactivity_probe=60000
systemctl restart neutron-server nginx
```

### 12. Cấu hình Neutron trên Compute node

Cài đặt Neutron

```sh
apt -y install neutron-common neutron-plugin-ml2 neutron-ovn-metadata-agent ovn-host openvswitch-switch
```

Cấu hình Neutron

```sh
mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bk

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
core_plugin = ml2
service_plugins = ovn-router
auth_strategy = keystone
state_path = /var/lib/neutron
allow_overlapping_ips = True
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz

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

[oslo_concurrency]
lock_path = $state_path/lock
EOF
```

```sh
chmod 640 /etc/neutron/neutron.conf
chgrp neutron /etc/neutron/neutron.conf
mv /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.bk
```

```sh
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
# IP address of Network node
ovn_nb_connection = tcp:172.16.10.13:6641
ovn_sb_connection = tcp:172.16.10.13:6642
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
[DEFAULT]
# Tại dòng 2: Thêm cấu hình Nova API host
nova_metadata_host = openstack.baotrung.xyz
nova_metadata_protocol = https
metadata_proxy_shared_secret = Welcome123

# line 231 : change
[ovs]
ovsdb_connection = tcp:127.0.0.1:6640

# Thêm vào cuối
[agent]
root_helper = sudo neutron-rootwrap /etc/neutron/rootwrap.conf

[ovn]
ovn_sb_connection = tcp:172.16.10.13:6642
```

```sh
vi /etc/default/openvswitch-switch
```

```sh
# Tại dòng 8: bỏ comment và sửa thành
OVS_CTL_OPTS="--ovsdb-server-options='--remote=ptcp:6640:127.0.0.1'"
```

```sh
vi /etc/nova/nova.conf
```

```sh
# Thêm vào phần [DEFAULT]
vif_plugging_is_fatal = True
vif_plugging_timeout = 300

# Thêm vào cuối : Neutron auth info
[neutron]
auth_url = https://openstack.baotrung.xyz:5000
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

Khởi động dịch vụ

```sh
systemctl restart openvswitch-switch ovn-controller ovn-host
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
systemctl restart neutron-ovn-metadata-agent
systemctl restart nova-compute
ovs-vsctl set open . external-ids:ovn-remote=tcp:172.16.10.13:6642
ovs-vsctl set open . external-ids:ovn-encap-type=geneve
ovs-vsctl set open . external-ids:ovn-encap-ip=172.16.10.12
```

Đảm bảo là cấu hình sau đã được khai báo trong file ```/etc/nova/nova.conf``` của control node

```sh
[neutron]
auth_url = https://openstack.baotrung.xyz:5000
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

Khởi động lại dịch vụ trên Control node

```sh
systemctl restart nova-api
openstack network agent list
```

![](./images/Zed_1.png)

### 13. Cấu hình Neutron Network Geneve

Trong mô hình lab, các node network và compute có interface [eth1] UP nhưng không có IP, chúng ta sẽ sử dụng interface này để kết nói với bridge

Trên **Network Node** và **Compute Node**, cùng thực hiện các lệnh sau

```sh
# Thêm bridge
ovs-vsctl add-br br-eth1

# Thêm port vào bridge
ovs-vsctl add-port br-eth1 eth1

# Ánh xạ physnet1 vào bridge (physnet1 có thể đổi thành tên bất kỳ)
ovs-vsctl set open . external-ids:ovn-bridge-mappings=physnet1:br-eth1
```

Trên Control Node, tạo Virtual router

```sh
openstack router create router01
```

Tạo internal network liên kết với router trên

```sh
openstack network create private --provider-network-type geneve
```

Tạo subnet bên trong network kể trên

```sh
openstack subnet create private-subnet --network private \
--subnet-range 192.168.100.0/24 --gateway 192.168.100.1
```

Gán internal network vào router

```sh
openstack router add subnet router01 private-subnet
```

Tạo external network liên kết với router

```sh
openstack network create \
--provider-physical-network physnet1 \
--provider-network-type flat --external public
```

Tạo subnet trong external network

```sh
openstack subnet create public-subnet \
--network public --subnet-range 103.28.37.0/24 \
--allocation-pool start=103.28.37.172,end=103.28.37.175 \
--gateway 103.28.37.1 --dns-nameserver 8.8.8.8 --no-dhcp
```

Gán gateway vào router

```sh
openstack router set router01 --external-gateway public
```

Mặc định, tất cả các project đều có thể truy nhập external network, nhưng đối với internal network thì chỉ admin project có quyền truy nhập thôi. Vì vậy hãy cấp quyền truy nhập này cho project mà bạn muốn bằng cách sau

```sh
netID=$(openstack network list | grep private | awk '{ print $2 }')
prjID=$(openstack project list | grep tula_project | awk '{ print $2 }')
openstack network rbac create --target-project $prjID --type network --action access_as_shared $netID
```

Tạo 1 sshkey để connect đến instance (**cẩn thận không ghi đè mất ssh-key có sẵn**)

```sh
ssh-keygen -q -N ""
```

```sh
openstack keypair create --public-key ~/.ssh/mykey_id_rsa.pub mykey
```

Tạo instance

```sh
openstack server create --flavor m1.small --image Ubuntu2204 --security-group secgroup01 --nic net-id=$netID --key-name mykey Ubuntu-2204
```

Tạo floating IP

```sh
openstack floating ip create public
```

![](./images/Zed_2.png)

Thêm floating IP vào license

```sh
openstack server add floating ip <server-name-or-id> <floating-ip-address>
```

![](./images/Zed_3.png)

```sh
ssh -i ~/.ssh/mykey ubuntu@<floating-ip-address>
```

![](./images/Zed_4.png)

### 14. Cài đặt Horizon

Cài đặt Horizon trên Controller Node

```sh
apt -y install openstack-dashboard
```

Cấu hình Horizon

```sh
vi /etc/openstack-dashboard/local_settings.py
```

```sh
# Dòng 99: thay đổi thông tin memcached server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '172.16.10.11:11211',
    },
}

# Dòng 113: thêm mới
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Dòng 126: cấu hình Openstack host
OPENSTACK_HOST = "openstack.baotrung.xyz"
# Dòng 127: comment lại và thêm vào 1 dòng mới bên dưới như thế này
#OPENSTACK_KEYSTONE_URL = "http://%s/identity/v3" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_URL = "https://openstack.baotrung.xyz:5000/v3"

# Dòng 131: Thiết lập timezone
TIME_ZONE = "Asia/Ho_Chi_Minh"

# Thêm vào cuối các dòng sau
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'
```

```sh
vi /etc/apache2/sites-available/default-ssl.conf
```

```sh
# Dòng 32,33: Thay đổi đường dẫn tới certificate
SSLCertificateFile      /root/ssl/app.crt
SSLCertificateKeyFile   /root/ssl/app.key

# Dòng 42: Bỏ comment và chỉ định chained file
SSLCertificateChainFile /root/ssl/app.chained.crt
```

```sh
a2enmod ssl
a2ensite default-ssl
systemctl restart apache2 nova-api
```

![](./images/Zed_5.png)

### 15. Cài đặt và cấu hình Cinder (Control Node)

Trên Control Node, thêm user và endpoint cho Cinder

```sh
openstack user create --domain default --project service --password Welcome123 cinder
openstack role add --project service --user cinder admin
openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3
export controller=openstack.baotrung.xyz
openstack endpoint create --region RegionOne volumev3 public https://$controller:8776/v3/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev3 internal https://$controller:8776/v3/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev3 admin https://$controller:8776/v3/%\(tenant_id\)s
```

Thêm user và database trên MariaDB cho Cinder

```sh
mysql
```

```sh
create database cinder;
grant all privileges on cinder.* to cinder@'localhost' identified by 'Welcome123';
grant all privileges on cinder.* to cinder@'%' identified by 'Welcome123';
flush privileges;
exit
```

Cài đặt Cinder Service

```sh
apt -y install cinder-api cinder-scheduler python3-cinderclient
```

Cấu hình Cinder

```sh
mv /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bk
cat << EOF >> /etc/cinder/cinder.conf
[DEFAULT]
rootwrap_config = /etc/cinder/rootwrap.conf
api_paste_confg = /etc/cinder/api-paste.ini
state_path = /var/lib/cinder
auth_strategy = keystone
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz
enable_v3_api = True

# MariaDB connection info
[database]
connection = mysql+pymysql://cinder:Welcome123@openstack.baotrung.xyz/cinder

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = cinder
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[oslo_concurrency]
lock_path = $state_path/tmp
EOF
```

```sh
chmod 640 /etc/cinder/cinder.conf
chgrp cinder /etc/cinder/cinder.conf
sed -i "s/^Listen/Listen 127.0.0.1:8776/g" /etc/apache2/conf-available/cinder-wsgi.conf
```

Cấu hình nginx

```sh
# Thêm đoạn cấu hình sau vào [stream] section
    upstream cinder-api {
        server 127.0.0.1:8776;
    }
    server {
        listen 172.16.10.11:8776 ssl;
        proxy_pass cinder-api;
    }
```

Sync DB và khởi động dịch vụ

```sh
su -s /bin/bash cinder -c "cinder-manage db sync"
systemctl restart cinder-scheduler apache2 nginx
systemctl enable cinder-scheduler
echo "export OS_VOLUME_API_VERSION=3" >> ~/keystonerc
source ~/keystonerc
```

### 16. Cài đặt và cấu hình Cinder (Network Node)

Cài đặt Cinder Volume service

```sh
apt -y install cinder-volume python3-mysqldb
```

```sh
mv /etc/cinder/cinder.conf /etc/cinder/cinder.conf.org

cat << EOF >> /etc/cinder/cinder.conf
# create new
[DEFAULT]
# define IP address
my_ip = 172.16.11.13
rootwrap_config = /etc/cinder/rootwrap.conf
api_paste_confg = /etc/cinder/api-paste.ini
state_path = /var/lib/cinder
auth_strategy = keystone
# RabbitMQ connection info
transport_url = rabbit://openstack:Welcome123@openstack.baotrung.xyz
enable_v3_api = True
# Glance connection info
glance_api_servers = https://openstack.baotrung.xyz:9292
# OK with empty value now
enabled_backends =

# MariaDB connection info
[database]
connection = mysql+pymysql://cinder:Welcome123@openstack.baotrung.xyz/cinder

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = https://openstack.baotrung.xyz:5000
auth_url = https://openstack.baotrung.xyz:5000
memcached_servers = openstack.baotrung.xyz:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = cinder
password = Welcome123
# if using self-signed certs on Apache2 Keystone, turn to [true]
insecure = true

[oslo_concurrency]
lock_path = $state_path/tmp
EOF
```

```sh
chmod 640 /etc/cinder/cinder.conf
chgrp cinder /etc/cinder/cinder.conf
systemctl restart cinder-volume
systemctl enable cinder-volume
```

### 17. Cấu hình Storage sử dụng LVM (Storage Node)

Tạo 1 volume group cho Cinder

```sh
pvcreate /dev/sdb1
vgcreate -s 32M vg_volume01 /dev/sdb1
```

Cấu hình Cinder volume

```sh
apt -y install targetcli-fb python3-rtslib-fb
vi /etc/cinder/cinder.conf

# Chỉnh sửa giá trị dựa trên loại storage backend sử dụng
enabled_backends = lvm

# Thêm vào cuối
[lvm]
target_helper = lioadm
target_protocol = iscsi
target_ip_address = $my_ip
# volume group name created on [1]
volume_group = vg_volume01
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volumes_dir = $state_path/volumes
```

```sh
systemctl restart cinder-volume
```

Cấu hình Nova trên **Compute Node**

```sh
cat << EOF >> /etc/nova/nova.conf
[cinder]
os_region_name = RegionOne
EOF
```

```sh
systemctl restart nova-compute
```

Tạo thử volume

```sh
echo "export OS_VOLUME_API_VERSION=3" >> ~/keystonerc
source ~/keystonerc
openstack volume create --size 5 disk01
```

Để add volume vào instance, hãy sử dụng lệnh

```sh
openstack server add volume Ubuntu-2204 disk01
```