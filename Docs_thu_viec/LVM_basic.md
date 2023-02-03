# Cấu hình và sử dụng LVM

### 1. Chuẩn bị

- Cắm ổ -> Import Foreign Volume -> Cấu hình RAID

### 2. Tạo và định dạng phân vùng

- Đầu tiên kiểm tra xem ổ đã online chưa 

```sh
lsblk
```

- Tạo phân vùng cho ổ đĩa mới gắn

```sh
fdisk /dev/sdb/
```

- Sau đó, lệnh này sẽ hỏi về các tùy chọn, 1 số tùy chọn khả dụng bao gồm:
 - n - Tạo phân vùng
 - p - In bảng phân vùng
 - d - Xóa phân vùng
 - q - Thoát mà không save
 - w - Lưu lại thay đổi và thoát

- Thông thường, sau khi gõ lệnh ```fdisk``` ta sẽ gõ lần lượt các option theo thứ tự sau:

```sh
n
p
1
w
```

- Định dạng lại phân vùng vừa tạo:

```sh
mkfs.ext4 /dev/sdb1
```

### 3. Cấu hình LVM

- Tạo Physical volume:

```sh
pvcreate /dev/sdb1
```

- Tạo Volume Group

```sh
vgcreate vg_kvm /dev/sdb1
```

- Tạo Logical Volume

```sh
lvcreate -L 200G -n lv_kvmdisk vg_kvm
```

- Định dạng lại Logical Volume vừa tạo

```sh
mkfs.ext4 /dev/vg_kvm/lv_kvmdisk
```

- Mount volume vừa tạo

```sh
mkdir /kvmdata
mount /dev/vg_kvm/lv_kvmdisk /kvmdata
```

- Thêm vào fstab để reboot thì auto mount:

```sh
# Check blkid để xem UUID của ổ vừa tạo là gì sau đó thêm vào fstab
echo "UUID=<UUID_here>  /kvmdata    ext4    defaults    0   0" >> /etc/fstab
```

### Add pool để sử dụng cho KVM

- Lần lượt thực hiện như sau:

![](../KVM/images/LVM_1.png)

![](../KVM/images/LVM_2.png)

![](../KVM/images/LVM_3.png)

![](../KVM/images/LVM_4.png)

- OK vậy là có thể chọn pool và tạo VM vào disk mới được rồi

### Extend disk máy ảo

- Tắt máy, add thêm ổ

![](../KVM/images/LVM_5.png)

![](./images/LVM_1.png)

- Boot VM

```sh
virsh start vmvlan660
```

- Check xem VM nhận ổ mới chưa:

```sh
lsblk
```

![](./images/LVM_2.png)

- Tạo phân vùng cho ổ mới

```sh
fdisk /dev/sdb
```

![](./images/LVM_3.png)

- Sử dụng option ```n``` để tạo phân vùng mới

![](./images/LVM_4.png)

- Tiếp theo option ```p``` để tạo loại phân vùng cơ bản -> Chọn 1 số theo như màn hình ghi, ở đây chọn 1 -> Về phần sector thì chọn default để tạo phân vùng từ sector đầu đến cuối của ổ

![](./images/LVM_5.png)

- Cuối cùng gõ ```w``` để lưu và thoát

![](./images/LVM_6.png)

- Lúc này lsblk lên ta sẽ thấy như này

![](./images/LVM_7.png)

- Định dạng lại ổ thành ```ext4``` để ta có thể dùng LVM với nó

```sh
mkfs.ext4 /dev/sdb1
```

![](./images/LVM_8.png)

- Tạo physical volume

```sh
pvcreate /dev/sdb1
```

![](./images/LVM_9.png)

- Add thêm physical volume vào volume group có sẵn (đầu tiên phải kiểm tra volume group đang có trước)

```sh
pvs
vgs
vgextend centos /dev/sdb1
```

![](./images/LVM_10.png)

![](./images/LVM_11.png)

- Mở rộng logical volume

```sh
lvextend -L +80G /dev/centos/root
```

![](./images/LVM_12.png)

- Cuối cùng, reszie lại ổ, trước hết phải kiểm tra filesystem, sử dụng lệnh

```sh
file -sL /dev/sda1
```

![](./images/LVM_13.png)

- Vì là xfs nên sử dụng lệnh sau để resize:

```sh
xfs_growfs /dev/centos/root
```

![](./images/LVM_14.png)

- Nếu là ext4 thì ta sử dụng lệnh

```sh
resize2fs /dev/centos/root
```

- Kiểm tra lại dung lượng ổ

```sh
df -h
```

![](./images/LVM_15.png)