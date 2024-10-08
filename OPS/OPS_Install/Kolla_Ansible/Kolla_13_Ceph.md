# External Ceph

Kolla Ansible không cung cấp hỗ trợ cho việc xây dựng và cấu hình 1 ceph cluster. Thay vào đó, người quản trị nên sử dụng 1 số tool khác cho việc này như ```ceph-ansible``` hoặc ```cephadm```

Các pool mong muốn và keyrings sau đó sẽ được tjao thông qua Ceph CLI hoặc tương tự.

### Requirements

- 1 Ceph cluster
- Storage pools trên ceph
- Credentials để OpenStack kết nối đến Ceph

## Configuring External Ceph

### Glance

Ceph RBD có thể được sử dụng như 1 storage backend cho Glance images. Cấu hình Glance cho Ceph bao gồm các bước sau:

Bật cấu hình Glance Ceph backend trong ```globals.yml```

```sh
glance_backend_ceph: "yes"
```

Cấu hình Ceph authentication chi tiết trong ```globals.yml```

- ```ceph_glance_keyring``` (default: ```client.glance.keyring```)
- ```ceph_glance_user``` (default: ```glance```)
- ```ceph_glance_pool_name``` (default: ```images```)

Copy tệp cấu hình của Ceph vào ```/etc/kolla/config/glance/ceph.conf```

```sh
[global]
fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
keyring = /etc/ceph/ceph.client.glance.keyring
mon_initial_members = ceph-0
mon_host = 192.168.0.56
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

Copy Ceph keyring vào ```/etc/kolla/config/glance/ceph.<ceph_glance_keyring>```

Để cấu hình multiple Ceph backends với Glance, thứ mà hữu dụng cho multistore:

Copy tệp cấu hình của Ceph vào ```/etc/kolla/config/glance/``` sử dụng các tên khác nhau, ví dụ:

```/etc/kolla/config/glance/ceph.conf```

```sh
[global]
fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
keyring = /etc/ceph/ceph.client.glance.keyring
mon_initial_members = ceph-0
mon_host = 192.168.0.56
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

```/etc/kolla/config/glance/rbd1.conf```

```sh
[global]
fsid = dbfea068-89ca-4d04-bba0-1b8a56c3abc8
keyring = /etc/ceph/rbd1.client.glance.keyring
mon_initial_members = ceph-0
mon_host = 192.10.0.100
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

Khai báo Ceph backends trong ```globals.yml```

```sh
glance_ceph_backends:
  - name: "rbd"
    type: "rbd"
    cluster: "ceph"
    enabled: "{{ glance_backend_ceph | bool }}"
  - name: "another-rbd"
    type: "rbd"
    cluster: "rbd1"
    enabled: "{{ glance_backend_ceph | bool }}"
