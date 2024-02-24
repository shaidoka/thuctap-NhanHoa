# Cài đặt OpenStack Queens CentOS 7 (ko HA, ko Ceph)

## I. Cài đặt trên node controller

### 1. Cài đặt các thành phần cơ bản

Cấu hình IP, tắt selinux

Update

```sh
yum -y update
```

Cấu hình các mode sysctl: chỉnh sửa trong file ```/etc/sysctl.conf```

```sh
echo 'net.ipv4.conf.all.arp_ignore = 1'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.arp_announce = 2'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.rp_filter = 2'  >> /etc/sysctl.conf
echo 'net.netfilter.nf_conntrack_tcp_be_liberal = 1'  >> /etc/sysctl.conf

cat << EOF >> /etc/sysctl.conf
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

Tiếp theo, cài đặt các gói cần thiết:

```sh
yum -y install centos-release-openstack-queens
yum -y install crudini wget
yum -y install python-openstackclient openstack-selinux python2-PyMySQL
```

### 2. Đồng bộ thời gian

```sh
yum -y install chrony
sed -i 's/server 0.centos.pool.ntp.org iburst/ \
server 1.vn.pool.ntp.org iburst \
server 0.asia.pool.ntp.org iburst \
server 3.asia.pool.ntp.org iburst/g' /etc/chrony.conf
sed -i 's/server 1.centos.pool.ntp.org iburst/#/g' /etc/chrony.conf
sed -i 's/server 2.centos.pool.ntp.org iburst/#/g' /etc/chrony.conf
sed -i 's/server 3.centos.pool.ntp.org iburst/#/g' /etc/chrony.conf
sed -i 's/#allow 192.168.0.0\/16/allow 172.16.10.0\/24/g' /etc/chrony.conf
```

Đồng bộ thời gian

```sh
systemctl enable chronyd.service
systemctl start chronyd.service
chronyc sources
```

![](./images/OPS_Install_1.png)

### 3. Cài đặt và cấu hình memcache

Cài đặt

```sh
yum install -y memcached
sed -i "s/-l 127.0.0.1,::1/-l 172.16.10.11/g" /etc/sysconfig/memcached

systemctl enable memcached.service
systemctl restart memcached.service
```

### 4. Cài đặt và cấu hình MariaDB

Add repo MariaDB

```sh
curl -LsS -O https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
sudo bash mariadb_repo_setup --mariadb-server-version=10.6
```

Cài đặt MariaDB 10.6

```sh
yum install MariaDB-server MariaDB-client MariaDB-backup -y
```

Cấu hình MariaDB

```sh
cp /etc/my.cnf.d/server.cnf /etc/my.cnf.d/server.cnf.bk
rm -rf /etc/my.cnf.d/server.cnf
```

```sh
cat << EOF > /etc/my.cnf.d/openstack.cnf
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

### 5. Cài đặt và cấu hình RabbitMQ

Cài đặt RabbitMQ

```sh
yum install -y rabbitmq-server
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

![](./images/OPS_Install_2.png)

Tiếp tục cấu hình RabbitMQ

```sh
rabbitmqctl add_user openstack Welcome123
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
rabbitmqctl set_user_tags openstack administrator
```

### 6. Cài đặt Keystone

Tạo database cho Keystone

```sh
mysql -u root -p
```

```sh
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'Welcome123';
exit
```

Cài đặt Keystone

```sh
yum install openstack-keystone httpd mod_wsgi -y
```

Cấu hình VHost

```sh
cp /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.11/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 5000/Listen 172.16.10.11:5000/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 35357/Listen 172.16.10.11:35357/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/^Listen.*/Listen 172.16.10.11:80/g' /etc/httpd/conf/httpd.conf
```

Cấu hình Keystone

```sh
cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.bk
rm -rf /etc/keystone/keystone.conf
```

```sh
cat << EOF >> /etc/keystone/keystone.conf
[DEFAULT]
[assignment]
[auth]
[cache]
[catalog]
[cors]
[credential]
[database]
connection = mysql+pymysql://keystone:Welcome123@172.16.10.11/keystone
[domain_config]
[endpoint_filter]
[endpoint_policy]
[eventlet_server]
[federation]
[fernet_tokens]
[healthcheck]
[identity]
[identity_mapping]
[ldap]
[matchmaker_redis]
[memcache]
[oauth1]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
[policy]
[profiler]
[resource]
[revoke]
[role]
[saml]
[security_compliance]
[shadow_users]
[signing]
[token]
provider = fernet
[tokenless_auth]
[trust]
EOF
```

Phân quyền file cấu hình

```sh
chown root:keystone /etc/keystone/keystone.conf
```

Sync DB

```sh
su -s /bin/sh -c "keystone-manage db_sync" keystone
```

Thiết lập fernet key

```sh
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
```

Bootstrap keystone

```sh
keystone-manage bootstrap --bootstrap-password Welcome123 \
  --bootstrap-admin-url http://172.16.10.11:5000/v3/ \
  --bootstrap-internal-url http://172.16.10.11:5000/v3/ \
  --bootstrap-public-url http://172.16.10.11:5000/v3/ \
  --bootstrap-region-id RegionOne
