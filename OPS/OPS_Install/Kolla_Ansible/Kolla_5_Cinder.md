# Cinder - Block Storage

## Overview

Cinder có thể được triển khai sử dụng Kolla và hỗ trợ các loại storage sau đây:

- ceph
- hnas_nfs
- iscsi
- lvm
- nfs

## LVM

Khi sử dụng ```lvm``` backend, 1 volume group nên được tạo trên mỗi storage node. Điều này có thể là 1 ổ cứng vật lý hoặc 1 loopback mounted file để test. Sử dụng ```pvcreate``` và ```vgcreate``` để tạo volume group. Ví dụ với devices ```/dev/sdb``` và ```/dev/sdc```:

```sh
pvcreate /dev/sdb /dev/sdc
vgcreate cinder-volumes /dev/sdb /dev/sdc
```

Enable ```lvm``` backend trong ```globals.yml```:

```sh
enable_cinder_backend_lvm: "yes"
```

## NFS

To use ```nfs``` backend, configure ```/etc/exports``` to contain the mount where the volumes are to be stored:

```sh
/kolla_nfs 192.168.5.0/24(rw,sync,no_root_squash)
```

Trong ví dụ này, ```/kolla_nfs``` là đường dẫn trên storage node, nơi mà ```nfs``` được mount, ```192.168.5.0/24``` là storage network, và ```rw,sync,no_root_squash``` có nghĩa là share file/folder sẽ có quyền read-write, đồng bộ, và ngăn remote root user có thể truy cập vào tất cả files.

Sau đó start ```nfsd```:

```sh
systemctl start nfs
```

Trên deploy node, tạo ```/etc/kolla/config/nfs_shares``` với ` entry cho mỗi storage node:

```sh
storage01:/kolla_nfs
storage02:/kolla_nfs
```

Cuối cùng, enable ```nfs``` backend trong ```globals.yml```:

```sh
enable_cinder_backend_nfs: "yes"
```

## Validation

Tạo 1 volume như dưới đây

```sh
openstack volume create --size 1 steak_volume
openstack volume list
```

## Cinder LVM2 backend với iSCSI

Từ bản Newton thì Kolla đã hỗ trợ LVM2 làm cinder backend. Điều này thực hiện bởi 2 container mới là ```tgtd``` và ```iscsid```. Trong đó ```tgtd``` container hoạt động như 1 bridge giữa cinder-volume process và 1 server hosting Logical Volume Groups (LVG). Còn ```iscsid``` container phục vụ như 1 bridge giữa nova-compute process và server hosting LVG.

Để sử dụng LVM backend của Cinder, 1 LVG tên là ```cinder-volumes``` cần tồn tại trên server và tham số sau phải được chỉ định trong ```globals.yml```:

```sh
enable_cinder_backend_lvm: "yes"
```

### For Ubuntu and LVM2/iSCSI

```iscsid``` process sử dụng configfs, thứ mà được mount vào ```/sys/kernel/config``` để lưu trữ thông tin của các target đã phát hiện, trên centos/rhel systems, filesystem đặc biệt này được mount tự động. Vì ```iscsid``` container chạy trên mọi nova compute node, các bước sau phải được thực hiện trên mọi Ubuntu server mà có vai trò nova compute

- Thêm configfs module vào ```/etc/modules```
- Rebuild initramfs sử dụng lệnh ```update-initramfs -u```
- Stop ```open-iscsi``` system service vì nó có thể conflict với ```iscsid``` container
- Đảm bảo configfs được mount trong quá trình boot. Có nhiều cách để thực hiện điều này, ví dụ:

```sh
mount -t configfs /etc/rc.local /sys/kernel/config
```

## Cinder backend với external iSCSI storage

Để sử dụng external storage system, hãy chỉ định tham số sau:

```sh
enable_cinder_backend_iscsi: "yes"
```

Ngoài ra, ```enable_cinder_backend_lvm``` cần được đặt thành ```no``` trong trường hợp này.

## Skip Cinder prechecks for Custom backends

Để sử dụng custom storage backends, thứ mà hiện tại chưa được hỗ trợ chính thức bởi Kolla, hãy chỉ định tham số sau:

```sh
skip_cinder_backend_check: True
```

Tất cả cấu hình cho NFS backend nên được thực hiện bởi ```cinder.conf``` trong config overrides directory

## Cinder-Backup with S3 Backend

Cấu hình Cinder-Backup cho S3 với các bước sau:

1. Enable Cinder-Backup S3 backend trong ```globals.yml```

```sh
cinder_backup_driver: "s3"
```

2. Cấu hình S3 connection trong ```globals.yml```

- ```cinder_backup_s3_url``` (VD: http://127.0.0.1:9000)
- ```cinder_backup_s3_access_key``` (VD: minio)
- ```cinder_backup_s3_bucket``` (VD: cinder)
- ```cinder_backup_s3_secret_key``` (VD: admin)

Nếu ta muốn sử dụng 1 S3 backend cho tất cả các dịch vụ được hỗ trợ, sử dụng các biến sau:

- ```s3_url```
- ```s3_access_key```
- ```s3_glance_bucket```
- ```s3_secret_key```