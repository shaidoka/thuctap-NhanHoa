# Cấu hình Cinder backups với backends là NFS

## Cấu hình NFS làm backend cho Cinder

**Trên host chạy Cinder service**

Dùng trình soạn thảo vi mở file ```/etc/cinder/nfs_shares```:

```sh
vi /etc/cinder/nfs_shares
```

Thêm ```/var/lib/nfs-share``` là thư mục chứa volume NFS và các volume backups

```sh
172.16.6.10:/var/lib/nfs-share
```

Phân quyền với file ```/etc/cinder/nfs_shares```

```sh
chown root:cinder /etc/cinder/nfs_shares
chmod 0640 /etc/cinder/nfs_shares
```

Cấu hình Cinder service sử dụng ```/etc/cinder/nfs_shares``` file được tạo ở phía trên

```sh
vi /etc/cinder/cinder.conf
```

Thêm đoạn cấu hình:

```sh
[backend_defaults]
nfs_shares_config = /etc/cinder/nfs_shares
volume_driver = cinder.volume.drivers.nfs.NfsDriver
```

Khởi động lại các dịch vụ để hoàn tất quá trình cài đặt

```sh
systemctl enable openstack-cinder-volume target
systemctl restart openstack-cinder-volume target
```

## Cấu hình Block Storage NFS

**Trên node NFS-server**

```sh
yum install nfs-utils -y
mkdir /var/lib/nfs-share
echo "/var/lib/nfs-share 172.16.10.0/24(rw,no_root_squash)" > /etc/exports 
systemctl restart rpcbind nfs-server
systemctl enable rpcbind nfs-server
```

## Trên storage node

Cài các gói:

```sh
yum install --enablerepo=centos-openstack-train,epel -y openstack-cinder targetcli python-keystone python-openstackclient
```

Thực hiện sửa cấu hình trong file ```/etc/cinder/cinder.conf``` trên node storage

```sh
vi /etc/cinder/cinder.conf 
```

Sửa các phần sau

```sh
[DEFAULT]
enabled_backends = lvm,nfs
...
[nfs]
volume_driver = cinder.volume.drivers.nfs.NfsDriver
nfs_shares_config = /etc/cinder/nfs_shares
volume_backend_name = nfsdriver-1
nfs_mount_point_base = $state_path/mnt_nfs
```

Cài đặt và cấu hình NFs client trên Storage node

```sh
yum -y install nfs-utils
systemctl enable rpcbind --now
```

```sh
chown  -R cinder. /var/lib/cinder/mnt_nfs/
```

Khởi động lại dịch vụ để hoàn tất cài đặt

```sh
systemctl enable openstack-cinder-volume target nfs
systemctl restart openstack-cinder-volume target rpcbind nfs
```

## Tạo type NFS trên Controller node

**Thực hiện trên Controller node**

Tạo type volume

```sh
openstack volume type create nfs
openstack volume type set nfs --property volume_backend_name=nfsdriver-1
```

Kiểm tra lại

```sh
openstack volume type list --long
```

Khởi tạo NFS disk

```sh
openstack volume create --type nfs --size 5 disk_nfs
```

Restart service backup

```sh
systemctl enable openstack-cinder-backup
systemctl restart openstack-cinder-backup
```

Kiểm tra:

```sh
openstack volume service list
```

## Backup & Restore volume

Để có thể tạo backup từ một volume thì volume đó phải ở trạng thái ```available```. Nếu volume đang ở ```in-use``` thì cần gỡ nó ra hoặc chuyển đổi status của nó bằng tài khoản admin, sau khi backup xong thì attach lại.

### Backup volume

```sh
openstack volume backup create --name <backup-name> [--incremental] [--force] <volume-name>
``` 

Trong đó:
- ```<volume-name>```: tên hoặc id của volume
- ```incremental```: tùy chọn backup theo kiểu incremental hay full backup
- ```force```: là cờ chỉ ra sự cho phép hoặc không cho phép thực hiện backup volume trong khi nó đang ```in-use```. Nếu không có cờ ```force``` thì volume chỉ có thể backup khi đang ```available```. Khi trạng thái của volume là ```in-use``` mà backup mà cờ ```force``` thì dữ liệu của volume đó sẽ bị ngắt ngoãng. Mặc định cờ ```force``` được tắt

### Restore volume

```sh
openstack volume backup restore <backup-id> <volume-id>
```

Sau khi restore thì cần reboot lại VM
- Khi restore từ full backup thì gọi là full restore
- Khi restore thì incremental backup, danh sách backup được liệt kê dựa trên IDs của parent backups. Một full restore được thực hiện dựa trên full backup đầu tiên và các lần incremental backup sau đó được đặt theo đúng thứ tự