```

Start httpd

```sh
systemctl enable httpd --now
```

Thiết lập biến môi trường

```sh
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://172.16.10.11:35357/v3
export OS_IDENTITY_API_VERSION=3
```

Tạo domain

```sh
openstack domain create --description "An Example Domain" example
openstack project create --domain default --description "Service Project" service
```

![](./images/OPS_Install_3.png)

Tạo project và user

```sh
openstack project create --domain default  --description "Demo Project" demo
openstack user create --domain default --password Welcome123 demo
```

![](./images/OPS_Install_4.png)

Tạo role và gắn role

```sh
openstack role create user
openstack role add --project demo --user demo user
```

Unset biến môi trường

```sh
unset OS_AUTH_URL OS_PASSWORD
```

Tạo token

```sh
openstack --os-auth-url http://172.16.10.11:35357/v3 \
  --os-project-domain-name Default --os-user-domain-name Default \
  --os-project-name admin --os-username admin token issue
Password: Welcome123
```

![](./images/OPS_Install_5.png)

Tạo file xác thực

```sh
cat << EOF >> admin-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.11:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF
```

```sh
cat << EOF >> demo-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.11:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF
```

Kiểm tra cấu hình keystone

```sh
. admin-openrc
openstack token issue
```

![](./images/OPS_Install_6.png)

### 7. Cài đặt Glance

Tạo DB

```sh
mysql -u root -p
CREATE DATABASE glance;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'Welcome123';
exit
```

Tạo user

```sh
openstack user create --domain default --password Welcome123 glance
openstack role add --project service --user glance admin
openstack service create --name glance --description "OpenStack Image" image
```

![](./images/OPS_Install_7.png)

Tạo endpoint

```sh
openstack endpoint create --region RegionOne image public http://172.16.10.11:9292
openstack endpoint create --region RegionOne image admin http://172.16.10.11:9292
openstack endpoint create --region RegionOne image internal http://172.16.10.11:9292
```

![](./images/OPS_Install_8.png)

Cài Glance

```sh
yum install -y openstack-glance
```

Cấu hình Glance API

```sh
cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.bk
rm -rf /etc/glance/glance-api.conf
```

```sh
cat << EOF >> /etc/glance/glance-api.conf
[DEFAULT]
bind_host = 172.16.10.11
registry_host = 172.16.10.11
[cors]
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.11/glance
[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
[image_format]
[keystone_authtoken]
auth_uri = http://172.16.10.11:5000
auth_url = http://172.16.10.11:5000
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_concurrency]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
[store_type_location_strategy]
[task]
[taskflow_executor]
EOF
```

Phân quyền file cấu hình

```sh
chown root:glance /etc/glance/glance-api.conf
chown root:glance /etc/glance/glance-registry.conf
```

Sync DB

```sh
su -s /bin/sh -c "glance-manage db_sync" glance
```

Enable và Start service

```sh
systemctl enable openstack-glance-api openstack-glance-registry
systemctl start openstack-glance-api openstack-glance-registry
```

Download và Upload image test ```cirros```

```sh
wget http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
openstack image create "cirros" \
  --file cirros-0.3.5-x86_64-disk.img \
  --disk-format qcow2 --container-format bare \
  --public
