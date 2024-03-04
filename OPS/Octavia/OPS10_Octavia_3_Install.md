# Install and configure Octavia

## Prerequisites

Trước khi cài đặt và cấu hình dịch vụ, ta phải tạo 1 database, service credentials, và API endpoint

1. Tạo database:

```sh
mysql -u root -p
```

```sh
CREATE DATABASE octavia;
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'localhost' \
IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'%' \
IDENTIFIED BY 'Welcome123';
exit;
```

2. Source ```admin``` credentials để truy cập vào admin CLI:

```sh
. admin-openrc
```

3. Tạo Octavia service credentials:

```sh
openstack user create --domain default --password-prompt octavia
```

```sh
openstack role add --project service --user octavia admin
```

```sh
openstack service create --name octavia --description "OpenStack Octavia" load-balancer
```

4. Tạo LB service API endpoint:

```sh
openstack endpoint create --region RegionOne \
  load-balancer public http://controller:9876
openstack endpoint create --region RegionOne \
  load-balancer internal http://controller:9876
openstack endpoint create --region RegionOne \
  load-balancer admin http://controller:9876
```

5. Tạo tệp ```octavia-openrc```:

```sh
cat << EOF >> $HOME/octavia-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=service
export OS_USERNAME=octavia
export OS_PASSWORD=OCTAVIA_PASS
export OS_AUTH_URL=http://controller:5000
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export OS_VOLUME_API_VERSION=3
EOF
```

6. Source ```octavia``` credentials để truy nhập vào CLI

```sh
. $HOME/octavia-openrc
```

7. Tạo amphora image

Để tạo amphora image, hãy xem bài viết: [Building Octavia Amphora Images]()

8. Tải lên amphora image

```sh
openstack image create --disk-format qcow2 --container-format bare \
  --private --tag amphora \
  --file <path to the amphora image> amphora-x64-haproxy
```

9. Tạo flavor cho amphora image

```sh
openstack flavor create --id 200 --vcpus 1 --ram 1024 \
  --disk 2 "amphora" --private
```

## Install and configure components

1. Cài đặt các gói cần thiết

```sh
sudo yum install octavia-api octavia-health-manager octavia-housekeeping \
  octavia-worker python3-octavia python3-octaviaclient
```

Nếu các gói ```octavia-common``` và ```octavia-api``` hỏi bạn về việc cấu hình, hãy chọn No

2. Tạo certificate

```sh
git clone https://opendev.org/openstack/octavia.git
cd octavia/bin/
source create_dual_intermediate_CA.sh
sudo mkdir -p /etc/octavia/certs/private
sudo chmod 755 /etc/octavia -R
sudo cp -p etc/octavia/certs/server_ca.cert.pem /etc/octavia/certs
sudo cp -p etc/octavia/certs/server_ca-chain.cert.pem /etc/octavia/certs
sudo cp -p etc/octavia/certs/server_ca.key.pem /etc/octavia/certs/private
sudo cp -p etc/octavia/certs/client_ca.cert.pem /etc/octavia/certs
sudo cp -p etc/octavia/certs/client.cert-and-key.pem /etc/octavia/certs/private
```

