# Install and Configure

Phần này sẽ mô tả cách cài đặt và cấu hình dịch vụ Container Infrastucture Management, hay gọi theo codename là ```magnum``` trên Controller Node.

Bài này cũng giả định rằng bạn đã làm việc với môi trường OpenStack với tối thiểu các thành phần sau: Identity Service, Image service, Compute Service, Networking Service, Block Storage service, Orchestration service.

Để cung cấp truy nhập vào K8s sử dụng native client (kubectl) thì magnum sử dụng TLS certificates. Để lưu trữ certificates, chúng tôi khuyến nghị rằng bạn nên sử dụng Key Manager service (codename [Barbican](https://docs.openstack.org/project-install-guide/key-manager/draft/)), hoặc bạn có thể giữ chúng trong database của magnum cũng được.

Optionally, bạn có thể cài đặt các thành phần sau:

- [Load Balancer as a Service (LBaaS v2)](https://docs.openstack.org/ocata/networking-guide/config-lbaas.html) để tạo các clusters với nhiều masters
- [Bare Metal service](https://docs.openstack.org/ironic/latest/install/index.html/) để tạo baremetal clusters
- [Object Storage service](https://docs.openstack.org/swift/latest/install/index.html) để tạo private Docker registry cho người dùng
- [Telemetry Data Collection service](https://docs.openstack.org/ceilometer/latest/install/index.html) để định kỳ gửi metrics liên quan đến magnum

## Prerequisites

Bài này mô tả các bước ngắn gọn để cài đặt Magnum trên CentOS 7.

Trước khi cài đặt và cấu hình Container Infrastructure Management service, bạn phải tạo 1 database, service credentials, và API endpoints.

Truy cập vào database với user root:

```sh
mysql -u root -p
```

Tạo ```magnum``` database:

```sh
CREATE DATABASE magnum;
```

Thêm quyền phù hợp:

```sh
GRANT ALL PRIVILEGES ON magnum.* TO 'magnum'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON magnum.* TO 'magnum'@'%' \
  IDENTIFIED BY 'Welcome123';
```

Source ```admin``` credentials để truy nhập vào admin-only CLI:

```sh
. admin-openrc
```

Tạo ```magnum``` user:

```sh
openstack user create --domain default --password-prompt magnum
```

Thêm quyền ```admin``` cho ```magnum``` user:

```sh
openstack role add --project service --user magnum admin
```

Tạo ```magnum``` service entity

```sh
openstack service create --name magnum \
  --description "OpenStack Container Infrastructure Management Service" \
  container-infra
```

Tạo Container Infrastructure Management service API endpoints:

```sh
openstack endpoint create --region RegionOne \
  container-infra public http://CONTROLLER_IP:9511/v1
openstack endpoint create --region RegionOne \
  container-infra internal http://CONTROLLER_IP:9511/v1
openstack endpoint create --region RegionOne \
  container-infra admin http://CONTROLLER_IP:9511/v1
```

Magnum yêu cầu thêm thông tin trong Identity service để quản lý COE clusters. Đầu tiên hãy tạo ```magnum``` domain:

```sh
openstack domain create --description "Owns users and projects \
  created by magnum" magnum
```

Tạo user ```magnum_domain_admin``` để quản lý các projects và users trong ```magnum``` domain:

```sh
openstack user create --domain magnum --password-prompt \
  magnum_domain_admin
```

Thêm ```admin``` role để ```magnum_domain_admin``` user trong ```magnum``` domain để người dùng này có quyền quản lý của admin:

```sh
openstack role add --domain magnum --user-domain magnum --user \
  magnum_domain_admin admin
```

## Install and configure components

Cài đặt các gói cần thiết:

```sh
yum install openstack-magnum-api openstack-magnum-conductor python-magnumclient -y
```

Chỉnh sửa file config ```/etc/magnum/magnum.conf```

```sh
cp /etc/magnum/magnum.conf /etc/magnum/magnum.conf.bk
```

Trong phần ```[api]```, chỉnh sửa host

```sh
[api]
...
host = CONTROLLER_IP
```

Trong ```[ceriticates]``` section, chọn ```barbican``` (hoặc ```x509keypair``` nếu bạn chưa cài đặt barbican):

```sh
[certificates]
...
# cert_manager_type = barbican
cert_manager_type = x509keypair
```

Trong ```[database]``` section, chỉnh sửa:

```sh
[database]
...
connection = mysql+pymysql://magnum:MAGNUM_DBPASS@controller/magnum
```

Trong ```[keystone_authtoken]``` và ```[trust]``` section, cấu hình Identity service access:

```sh
[keystone_authtoken]
...
memcached_servers = 192.168.0.94:11211
auth_version = v3
www_authenticate_uri = http://192.168.0.94:5000/v3
project_domain_id = default
project_name = service
user_domain_id = default
password = Welcome123
username = magnum
auth_url = http://192.168.0.94:5000
auth_type = password
admin_user = magnum
admin_password = Welcome123
admin_tenant_name = service

[trust]
...
trustee_domain_name = magnum
trustee_domain_admin_name = magnum_domain_admin
trustee_domain_admin_password = Welcome123
trustee_keystone_interface = public
```

Trong ```[oslo_messaging_notifications]```, cấu hình driver:

```sh
[oslo_messaging_notifications]
...
driver = messagging
```

Trong ```[DEFAULT]``` section, cấu hình ```RabbitMQ``` messafge queue accessL

```sh
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@192.168.0.94:5672
````

Trong ```[oslo_concurrency]``` section, cấu hình lock_path:

```sh
[oslo_concurrency]
...
lock_path = /var/lib/magnum/tmp
```

Sync DB:

```sh
su -s /bin/sh -c "magnum-db-manage upgrade" magnum
```

Restart service:

```sh
systemctl enable openstack-magnum-api.service \
  openstack-magnum-conductor.service
systemctl restart openstack-magnum-api.service \
  openstack-magnum-conductor.service
```

Kiểm tra dịch vụ

```sh
openstack coe service list
```