```

![](./images/OPS_Install_9.png)

Mặc định, image được lưu tại ```/var/lib/glance/images```

### 8. Cài đặt và cấu hình Nova

Tạo DB

```sh
mysql -u root -p
```

```sh
CREATE DATABASE nova_api;
CREATE DATABASE nova;
CREATE DATABASE nova_cell0;
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'%' IDENTIFIED BY 'Welcome123';
FLUSH PRIVILEGES;
exit
```

Tạo user và endpoint

```sh
openstack user create --domain default --password Welcome123 nova
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute
```

```sh
openstack endpoint create --region RegionOne compute public http://172.16.10.11:8774/v2.1
openstack endpoint create --region RegionOne compute admin http://172.16.10.11:8774/v2.1
openstack endpoint create --region RegionOne compute internal http://172.16.10.11:8774/v2.1
```

![](./images/OPS_Install_10.png)

```sh
openstack user create --domain default --password Welcome123 placement
openstack role add --project service --user placement admin
openstack service create --name placement --description "Placement API" placement
```

```sh
openstack endpoint create --region RegionOne placement public http://172.16.10.11:8778
openstack endpoint create --region RegionOne placement admin http://172.16.10.11:8778
openstack endpoint create --region RegionOne placement internal http://172.16.10.11:8778
```

![](./images/OPS_Install_11.png)

Tải các gói cần thiết của Nova

```sh
yum install -y openstack-nova-api openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler openstack-nova-placement-api
```

Cấu hình Nova

```sh
cp /etc/nova/nova.conf /etc/nova/nova.conf.bk
rm -rf /etc/nova/nova.conf
```

```sh
cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
my_ip = 172.16.10.11
enabled_apis = osapi_compute,metadata
use_neutron = True
osapi_compute_listen=172.16.10.11
metadata_host=172.16.10.11
metadata_listen=172.16.10.11
metadata_listen_port=8775
firewall_driver = nova.virt.firewall.NoopFirewallDriver
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672
[api]
auth_strategy = keystone
[api_database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.11/nova_api
[barbican]
[cache]
backend = oslo_cache.memcache_pool
enabled = true
memcache_servers = 172.16.10.11:11211
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.11/nova
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.11:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.11:5000/v3
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
[matchmaker_redis]
[metrics]
[mks]
[neutron]
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.11:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
discover_hosts_in_cells_interval = 300
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
novncproxy_host=172.16.10.11
enabled = true
vncserver_listen = 172.16.10.11
vncserver_proxyclient_address = 172.16.10.11
novncproxy_base_url = http://172.16.10.11:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Thêm vào file ```00-nova-placement-api.conf```

```sh
cat << EOF >> /etc/httpd/conf.d/00-nova-placement-api.conf

<Directory /usr/bin>
   <IfVersion >= 2.4>
      Require all granted
   </IfVersion>
   <IfVersion < 2.4>
      Order allow,deny
      Allow from all
   </IfVersion>
</Directory>
EOF
```

Cấu hình bind port cho nova-placement

```sh
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.11/g' /etc/httpd/conf.d/00-nova-placement-api.conf
sed -i -e 's/Listen 8778/Listen 172.16.10.11:8778/g' /etc/httpd/conf.d/00-nova-placement-api.conf
```

Restart service httpd

```sh
systemctl restart httpd
```

Sync DB

```sh
su -s /bin/sh -c "nova-manage api_db sync" nova
su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova
su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova
su -s /bin/sh -c "nova-manage db sync" nova
```

Enable và Start service

```sh
systemctl enable openstack-nova-api openstack-nova-scheduler openstack-nova-consoleauth openstack-nova-conductor openstack-nova-novncproxy
systemctl start openstack-nova-api openstack-nova-scheduler openstack-nova-consoleauth openstack-nova-conductor openstack-nova-novncproxy
```

Kiểm tra dịch vụ

```sh
openstack compute service list
```

![](./images/OPS_Install_12.png)

### 9. Cài đặt và cấu hình Neutron

Tạo DB cho Neutron

```sh
mysql -u root -p
```

```sh
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'Welcome123';
FLUSH PRIVILEGES;
exit
```

Tạo user và endpoint trên một node

```sh
openstack user create --domain default --password Welcome123 neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking" network
```

```sh
openstack endpoint create --region RegionOne network public http://172.16.10.11:9696
openstack endpoint create --region RegionOne network internal http://172.16.10.11:9696
openstack endpoint create --region RegionOne network admin http://172.16.10.11:9696
```

Cài dặt Neutron

```sh
yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y
```

Trong bài này, chúng ta sẽ sử dụng mô hình mạng provider (flat) sử dụng Linux Bridge DHCP agent và metadata agent được chạy trên node compute

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bk
rm -rf /etc/neutron/neutron.conf
```

```sh
cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
bind_host = 172.16.10.11
core_plugin = ml2
service_plugins = router
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672
auth_strategy = keystone
notify_nova_on_port_status_changes = true
notify_nova_on_port_data_changes = true
allow_overlapping_ips = True
dhcp_agents_per_network = 2
[agent]
[cors]
[database]
connection = mysql+pymysql://neutron:Welcome123@172.16.10.11/neutron
[keystone_authtoken]
auth_uri = http://172.16.10.11:5000
auth_url = http://172.16.10.11:35357
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
auth_url = http://172.16.10.11:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = Welcome123
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình file ml2

```sh
cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.bk
rm -rf /etc/neutron/plugins/ml2/ml2_conf.ini
```

```sh
cat << EOF >> /etc/neutron/plugins/ml2/ml2_conf.ini
[DEFAULT]
[l2pop]
[ml2]
type_drivers = flat,vlan,vxlan
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security
[ml2_type_flat]
[ml2_type_geneve]
[ml2_type_gre]
[ml2_type_vlan]
network_vlan_ranges = provider
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True
EOF
```

Cấu hình file LB agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.bk
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini
```

```sh
cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
[linux_bridge]
physical_interface_mappings = provider:eth1
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.12.11
l2_population = true
EOF
```

Trong đó:
- ```physical_interface_mappings```: Tên physical interface của đường provider
- ```local_ip```: Dải mạng sử dụng cho Data VM

Cấu hình trên file L3 agent

```sh
cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.bk
rm -rf /etc/neutron/l3_agent.ini
```

```sh
cat << EOF >> /etc/neutron/l3_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
[agent]
[ovs]
EOF
```

Chỉnh sửa cấu hình Nova

```sh
vi /etc/nova/nova.conf
```

```sh
[neutron]
url = http://172.16.10.11:9696
auth_url = http://172.16.10.11:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
service_metadata_proxy = true
metadata_proxy_shared_secret = Welcome123
```

Restart service nova-api

```sh
systemctl restart openstack-nova-api
```

Phân quyền file cấu hình

```sh
chown -R root:neutron /etc/neutron
```

Tạo symlink

```sh
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
```

Sync DB

```sh
su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
```

Enable và Start dịch vụ

```sh
systemctl restart openstack-nova-api openstack-nova-scheduler openstack-nova-consoleauth openstack-nova-conductor openstack-nova-novncproxy
```

Enable và Start Neutron, LinuxBridge

```sh
systemctl enable neutron-server neutron-linuxbridge-agent neutron-l3-agent
systemctl start neutron-server neutron-linuxbridge-agent neutron-l3-agent
```

### 10. Cài đặt và cấu hình Horizon

Cài đặt Horizon

```sh
yum install openstack-dashboard -y
```

Tạo file direct

```sh
filehtml=/var/www/html/index.html
touch $filehtml
cat << EOF >> $filehtml
<html>
<head>
<META HTTP-EQUIV="Refresh" Content="0.5; URL=http://172.16.10.11/dashboard">
</head>
<body>
<center> <h1>Redirecting to OpenStack Dashboard</h1> </center>
</body>
</html>
EOF
```

Backup cấu hình

```sh
cp /etc/openstack-dashboard/local_settings /etc/openstack-dashboard/local_settings.bk
```

Thay đổi cấu hình trong file ```/etc/openstack-dashboard/local_settings```

```sh
vi /etc/openstack-dashboard/local_settings
```

```sh
ALLOWED_HOSTS = ['*',]
OPENSTACK_API_VERSIONS = {
    "identity": 3,
    "image": 2,
    "volume": 2,
}
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'
```

Lưu ý thêm SESSION_ENGINE vào trên dòng CACHES như bên dưới

```sh
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
         'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
         'LOCATION': ['172.16.10.11:11211',],
    }
}
OPENSTACK_HOST = "172.16.10.11"
OPENSTACK_KEYSTONE_URL = "http://172.16.10.11:5000/v3"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"
```

**Lưu ý:** Nếu chỉ sử dụng provider ta chỉnh sửa các thông số sau

```sh
OPENSTACK_NEUTRON_NETWORK = {
    'enable_router': False,
    'enable_quotas': False,
    'enable_ipv6': False,
    'enable_distributed_router': False,
    'enable_ha_router': False,
    'enable_fip_topology_check': False,
}
```

```sh
TIME_ZONE = "Asia/Ho_Chi_Minh"
```

Chỉnh sửa vhost của OPS Dashboard

```sh
echo "WSGIApplicationGroup %{GLOBAL}" >> /etc/httpd/conf.d/openstack-dashboard.conf
```

Restart httpd và memecache:

```sh
systemctl restart httpd memcached
```

### 11. Cài đặt Cinder

**Sử dụng 1 phân vùng riêng để lưu các volume của máy ảo**

Tạo DB Cinder

```sh
mysql -u root -p
```

```sh
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'Welcome123';
FLUSH PRIVILEGES;
exit
```

Tạo service, endpoint, user

```sh
openstack user create --domain default --password Welcome123 cinder
openstack role add --project service --user cinder admin
openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2
openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3
```

```sh
openstack endpoint create --region RegionOne volumev2 public http://172.16.10.11:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne volumev2 internal http://172.16.10.11:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne volumev2 admin http://172.16.10.11:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne volumev3 public http://172.16.10.11:8776/v3/%\(project_id\)s
openstack endpoint create --region RegionOne volumev3 internal http://172.16.10.11:8776/v3/%\(project_id\)s
openstack endpoint create --region RegionOne volumev3 admin http://172.16.10.11:8776/v3/%\(project_id\)s
```

Cài đặt Keystone

```sh
yum install openstack-cinder targetcli python-keystone -y
```

Cài đặt và cấu hình Cinder volume với LVM

```sh
yum install -y lvm2
```

Khởi động dịch vụ LVM và cho phép khởi động cùng hệ thống

```sh
systemctl enable lvm2-lvmetad --now
```

Tạo LVM physical volume ```/dev/sdb1```

```sh
pvcreate /dev/sdb1
```

Tạo LVM volume group ```cinder volumes```

```sh
vgcreate cinder-volumes /dev/sdb1
```

Chỉnh sửa file ```lvm.conf```, để LVM chỉ scan ổ sdb cho block storage

```sh
vi /etc/lvm/lvm.conf
```

```sh
devices {
    ...
    filter = ["a/sdb/", "r/.*/"]
}
```

Cấu hình Cinder

```sh
cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bk
rm -rf /etc/cinder/cinder.conf
```

```sh
cat << EOF >> /etc/cinder/cinder.conf
[DEFAULT]
my_ip = 172.16.10.11
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672
auth_strategy = keystone
osapi_volume_listen = 172.16.10.11
enabled_backends = lvm
[backend]
[backend_defaults]
[barbican]
[brcd_fabric_example]
[cisco_fabric_example]
[coordination]
[cors]
[database]
connection = mysql+pymysql://cinder:Welcome123@172.16.10.11/cinder
[fc-zone-manager]
[healthcheck]
[key_manager]
[keystone_authtoken]
auth_uri = http://172.16.10.11:5000
auth_url = http://172.16.10.11:35357
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_id = default
user_domain_id = default
project_name = service
username = cinder
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[oslo_reports]
[oslo_versionedobjects]
[profiler]
[service_user]
[ssl]
[vault]
[lvm]
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_group = cinder-volumes
iscsi_protocol = iscsi
iscsi_helper = lioadm
volume_backend_name = lvm
EOF
```

Phân quyền file cấu hình 

```sh
chown root:cinder /etc/cinder/cinder.conf
```

Sync DB

```sh
su -s /bin/sh -c "cinder-manage db sync" cinder
```

Chỉnh sửa cấu hình Nova

```sh
vi /etc/nova/nova.conf
```

```sh
[cinder]
os_region_name = RegionOne
```

Restart service nova-api

```sh
systemctl restart openstack-nova-api
```

Enable và Restart dịch vụ

```sh
systemctl enable openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler
systemctl restart openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler
```

## Cài đặt trên node Compute 1

### 1. Cấu hình các thành phần cơ bản

Thiết lập đầy đủ hostname, hosts file, IP, tắt firewall, selinux,...

Cấu hình cho các mode sysctl

```sh
echo 'net.ipv4.conf.all.arp_ignore = 1'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.arp_announce = 2'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.rp_filter = 2'  >> /etc/sysctl.conf
echo 'net.netfilter.nf_conntrack_tcp_be_liberal = 1'  >> /etc/sysctl.conf
```

```sh
cat << EOF >> /etc/sysctl.conf
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.tcp_keepalive_time = 6
net.ipv4.tcp_keepalive_intvl = 3
net.ipv4.tcp_keepalive_probes = 6
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.default.rp_filter = 0
EOF
```

```sh
sysctl -p 
```

Khai báo các file hosts

```sh
echo "172.16.10.11 ctl1" >> /etc/hosts
echo "172.16.10.12 com1" >> /etc/hosts
echo "172.16.10.13 com2" >> /etc/hosts
```

Tải các gói cần thiết

```sh
yum -y install centos-release-openstack-queens
yum -y install crudini wget
yum -y install python-openstackclient openstack-selinux python2-PyMySQL
```

Cài đặt và cấu hình NTP

```sh
yum -y install chrony
VIP_MGNT_IP='172.16.10.11'
sed -i '/server/d' /etc/chrony.conf
echo "server $VIP_MGNT_IP iburst" >> /etc/chrony.conf
systemctl enable chronyd.service
systemctl restart chronyd.service
chronyc sources
```

Chỉnh sửa file repo QEMU của CentOS

```sh
sed -i 's|baseurl=http:\/\/mirror.centos.org\/$contentdir\/$releasever\/virt\/$basearch\/kvm-common\/|baseurl=http:\/\/mirror.centos.org\/centos\/7\/virt\/x86_64\/kvm-common\/|g' /etc/yum.repos.d/CentOS-QEMU-EV.repo
```

### 2. Cài đặt Nova

Cài đặt

```sh
yum install openstack-nova-compute libvirt-client -y
```

Cấu hình

```sh
cp /etc/nova/nova.conf  /etc/nova/nova.conf.bk
rm -rf /etc/nova/nova.conf
```

```sh
cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
enabled_apis = osapi_compute,metadata
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
[api]
auth_strategy = keystone
[api_database]
[barbican]
[cache]
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.11:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.11:5000/v3
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
virt_type = qemu
[matchmaker_redis]
[metrics]
[mks]
[neutron]
url = http://172.16.10.11:9696
auth_url = http://172.16.10.11:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.11:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
discover_hosts_in_cells_interval = 300
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
enabled = True
server_listen = 0.0.0.0
server_proxyclient_address = 172.16.10.12
novncproxy_base_url = http://172.16.10.11:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Phân quyền file cấu hình Nova