```

Copy Ceph keyring vào ```/etc/kolla/config/glance/ceph.<ceph_glance_keyring>```, và tương tự với ```/etc/kolla/config/glance/rbd1.<ceph_glance_keyring>```

Với copy-on-write, thiết lập tham số sau trong ```/etc/kolla/config/glance.conf```:

```sh
[DEFAULT]
show_image_direct_url = True
```

### Cinder

Ceph RBD có thể được sử dụng như 1 storage backend cho Cinder volumes. Cấu hình Cinder cho Ceph như sau:

Khi sử dụng external Ceph, ta sẽ không cần có 1 node nào đưa vào nhóm ```storage``` trong file inventory. Tuy vậy, điều này sẽ khiến Cinder và các dịch vụ liên quan phụ thuộc vào nhóm này bị lỗi. Trong trường hợp này, người quản trị nên đặt 1 (hoặc 1 vài) node vào nhóm ```storage```, tất cả các nodes nơi ```cinder-volume``` và ```cinder-backup``` sẽ chạy:

```sh
[storage]
control01
```

Bật Cinder Ceph backend trong ```globals.yml```:

```sh
cinder_backend_ceph: "yes"
```

Cấu hình Ceph authentication trong ```globals.yml```:

- ```ceph_cinder_keyring``` (default: ```client.cinder.keyring```)
- ```ceph_cinder_user``` (default: ```cinder```)
- ```ceph_cinder_pool_name``` (default: ```volumes```)
- ```ceph_cinder-backup.keyring``` (default: ```client.cinder-backup.keyring```)
- ```ceph_cinder_backup_user``` (default: ```cinder-backup```)
- ```ceph_cinder_backup_pool_name``` (default: ```backups```)

Copy tệp cấu hình Ceph vào ```/etc/kolla/config/cinder/ceph.conf```

*(optional)* Tách các tùy chọn cấu hình có thể được thiết lập cho cinder-volume và cinder-backup bằng cách thêm ceph.conf vào ```/etc/kolla/config/cinder/cinder-volume``` và ```/etc/kolla/config/cinder/cinder-backup``` tương ứng. Chúng sẽ được gộp lại với ```/etc/kolla/config/cinder/ceph.conf```

Copy các tệp Ceph keyrings vào:

- /etc/kolla/config/cinder/cinder-volume/ceph.<ceph_cinder_keyring>
- /etc/kolla/config/cinder/cinder-backup/ceph.<ceph_cinder_keyring>
- /etc/kolla/config/cinder/cinder-backup/ceph.<ceph_cinder_backup_keyring>

*Lưu ý: ```cinder-backup``` yêu cầu 2 keyrings để truy cập volumes và backup pool*

Để cấu hình ```multiple Ceph backends``` với Cinder, thứ mà sẽ hữu dụng cho việc sử dụng với nhiều availability zones:

Copy các tệp cấu hình Ceph vào ```/etc/kolla/config/cinder/``` sử dụng các tên khác nhau 

```/etc/kolla/config/cinder/ceph.conf```

```sh
[global]
fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
mon_initial_members = ceph-0
mon_host = 192.168.0.56
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

```/etc/kolla/config/cinder/rbd2.conf```

```sh
[global]
fsid = dbfea068-89ca-4d04-bba0-1b8a56c3abc8
mon_initial_members = ceph-0
mon_host = 192.10.0.100
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

Định nghĩa các Ceph backends trong ```globals.yml```

```sh
cinder_ceph_backends:
  - name: "rbd-1"
    cluster: "ceph"
    enabled: "{{ cinder_backend_ceph | bool }}"
  - name: "rbd-2"
    cluster: "rbd2"
    availability_zone: "az2"
    enabled: "{{ cinder_backend_ceph | bool }}"
