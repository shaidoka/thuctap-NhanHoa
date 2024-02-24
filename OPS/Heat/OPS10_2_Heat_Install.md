# Install Heat on CentOS 7

## Prerequisites

Trước khi cài đặt và cấu hình Orchestration, ta phải tạo credential cho database service và các API endpoint. Orchestration cũng cần thêm thông tin trong Identity service.

1. Để tạo database, hoàn thiện các bước sau đây:

- Sử dụng database access client để kết nối đến database server bằng user root

```sh
mysql -u root -p
```

- Tạo **heat** database:

```sh
CREATE DATABASE heat;
```

Cấp quyền truy cập phù hợp vào **heat** database:

```sh
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' \
  IDENTIFIED BY 'Welcome123';
```

- Thoát:

```sh
exit
```

2. Source admin credential để truy cập vào CLI của admin:

```sh
. admin-openrc
```

3. Để tạo service credentials, hoàn thiện các bước sau:

- Tạo **heat** user:

```sh
openstack user create --domain default --password-prompt heat
```

- Tạo **admin** role cho **heat** user

```sh
openstack role add --project service --user heat admin
```

- Tạo service cho **heat** và **heat-cfn**

```sh
openstack service create --name heat --description "Orchestration" orchestration

openstack service create --name heat-cfn --description "Orchestration" cloudformation
```

Tạo Orchestration service API endpoints:

```sh
openstack endpoint create --region RegionOne \
  orchestration public http://controller:8004/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
  orchestration internal http://controller:8004/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
  orchestration admin http://controller:8004/v1/%\(tenant_id\)s
```

```sh
openstack endpoint create --region RegionOne \
  cloudformation public http://controller:8000/v1

openstack endpoint create --region RegionOne \
  cloudformation internal http://controller:8000/v1

openstack endpoint create --region RegionOne \
  cloudformation admin http://controller:8000/v1
```

5. Orchestration yêu cầu thêm thông tin trong Identity service để quản lý stacks. Để thêm thông tin này, hoàn thiện các bước sau:

- Tạo **heat** domain mà chứa project và user cho stacks:

```sh
openstack domain create --description "Stack projects and users" heat
```

- Tạo người dùng ```heat_domain_admin``` để quản lý project và user trong **heat** domain

```sh
openstack user create --domain heat --password-prompt heat_domain_admin
```

- Thêm **admin** role cho người dùng **heat_domain_admin** trong **heat** domain để có quyền quản lý administrative stack bằng **heat_domain_admin** user:

```sh
openstack role add --domain heat --user-domain heat --user heat_domain_admin admin
```

- Tạo role **heat_stack_owner**:

```sh
openstack role create heat_stack_owner
```

- Thêm role **heat_stack_owner** vào **demo** project và user để có thể quản lý stack bằng **demo** user

```sh
openstack role add --domain heat --user-domain heat --user heat_domain_admin admin
```

- Tạo role **heat_stack_owner**:

```sh
openstack role create heat_stack_owner
```

- Thêm role **heat_stack_owner** vào **demo** project và user để có thể quản lý stack bằng **demo** user

```sh
openstack role add --project demo --user demo heat_stack_owner
```

- Tạo **heat_stack_user** role:

```sh
openstack role create heat_stack_user
```

## Install and configure components

1. Tải và cài đặt các gói cần thiết:

```sh
yum install openstack-heat-api openstack-heat-api-cfn openstack-heat-engine -y
```

2. Chỉnh sửa ```/etc/heat/heat.conf```

- Trong phần ```[database]```, chỉnh sửa thông tin truy cập database:

```sh
[database]
...
connection = mysql+pymysql://heat:Welcome123@controller/heat
```

Trong phần ```[DEFAULT]```, cấu hình RabbitMQ message queue access:

```sh
[DEFAULT]
...
transport_url = rabbit://openstack:RABBIT_PASS@controller
```

- Trong ```[keystone_authtoken]```, ```[trustee]```, và ```[clients_keystone]```, cấu hình Identity service access:

```sh
[keystone_authtoken]
...
www_authenticate_uri = http://controller:5000
auth_url = http://controller:5000
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = heat
password = Welcome123

[trustee]
...
auth_type = password
auth_url = http://controller:5000
username = heat
password = Welcome123
user_domain_name = default

[clients_keystone]
...
auth_uri = http://controller:5000
```

- Trong phần ```[DEFAULT]```, cấu hình metadata và waitcondition URLs:

```sh
[DEFAULT]
...
heat_metadata_server_url = http://controller:8000
heat_waitcondition_server_url = http://controller:8000/v1/waitcondition
```

- Trong ```[DEFAULT]``` section, cấu hình stack domain và administrative credentials:

```sh
[DEFAULT]
...
stack_domain_admin = heat_domain_admin
stack_domain_admin_password = HEAT_DOMAIN_ADMIN_PASS
stack_user_domain_name = heat
```

**Lưu ý:** Thay thế ```HEAT_DOMAIN_ADMIN_PASS``` với password đã thiết lập trước đó

3. Sync DB

```sh
su -s /bin/sh -c "heat-manage db_sync" heat
```

4. Cuối cùng, khởi động Orchestration services và thiết lập chúng để khởi động cùng hệ thống:

```sh
systemctl enable --now openstack-heat-api.service \
  openstack-heat-api-cfn.service openstack-heat-engine.service
```

## Verify operation

1. Source admin tenant credentials

```sh
. admin-openrc
```

2. Liệt kê các thành phần dịch vụ để verify chúng đã và đang hoạt động

```sh
openstack orchestration service list
```