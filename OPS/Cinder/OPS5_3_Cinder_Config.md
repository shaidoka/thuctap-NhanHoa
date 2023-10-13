# File cấu hình Cinder

Vị trí lưu file cấu hình Cinder: ```/etc/cinder/cinder.conf```

## I. Khai báo DB

```sh
[database]
connection = mysql+pymysql://cinder:Welcome123@10.10.31.166/cinder
```

Trong đó:
- ```connection = ...```: chỉ ra địa chỉ mà cần kết nối database. Khai báo password: ```Welcome123``` cho database ```cinder``` và địa chỉ: ```10.10.31.166``` (hostname hoặc IP) của node controller

## II. Khai báo message queue

```sh
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@10.10.31.166
```

Trong đó:
- ```transport_url```: đường dẫn, user, mật khẩu, IP controller

## III. Khai báo xác thực Keystone

```sh
[DEFAULT]
auth_strategy = keystone

[keystone_authtoken]
www_authenticate_uri = http://10.10.31.166:5000
auth_url = http://10.10.31.166:5000
memcached_servers = 10.10.31.166:11211
auth_type = password
project_domain_name = default
project_name = service
username = cinder
password = Welcome123
```

Trong đó:
- ```auth_strategy```: Cấu hình strategy dùng cho xác thực, ở đây là Keystone
- ```www_authenticate_uri```: Cấu hình endpoint Identity service
- ```auth_url```: URL để xác thực Identity service
- ```memcached_servers```: cấu hình địa chỉ memcached server
- ```auth_type```: xác định hình thức xác thực sử dụng
- ```project_domain_name```: chỉ định project domain name openstack
- ```user_domain_name```: chỉ định user domain name openstack
- ```project_name```: chỉ định project name
- ```username```: Chỉ định username của cinder
- ```password```: Chỉ định password của cinder

## IV. IP management

```sh
[DEFAULT]
my_ip = 10.10.31.166
```

Trong đó:
- ```my_ip```: Địa chỉ IP management của Storage Node

## V. Cấu hình Storage backend

### 1. LVM Backend 

```sh
[DEFAULT]
enabled_backends = lvm

[lvm]
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_group = cinder-volumes
target_protocol = iscsi
target_helper = lioadm
```

- ```enabled_backends```: cấu hình backend sử dụng. Ở đây là LVM, đối với multiple backend thì cần dấu phẩy giữa các backend (VD: enable_backends = lvm,nfs,glusterfs)
- ```volume_driver```: chỉ định driver mà LVM sử dụng
- ```volume_group = cinder-volumes```: Chỉ định vgroup mà tạo lúc cài đặt. Sử dụng câu lệnh ```vgs``` hoặc ```vgdisplay``` để xem thông tin về vgroup đã tạo
- ```target_protocol```: xác định giao thức iSCSI cho iSCSI volumes mới, được tạo ra với tgtadm hoặc lioadm. Để kích hoạt RDMA, tham số nên được cài đặt là "iser". Hỗ trợ cho giao thức iSCSI giá trị là "iscsi" và "iser"
- ```target_helper```: chỉ ra iSCSI sử dụng. Mặc định là ```tgtadm```. Có các tùy chọn sau:
   - ```lioadm```: hỗ trợ LIO iSCSI
   - ```scstadm```: hỗ trợ SCST
   - ```iseradm```: cho ISER
   - ```ietadm```: cho iSCSI

### 2. GlusterFS backend

```sh
[DEFAULT]
enabled_backends = glusterfs
[glusterfs]
volume_driver = cinder.volume.drivers.glusterfs.GlusterfsDriver
glusterfs_shares_config = /etc/cinder/glusterfs_shares
glusterfs_mount_point_base = $state_path/mnt_gluster
```

Trong đó:
- ```enabled_backends```: cấu hình backend sử dụng, ở đây là Glusterfs
- ```volume_driver```: chỉ định driver mà Glusterfs sử dụng
- ```glusterfs_shares_config```: file cấu hình để kết nối tới Glusterfs
- ```gluster_mount_point_base```: mount point tới Glusterfs
   - Nội dung file ```glusterfs_shares``` sẽ phải bao gồm:
   
   ```sh
   <IP_address>:/cinder-vol
   ```
      - ```IP_addres```: IP của Glusterfs pool
      - ```cinder-vol```: tên volume đã tạo ở Glusterfs

## VI. Cấu hình khác

```sh
[DEFAULT]
my_ip = 10.10.31.166
glance_api_servers = http://10.10.31.166:9292

[oslo_concurrentcy]
lock_path = /var/lib/cinder/tmp
```

Trong đó:
- ```my_ip```: Ip Management của Storage node
- ```glance_api_servers```: URL kết nối tới Glance
- ```lock_path```: Khai báo thư mục chứa lock_path