```

Copy Ceph keyring files cho tất cả các Ceph backends:

- ```/etc/kolla/config/cinder/cinder-volume/ceph.<ceph_cinder_keyring>```
- ```/etc/kolla/config/cinder/cinder-backup/ceph.<ceph_cinder_keyring>```
- ```/etc/kolla/config/cinder/cinder-backup/ceph. <ceph_cinder_backup_keyring>```
- ```/etc/kolla/config/cinder/cinder-volume/rbd2.<ceph_cinder_keyring>```
- ```/etc/kolla/config/cinder/cinder-backup/rbd2.<ceph_cinder_keyring>```
- ```/etc/kolla/config/cinder/cinder-backup/rbd2. <ceph_cinder_backup_keyring>```

Nova cũng phải được cấu hình để cho phép truy nhập đến Cinder volumes:

- Cấu hình Ceph authentication trong ```/etc/kolla/globals.yml```: ```ceph_cinder_keyring``` (mặc định: ```client.cinder.keyring```)
- Copy Ceph keyring file vào ```/etc/kolla/config/nova/ceph.<ceph_cinder_keyring>```

Để cấu hình Ceph backend khác cho nova-compute host, thứ mà sẽ hữu dụng cho nhiều availability zones:

- Copy Ceph keyring file vào ```/etc/kolla/config/nova/<hostname>/ceph.<ceph_cinder_keyring>```

Nếu ```zun``` được bật, và bạn muốn sử dụng cinder volumes với zun, bạn cũng phải cho phép nó truy cập vào Cinder volumes:

- Bật cinder ceph backend cho Zun trong ```globals.yml```:

```sh
zun_configure_for_cinder_ceph: "yes"
```

- Copy Ceph configuration file vào ```/etc/kolla/config/zun/zun-compute/ceph.conf```

- Copy các tệp Ceph keyring vào ```/etc/kolla/config/zun/zun-compute/ceph.<ceph_cinder_keyring>```

### Nova

Ceph RBD có thể được sử dụng như 1 storage backend cho Nova instance ephemeral disks. Điều này tránh yêu cầu về local storage cho instances trên compute nodes. Nó cải thiện hiệu năng của migration, vì ephemeral disks của instances không cần phải copy giữa các hypervisors.

Cấu hình Nova cho Ceph theo các bước sau:

- Enable Nova Ceph backend trong ```globals.yml```:

```sh
nova_backend_ceph: "yes"
```

- Cấu hình Ceph authentication trong ```/etc/kolla/globals.yml```:

   - ```ceph_nova_keyring``` (mặc định sẽ tương đồng với ```ceph_cinder_keyring```)
   - ```ceph_nova_user``` (mặc định là giống với ```ceph_cinder_user```)
   - ```ceph_nova_pool_name``` (mặc định là ```vms```)

- Copy Ceph configuration file vào ```/etc/kolla/config/nova/ceph.conf```

- Copy Ceph keyring files vào ```/etc/kolla/config/nova/ceph.<ceph_nova_keyring>```

### Manila

CephFS có thể được sử dụng như 1 storage backend cho Manila shares. Cấu hình Manila cho Ceph bao gồm các bước sau:

- Bật Manila Ceph backend trong ```globals.yml```:

```sh
enable_manila_backend_cephfs_native: "yes"
```

- Cấu hình Ceph authentication trong ```globals.yml```:

   - ```ceph_manila_keyring``` (mặc định là ```client.manila.keyring```)
   - ```ceph_manila_user``` (mặc định là ```manila```)

- Copy Ceph configuration file vào ```/etc/kolla/config/manila/ceph.conf```

- Copy Ceph keyring vào ```/etc/kolla/config/manila/ceph.<ceph_manila_keyring>```

Để cấu hình nhiều Ceph backends cho Manila, thứ mà sẽ hữu dụng cho nhiều availability zones:

- Copy các tệp cấu hình của Ceph vào ```/etc/kolla/config/manila``` sử dụng các tên khác nhau:

```/etc/kolla/config/manila/ceph.conf```

```sh
[global]
fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
mon_initial_members = ceph-0
mon_host = 192.168.0.56
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

```/etc/kolla/config/manila/rbd2.conf```

```sh
[global]
fsid = dbfea068-89ca-4d04-bba0-1b8a56c3abc8
mon_initial_members = ceph-0
mon_host = 192.10.0.100
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
```

Định nghĩa Ceph backends trong ```globals.yml```

```sh
manila_ceph_backends:
  - name: "cephfsnative1"
    share_name: "CEPHFS1"
    driver: "cephfsnative"
    cluster: "ceph"
    enabled: "{{ enable_manila_backend_cephfs_native | bool }}"
    protocols:
      - "CEPHFS"
  - name: "cephfsnative2"
    share_name: "CEPHFS2"
    driver: "cephfsnative"
    cluster: "rbd2"
    enabled: "{{ enable_manila_backend_cephfs_native | bool }}"
    protocols:
      - "CEPHFS"
  - name: "cephfsnfs1"
    share_name: "CEPHFSNFS1"
    driver: "cephfsnfs"
    cluster: "ceph1"
    enabled: "{{ enable_manila_backend_cephfs_nfs | bool }}"
    protocols:
      - "NFS"
      - "CIFS"
  - name: "cephfsnfs2"
    share_name: "CEPHFSNFS2"
    driver: "cephfsnfs"
    cluster: "rbd2"
    enabled: "{{ enable_manila_backend_cephfs_nfs | bool }}"
    protocols:
      - "NFS"
      - "CIFS"
```

