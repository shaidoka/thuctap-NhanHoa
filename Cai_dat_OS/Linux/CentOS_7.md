# Cài đặt CentOS 7 lên server vật lý

- Cài lại RAID

- Boot vào USB chứa file cài CentOS 7

- Chọn ```Install CentOS 7```

- Lựa chọn ngôn ngữ

![](./images/cent7_step_1.png)

- Thiết lập ngày giờ

![](./images/cent7_step_2.png)

- Phân vùng ổ cứng

![](./images/cent7_step_3.png)

- Hostname + network

![](./images/cent7_step_4.png)

- ```Begin Installation```

![](./images/cent7_step_5.png)

- Đặt mật khẩu cho tài khoản root

![](./images/cent7_step_6.png)

- Wait

![](./images/cent7_step_7.png)

- OK

![](./images/cent7_step_8.png)

### Đổi mật khẩu root mà không cần ssh vào sv

- Reboot

- Tại giao diện này, nhấn ```e``` trên bàn phím

![](./images/cent7_step_9.png)

- Tìm dòng có chữ ```/ro``` như sau

![](./images/cent7_step_10.png)

- Thay chữ ```/ro``` thành ```/rw init=/sysroot/bin/bash```

![](./images/cent7_step_11.png)

- Sau đó ta nhấn tổ hợp phím ```Ctrl X``` để vào chế độ **1 người dùng**

![](./images/cent7_step_12.png)

- Truy cập bằng lệnh chroot

```sh
chroot /sysroot
```

- Đổi mật khẩu tài khoản root

```sh
passwd root
```

- Update thông tin selinux

```sh
touch /.autorelabel
```

- Thoát hệ thống và khởi động lại

```sh
exit
reboot
```

![](./images/cent7_step_13.png)

- Đăng nhập vào bằng mật khẩu mới

![](./images/cent7_step_14.png)