Đối với môi trường Production, hãy tham khảo: [Octavia Cert Configuration](https://docs.openstack.org/octavia/latest/admin/guides/certificates.html)

3. Source ```octavia``` credentials

```sh
. octavia-openrc
```

4. Tạo security groups và các luật

```sh
openstack security group create lb-mgmt-sec-grp
openstack security group rule create --protocol icmp lb-mgmt-sec-grp
openstack security group rule create --protocol tcp --dst-port 22 lb-mgmt-sec-grp
openstack security group rule create --protocol tcp --dst-port 9443 lb-mgmt-sec-grp
openstack security group create lb-health-mgr-sec-grp
openstack security group rule create --protocol udp --dst-port 5555 lb-health-mgr-sec-grp
```

5. Tạo 1 cặp key để đăng nhập vào amphora instance

```sh
openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey
```

*Lưu ý: Nếu chưa có file id_rsa.pub thì có thể tạo bằng lệnh ssh-keygen*

6. Tạo tệp dhclient.conf cho dhclient

```sh
cd $HOME
sudo mkdir -m755 -p /etc/dhcp/octavia
sudo cp octavia/etc/dhcp/dhclient.conf /etc/dhcp/octavia
```

7. Tạo 1 network

```sh
OCTAVIA_MGMT_SUBNET=172.16.0.0/12
OCTAVIA_MGMT_SUBNET_START=172.16.0.100
OCTAVIA_MGMT_SUBNET_END=172.16.31.254
OCTAVIA_MGMT_PORT_IP=172.16.0.2

openstack network create lb-mgmt-net
openstack subnet create --subnet-range $OCTAVIA_MGMT_SUBNET --allocation-pool \
  start=$OCTAVIA_MGMT_SUBNET_START,end=$OCTAVIA_MGMT_SUBNET_END \
  --network lb-mgmt-net lb-mgmt-subnet

SUBNET_ID=$(openstack subnet show lb-mgmt-subnet -f value -c id)
PORT_FIXED_IP="--fixed-ip subnet=$SUBNET_ID,ip-address=$OCTAVIA_MGMT_PORT_IP"

MGMT_PORT_ID=$(openstack port create --security-group \
  lb-health-mgr-sec-grp --device-owner Octavia:health-mgr \
  --host=$(hostname) -c id -f value --network lb-mgmt-net \
PORT_FIXED_IP octavia-health-manager-listen-port)

MGMT_PORT_MAC=$(openstack port show -c mac_address -f value \
MGMT_PORT_ID)

sudo ip link add o-hm0 type veth peer name o-bhm0
NETID=$(openstack network show lb-mgmt-net -c id -f value)
BRNAME=brq$(echo $NETID|cut -c 1-11)
sudo brctl addif $BRNAME o-bhm0
sudo ip link set o-bhm0 up

sudo ip link set dev o-hm0 address $MGMT_PORT_MAC
sudo iptables -I INPUT -i o-hm0 -p udp --dport 5555 -j ACCEPT
sudo dhclient -v o-hm0 -cf /etc/dhcp/octavia
```

**Lưu ý:** Hãy lưu lại kết quả của ```BRNAME``` và ```MGMT_PORT_MAC``` vì bạn sẽ cần chúng sau

8. Bên dưới là các cài đặt cần thiết để tạo veth pair sau khi host reboot

Chỉnh sửa tệp ```/etc/systemd/network/o-hm0.network```

```sh
[Match]
Name=o-hm0

[Network]
DHCP=yes
```

Chỉnh sửa file ```/etc/systemd/system/octavia-interface.service```

```sh
[Unit]
Description=Octavia Interface Creator
Requires=neutron-linuxbridge-agent.service
After=neutron-linuxbridge-agent.service

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/opt/octavia-interface.sh start
ExecStop=/opt/octavia-interface.sh stop

[Install]
WantedBy=multi-user.target
```

Chỉnh sửa file ```/opt/octavia-interface.sh```:

```sh
#!/bin/bash

set -ex

MAC=$MGMT_PORT_MAC
BRNAME=$BRNAME

if [ "$1" == "start" ]; then
  ip link add o-hm0 type veth peer name o-bhm0
  brctl addif $BRNAME o-bhm0
  ip link set o-bhm0 up
  ip link set dev o-hm0 address $MAC
  ip link set o-hm0 up
  iptables -I INPUT -i o-hm0 -p udp --dport 5555 -j ACCEPT
elif [ "$1" == "stop" ]; then
  ip link del o-hm0
else
  brctl show $BRNAME
  ip a s dev o-hm0
fi
```

*Lưu ý các thông số $MGMT_PORT_MAC và $BRNAME được lấy từ bước 7*

9. Chỉnh sửa ```/etc/octavia/octavia.conf```:

Trong phần ```[database]```, sửa thông tin truy nhập database:

```sh
[database]
connection = mysql+pymysql://octavia:Welcome123@controller/octavia
```

Trong phần ```[DEFAULT]```, cấu hình trasport url cho RabbitMQ message broker:

```sh
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@controller
```

Trong phần ```[oslo_messaging]```, cấu hình transport url cho RabbitMQ message broker và topic name:

```sh
[oslo_messaging]
...
topic = octavia_prov
```

Trong phần ```[api_settings]```, cấu hình host IP và port bind:

```sh
[api_settings]
bind_host = 0.0.0.0
bind_port = 9876
```

Trong phần ```[keystone_authtoken]```, cấu hình identity service access:

```sh
[keystone_authtoken]
www_authenticate_uri = http://controller:5000
auth_url = http://controller:5000
memcached_servers = controller:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = octavia
password = Welcome123
```

Trong phần ```[service_auth]```, cấu hình credentials để sử dụng openstack service:

```sh
[service_auth]
auth_url = http://controller:5000
memcached_servers = controller:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = octavia
password = OCTAVIA_PASS
```

Trong phần ```[certificates]```, cấu hình đường dẫn tuyệt đối đến CA cert, private key và passphrases:

```sh
[certificates]
...
server_certs_key_passphrase = insecure-key-do-not-use-this-key
ca_private_key_passphrase = not-secure-passphrase
ca_private_key = /etc/octavia/certs/private/server_ca.key.pem
ca_certificate = /etc/octavia/certs/server_ca.cert.pem
```

Trong phần ```[haproxy_amphora]```, cấu hình client certificate và CA:

```sh
[haproxy_amphora]
...
server_ca = /etc/octavia/certs/server_ca-chain.cert.pem
client_cert = /etc/octavia/certs/private/client.cert-and-key.pem
```

Trong ```[health_manager]```, cấu hình IP và port number cho heartbeat:

```sh
[health_manager]
...
bind_port = 5555
bind_ip = 172.16.0.2
controller_ip_port_list = 172.16.0.2:5555
```

Trong ```[controller_worker]```, cấu hình worker settings:

```sh
[controller_worker]
...
amp_image_owner_id = <id of service project>
amp_image_tag = amphora
amp_ssh_key_name = mykey
amp_secgroup_list = <lb-mgmt-sec-grp_id>
amp_boot_network_list = <lb-mgmt-net_id>
amp_flavor_id = 200
network_driver = allowed_address_pairs_driver
compute_driver = compute_nova_driver
amphora_driver = amphora_haproxy_rest_driver
client_ca = /etc/octavia/certs/client_ca.cert.pem
```

10. Cập nhật DB

```sh
octavia-db-manage --config-file /etc/octavia/octavia.conf upgrade head
```

11. Restart service

```sh
systemctl restart octavia-api octavia-health-manager octavia-housekeeping octavia-worker
```