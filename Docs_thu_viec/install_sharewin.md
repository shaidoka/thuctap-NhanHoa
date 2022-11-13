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

## Update Driver + Tạo rule firewall

- Chọn "Tool"

![](./images/Screenshot_14.png)

- Chọn "Computer Management"

![](./images/Screenshot_15.png)

- "Device Manager" -> "Ethernet Controller" -> "Update Driver"

![](./images/Screenshot_16.png)

- Browse

![](./images/Screenshot_17.png)

- Browse đến file như trong hình "E:\NetKVM\2k16\amd64"

![](./images/Screenshot_18.png)

- "Install"

![](./images/Screenshot_19.png)

- Mạng đã về bản

![](./images/Screenshot_20.png)

- Enable Remote Desktop: "This PC" -> "Properties"

![](./images/Screenshot_21.png)

- "Remote Setting"

![](./images/Screenshot_22.png)

- "Allow" -> Apply và OK

![](./images/Screenshot_23.png)

- Check status firewall

![](./images/Screenshot_24.png)

- "Advanced settings"

![](./images/Screenshot_25.png)

- Tạo rule

![](./images/Screenshot_26.png)

- Sau đó reboot lại server và Remote Desktop vào thôi

## Install IIS

- ```Add Roles and Feature``` -> Chọn IIS, .NET và ASP như yêu cầu

![](./images/Screenshot_27.png)

![](./images/Screenshot_28.png)

- Install thôi

![](./images/Screenshot_29.png)

- Ok

![](./images/Screenshot_30.png)

- Để cài PHP, ta mở ```IIS Manager``` -> Chọn ```Get New Web Platform Components```

![](./images/Screenshot_31.png)

![](./images/Screenshot_32.png)

![](./images/Screenshot_33.png)

- Mở Web Platform Installer

![](./images/Screenshot_34.png)

- Cài đặt các bản PHP cần thiết

![](./images/Screenshot_35.png)

![](./images/Screenshot_36.png)

## Cài đặt SQL Server

- Lên trang chủ của Oracle download JDK về www.oracle.com

- Cài đặt trang wordpress

![](./images/Screenshot_37.png)



## Plesk

- Plesk: https://get.plesk.com/