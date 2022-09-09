# Cài đặt CentOS 6.9 trên máy chủ vật lý

-  Chuẩn bị USB boot CentOS 6.9
    - Tải file iso của CentOS 6.9
    - Dùng ```rufus``` tạo USB boot

- Cài đặt CentOS 6.9

- Khởi động lại máy chủ sau đó nhấn F11 để vào Boot Manager

- Tại ```Boot Manager``` chọn ```BIOS Boot Menu```

- Thực hiện Boot vào USB để cài đặt CentOS 6.9

![](./images/cent6_step_1.png)

- Chọn ngôn ngữ mặc định là English rồi nhấn ```OK```

![](./images/cent6_step_2.png)

- Chọn phương pháp cài đặt là ```Hard Drive``` -> ```OK```

![](./images/cent6_step_4.png)

- Chọn ```Next```

![](./images/cent6_step_5.png)

- ```Basic Storage Devices``` -> ```Next```

![](./images/cent6_step_6.png)

- Đặt hostname -> ```Next```

![](./images/cent6_step_7.png)

- Thiết lập lại timezone -> ```Next```

![](./images/cent6_step_8.png)

- Đặt mật khẩu cho tài khoản root -> ```Next```

![](./images/cent6_step_9.png)

- Chọn ```Create Custom Layout``` -> ```Next```

![](./images/cent6_step_10.png)

- Tạo các phân vùng

![](./images/cent6_step_11.png)

- Nhấn ```Next``` -> ```Write change to disk```

- Chọn ```Install boot loader on /dev/sdb1``` -> ```Next```

![](./images/cent6_step_12.png)

- Chờ hệ thống tiến hành cài đặt

![](./images/cent6_step_13.png)

- Reboot để khởi động lại hệ thống là xong

![](./images/cent6_step_14.png)