- Copy Ceph keyring files cho tất cả các Ceph backends:

   - ```/etc/kolla/config/manila/manila-share/ceph.<ceph_manila_keyring>```
   - ```/etc/kolla/config/manila/manila-share/rbd2.<ceph_manila_keyring>```

- Nếu sử dụng nhiều filesystem (Ceph Pacific+), đặt ```manila_cephfs_filesystem_name``` trong ```/etc/kolla/globals.yml``` thành tên của Ceph filesystem mà Manila sẽ sử dụng. Mặc định, Manila sẽ sử dụng filesystem đầu tiên được trả về bởi ```cephfs volume ls``` command

- Setup Manila như thông thường

Để biết thêm thông tin về phần còn lại cho việc setup Manila, như việc tạo share type ```default_share_type```, hãy xem [Manila in Kolla](https://docs.openstack.org/kolla-ansible/latest/reference/storage/manila-guide.html)

### RadosGW

Từ bản phát hành Xena 13.0.0, Kolla ansible hỗ trợ tích hợp với Ceph RadosGW. Điều này bao gồm:

- Registration of Swift-compatible endpoints in Keystone
- Load balancing across RadosGW API servers using HAProxy

Bật tùy chọn tích hợp Ceph RadosGW:

```sh
enable_ceph_rgw: true
```

#### Keystone integration

1 Keystone user và endpoints được registered theo mặc định, tuy vậy, điều này có thể được bỏ qua bằng cách đặt ```enable_ceph_rgw_keystone``` thành ```false```. Nếu setting trên được bật, username được khai báo thông qua ```ceph_rgw_keystone_user```, và mặc định là ```ceph_rgw```. Hostnames mà sử dụng bởi public và internal endpoints mặc định lần lượt là ```ceph_rgw_external_fqdn``` và ```ceph_rgw_internal_fqdn```. Port mà được sử dụng cho endpoints được định nghĩa qua ```ceph_rgw_port```, mặc định là 6780.

Theo mặc định RadosGW hỗ trợ cả Swift và S3 API, và nó không hoàn toàn tương thích với Swift API. Tùy chọn ```ceph_rgw_swift_compability``` có thể enable/disable hoàn toàn RadosGW compability với Swift API. Điều này có thể sẽ phù hợp với cấu hình được sử dụng bởi Ceph RadosGW. Sau khi thay đổi giá trị, chạy lệnh ```kolla-ansible deploy``` để áp dụng.

Mặc định, RadosGW endpoint URL không bao gồm project (account) ID. Điều này ngăn cross-project và public object access. Ta có thể giải quyết bằng cách đặt ```ceph_rgw_swift_account_in_url``` thành ```true```. Và nó cũng sẽ khớp với tùy chọn cấu hình ```rgw_swift_account_in_url``` trong Ceph RadosGW.

#### Load balancing

Load balancing được bật theo mặc định, tuy vậy, ta có thể tắt nó bằng cách đặt ```enable_ceph_rgw_loadbalancer``` thành ```false```. Nếu sử dụng load balancing, RadosGW hosts và ports cần phải được cấu hình. Mỗi item nên chứa ```host``` và ```port``` keys. ```ip``` và ```port``` keys là tùy chọn, nếu ```ip``` không được chỉ định, giá trị ```host``` nên có thể được phân giải từ HAProxy. Nếu ```port``` không được chỉ định, port HTTP (80) hoặc HTTPS (443) sẽ được sử dụng. Ví dụ:

```sh
ceph_rgw_hosts:
  - host: rgw-host-1
  - host: rgw-host-2
    ip: 10.0.0.42
    port: 8080
```

HAProxy frontend port được định nghĩa thông qua ```ceph_rgw_port```, và mặc định là 6780.

#### Cephadm và Ceph Client version

Khi cấu hình Zun với Cinder volumes, kolla-ansible cài đặt 1 vài Ceph client packages trên zun-compute hosts. Bạn có thể đặt phiên bản của Ceph packages bằng cách cấu hình Ceph version trong ```/etc/kolla/globals.yml```, tham số ```ceph_version``` (mặc định ```pacific```).

