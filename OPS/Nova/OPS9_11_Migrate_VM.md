# Migrate VM trong OPS

## Tổng quan

Migration là quá trinh di chuyển máy ảo từ host vật lí này sang host vật lí khác. Migration được sinh ra để giải quyết vấn đề bảo trì hay nâng cấp hệ thống. Ngày nay tính năng này đã được phát triển để thực hiện nhiều tác vụ hơn:
- **Cân bằng tải:** Di chuyển VMs tới các host khác khi phát hiện host đang chạy có dấu hiệu quá tải
- **Bảo trì, nâng cấp hệ thống:** Di chuyển các VMs ra khỏi host trước khi tắt nó đi
- **Khôi phục lại máy ảo khi host gặp lỗi:** Restart máy ảo trên 1 host khác

Trong Openstack, việc migrate được thực hiện giữa các node compute với nhau hoặc giữa các project trên cùng 1 node compute.

Openstack cung cấp 1 số phương pháp khác nhau để migrate VM. Các phương pháp này có các hạn chế như:

- Không thể live-migrate với shared storage
- Không thể live-migrate nếu đã bật enabled
- Không thể select target host nếu sử dụng nova migrate

Openstack hỗ trợ 2 kiểu migration là:

- Cold migration
- Live migration:
   - True live migration (shared storage or volume-based)
   - Block live migration

## So sánh 2 kiểu migrate

### Cold migrate

**Ưu điểm:**

- Đơn giản, dễ thực hiện
- Thực hiện được với mọi loại máy ảo

**Hạn chế:**

- Thời gian downtime lớn
- Không thể chọn host muốn migrate đến
- Quá trình migrate có thể mất một khoảng thời gian dài

### Live migrate

**Ưu điểm:**

- Có thể chọn host muốn migrate đến
- Tiết kiệm chi phí, tăng sự linh hoạt trong khâu quản lý và vận hành
- Giảm thời gian downtime và gia tăng khả năng rescue khi gặp sự cố

**Nhược điểm:**

- Quá trình migrate có thể fail nếu host được chọn không có đủ tài nguyên
- Không can thiệp được vào bất kỳ tiến trình nào trong quá trình live migrate
- Khó migrate với nhưng máy ảo có dung lượng bộ nhớ lớn và trường hợp 2 host khác CPU

## Workflow

### Cold migrate

1. Tắt máy ảo (giống với virsh destroy) và ngắt kết nối với volume
2. Di chuyển thư mục hiện tại của máy ảo (instance_dir -> instance_dir_resize)
3. Nếu sử dụng qcow2 với backing files (chế độ mặc định) thì image sẽ được convert thành dạng flat

### Live migrate

1. Kiểm tra lại xem storage backend có phù hợp với loại migrate sử dụng không

- Thực hiện check shared storage với chế độ migrate thông thường
- Không check khi sử dụng block migration
- Việc kiểm tra thực hiện trên cả 2 node gửi và nhận, chúng được điều phối bởi RPC call từ scheduler

2. Đối với nơi nhận

- Tạo các kết nối cần thiết với volume
- Nếu dùng block migration, tạo thêm thư mục chứa máy ảo, truyền vào đó những backing files còn thiếu từ Glance và tạo disk trống

3. Tạo nơi gửi, bắt đầu quá trình migration (qua url)

4. Khi hoàn thành, generate lại file XML và define lại nó ở nơi chứa máy ảo mới

## Thực hành migrate

### Cold migrate

Thực hiện migrate 1 VM từ ```com1``` sang ```com2```

**Tại COM1**

Sử dụng khóa gốc có trong thư mục ```/root/.ssh/id_rsa``` và ```/root/.ssh/id_rsa.pub``` hoặc tạo cặp khóa mới. Ở đây, ta sẽ tạo khóa mới

Tạo usermode

```sh
usermod -s /bin/bash nova
```

Tạo key-pair cho user nova

```sh
su nova
ssh-keygen
echo 'StrictHostKeyChecking no' >> /var/lib/nova/.ssh/config
cat /var/lib/nova/.ssh/id_rsa.pub > /var/lib/nova/.ssh/authorized_keys
chmod 600 /var/lib/nova/.ssh/id_rsa /var/lib/nova/.ssh/authorized_keys
exit
```

Thực hiện với quyền root, scp key pair tới node ```com2```. Nhập mật khẩu khi được yêu cầu

```sh
scp -r /var/lib/nova/.ssh root@com2:/var/lib/nova/
```

