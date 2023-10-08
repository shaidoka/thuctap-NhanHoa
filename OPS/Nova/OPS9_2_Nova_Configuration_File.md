# File cấu hình của Nova

File cấu hình của Nova được đặt tại ```/etc/nova/nova.conf```

## I. File cấu hình trên node Controller

### ```[DEFAULT]``` section

Là IP management của node Controller

```sh
my_ip = 10.10.34.161
```

Hỗ trợ neutron service

```sh
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
```

### ```[api]``` section

Xác thực qua Keystone

```sh
auth_strategy = keystone
```

### ```api_database``` section

Kết nối database của nova-api

```sh
connection = mysql+pymysql://nova:Welcome123@10.10.34.161/nova_api
```

### ```[cache]``` section

Cấu hình cache sử dụng memcached

```sh
backend = oslo_cache.memcache_pool
enabled = true
memcache_servers = 10.10.34.161:11211
```

### ```[database]``` section

Cấu hình database của nova-service

```sh
conection = mysql+pymysql://nova:Welcome123@10.10.34.161/nova
```

### ```[glance]``` section

Đường dẫn dịch vụ của glance

```sh
api_servers = http://10.10.34.161:9292
```

### ```[keystone_authtoken]``` section

URL xác thực với keystone

```sh
auth_url = http://10.10.34.161:5000/v3
```

Đường dẫn memcache server

```sh
memcached_servers = 10.10.34.161:11211
```

Kiểu xác thực

```sh
auth_type = password
```

Thông tin domain

```sh
project_domain_name = default
user_domain_name = default
```

Project name của Nova

```sh
project_name = service
```

Thông tin xác thực

```sh
username = nova
password = Welcome123
```

Region

```sh
region_name = RegionOne
```

### ```[neutron]``` section

Các cấu hình liên quan tới neutron-service

```sh
url = http://10.10.34.161:9696
auth_url = http://10.10.34.161:35357
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

### ```[placement]``` section

Các thông tin xác thực, project với placement

```sh
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://10.10.34.161:5000/v3
username = placement
password = Welcome123
```

### ```[vnc]``` section

Địa chỉ management IP của VNC proxy

```sh
novncproxy_host = 10.10.34.161
enabled = true
vncserrver_listen = 10.10.34.161
vncserver_proxyclient_address = 10.10.34.161
novncproxy_base_url = http://10.10.34.161:6080/vnc_auto.html
```

## II. File cấu hình của Nova-compute

Các cấu hình khác so với Nova trên Controller

### ```[libvirt]``` section

Loại ảo hóa sử dụng: có thể là ```kvm```, ```lxc```, ```qemu```, ```uml```, ```xen```, ```parallels```

```sh
virt_type = kvm
```