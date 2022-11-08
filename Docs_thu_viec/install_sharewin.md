# Tạo VM trên solus (37.208) và cài đặt windows

## Tạo VM

1. SSH vào con node và dùng lệnh ```lsblk``` để xem list block device

![](./images/Screenshot_1.png)

=> sda là ổ cài OS, từ sdb -> sde là các ổ chứa VM, 2 ổ cuối sdf sdg là 2 ổ chứa backup. Do sdd còn trống nên cài VM mới vào đây

2. Lên con solus cho các dịch vụ share 103.28.37.208, tìm con node và edit LV Group

![](./images/Screenshot_2.png)

- Đang muốn cài lên sdd nên chỉnh LV Group thành vps2

![](./images/Screenshot_3.png)

3. Add VM

- Điền các thông tin cần thiết rồi tạo thôi

![](./images/Screenshot_4.png)

4. Thay đổi disk driver

- Shutdown máy

- Lấy ID của VM

![](./images/Screenshot_5.png)

- Tiếp tục SSH vào con node, và cd vào ```/home/kvm/kvm1332```

```sh
cd /home/kvm/kvm1332
```

- Vào chỉnh sửa file .xml của VM

```sh
vi kvm1332.xml
```

- Sửa bus thành ```virtio``` và thêm đoạn sau vào

```sh
    <disk type='file' device='cdrom'>
     <source file='/home/solusvm/kvm/iso/virtio-win-0.1.126.iso'/>
     <target dev='hdd'/>
     <readonly/>
    </disk>
```

- Lưu lại và thoát ra

- Create VM theo file .xml

```sh
virsh create /home/kvm/kvm1332/kvm1332.xml
```

- Ra Solus và VNC vào thôi

## Cài Win

- Tua nhanh vì cài nhiều lần rồi

![](./images/Screenshot_6.png)

![](./images/Screenshot_7.png)

- Chọn "Load driver"

![](./images/Screenshot_8.png)

- Browse đến file như sau rồi ấn next

![](./images/Screenshot_9.png)

![](./images/Screenshot_10.png)

![](./images/Screenshot_11.png)

![](./images/Screenshot_12.png)

- Đã vào Win

![](./images/Screenshot_13.png)