```sh
chown root:nova /etc/nova/nova.conf
```

Enable và Start service

```sh
systemctl enable libvirtd openstack-nova-compute
systemctl restart libvirtd openstack-nova-compute
```

### 3. Cài đặt Neutron

Cài đặt

```sh
yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y
```

Cấu hình

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bk 
rm -rf /etc/neutron/neutron.conf
```

```sh
cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672
auth_strategy = keystone
[agent]
[cors]
[database]
[keystone_authtoken]
auth_uri = http://172.16.10.11:5000
auth_url = http://172.16.10.11:35357
memcached_servers = 172.16.10.11:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình file LinuxBridge agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.bk
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini
```

```sh
cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
[linux_bridge]
physical_interface_mappings = provider:eth1
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.12.13
l2_population = true
EOF
```

Trong đó:
- ```physical_interface_mappings```: tên interface của đường **provider**
- ```local_ip```: IP của đường **DataVM**

Cấu hình DHCP agent

```sh
cp /etc/neutron/dhcp_agent.ini /etc/neutron/dhcp_agent.ini.bk
rm -rf /etc/neutron/dhcp_agent.ini
```

```sh
cat << EOF >> /etc/neutron/dhcp_agent.ini
[DEFAULT]
interface_driver = linuxbridge
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = true
force_metadata = True
[agent]
[ovs]
EOF
```

Cấu hình metadata agent

```sh
cp /etc/neutron/metadata_agent.ini /etc/neutron/metadata_agent.ini.bk
rm -rf /etc/neutron/metadata_agent.ini
```

```sh
cat << EOF >> /etc/neutron/metadata_agent.ini
[DEFAULT]
nova_metadata_host = 172.16.10.11
metadata_proxy_shared_secret = Welcome123
[agent]
[cache]
EOF
```

Phân quyền các file cấu hình của Neutron

```sh
chown root:neutron /etc/neutron/metadata_agent.ini /etc/neutron/neutron.conf /etc/neutron/dhcp_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini
```

Restart service Nova

```sh
systemctl restart libvirtd.service openstack-nova-compute
```

Enable và Restart Neutron

```sh
systemctl enable neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent
systemctl restart neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent
```

## Cài đặt trên Compute 2 

Tương tự compute 1

## Kết quả

![](./images/OPS_Install_13.png)