**Tại node COM2**

Thay đổi quyền của key pair cho user nova và add key pair đó vào SSH

```sh
chown -R nova:nova /var/lib/nova/.ssh
```

Kiểm tra lại từ node ```com1``` để chắc chắn user ```nova``` login được vào node ```com2``` mà không cần sử dụng password

```sh
su nova
ssh com2
```

Kiểm tra tương tự trên node ```com2```

```sh
su nova
ssh com1
```

**Lưu ý:** Nếu gặp phải lỗi

```sh
This account is currently not available.
Connection to com2 closed
```

Kiểm tra shell của user ```nova``` trên node ```com2```, ta sẽ thấy ```nologin```

```sh
cat /etc/passwd | grep "nova"
nova:x:162:162:OpenStack Nova Daemons:/var/lib/nova:/sbin/nologin
```

Lúc này ta set usermod trên node ```com2```

```sh
usermod -s /bin/bash nova
```

**Lưu ý:** Đối với trường hợp sử dụng nhiều node compute, có thể dùng chung 1 cặp key, copy cặp key đó tới tất cả các node để các node có thể xác thực lẫn nhau

**Thực hiện trên cả 2 node**

Restart service 

```sh
systemctl restart libvirtd
systemctl restart openstack-nova-compute
```

**Thực hiện cold-migrate trên node controller bất kỳ**

Tắt máy ảo nếu nó đang chạy

```sh
openstack server stop <vm-name-or-id>
```

Migrate máy ảo

```sh
openstack server migrate <vm-name-or-id>
```

Lúc này VM sẽ ở trạng thái ```VERIFY_RESIZE```, xác thực resize bằng lệnh:

```sh
openstack server resize confirm <vm-name-or-id>
```

Kiểm tra lại kết quả:

```sh
openstack server show <vm-name-or-id>
```

### Live Migrate

#### Các loại live migrate

- **True live migration** (shared storage hoặc volume-based): Trong trường hợp này, máy ảo sẽ được di chuyển sử dụng storage mà cả 2 máy computes đều có thể truy cập tới. Nó yêu cầu máy ảo sử dụng block storage hoặc shared storage
- **Block live migration**: Mất 1 khoảng thời gian lâu hơn để hoàn tất quá trình migrate bởi máy ảo được chuyển từ host này sang host khác. Tuy nhiên nó lại không yêu cầu máy ảo sử dụng hệ thống lưu trữ tập trung

Các yêu cầu chung:

- Cả 2 node nguồn và đích đều phải được cài đặt trên cùng subnet và có cùng loại CPU
- Cả controller và compute đều phải phân giải được tên miền của nhau
- Compute node buộc phải sử dụng KVM với libvirt

**Lưu ý:** live-migration làm việc với 1 số loại VM và storage

- Shared storage: cả 2 hypervisor có quyền truy cập shared storage chung
- Block storage: VM sử dụng root disk, không tương thích với các loại readonly device
- Volume storage: VM sử dụng iSCSI volumes

#### Cấu hình live migrate

**Tại tất cả node compute:**

Chỉnh sửa cấu hình

```sh
sed -i 's/#listen_tls = 0/listen_tls = 0/g' /etc/libvirt/libvirtd.conf
sed -i 's/#listen_tcp = 1/listen_tcp = 1/g' /etc/libvirt/libvirtd.conf
sed -i 's/#auth_tcp = "sasl"/auth_tcp = "none"/g' /etc/libvirt/libvirtd.conf
sed -i 's/#LIBVIRTD_ARGS="--listen"/LIBVIRTD_ARGS="--listen"/g' /etc/sysconfig/libvirtd
```

Khởi động lại service

```sh
systemctl restart libvirtd
systemctl restart openstack-nova-compute
```

Nếu sử dụng block device, sửa file ```nova.conf```

```sh
[libvirt]
block_migration_flag=VIR_MIGRATE_UNDEFINE_SOURCE, VIR_MIGRATE_PEER2PEER, VIR_MIGRATE_LIVE, VIR_MIGRATE_NON_SHARED_INC
```

Khởi động lại dịch vụ

```sh
systemctl restart openstack-nova-compute
```

#### Tiến hành live migrate

**Thực hiện trên node controller bất kỳ**

- Đối với VM dùng ```shared storage```

```sh
openstack server migrate <vm-id> --live-migration --host com2
```

- Lệnh dùng với VM boot từ local:

```sh
openstack server migrate <vm-id> --live-migration --block-migration --host com2
```