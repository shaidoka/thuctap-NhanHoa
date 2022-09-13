# Cài đặt Ubuntu 16 lên máy chủ vật lý

- Boot vào USB chứa file cài Ubuntu

- Chọn ```Install Ubuntu Server```

![](./images/U_16_step_1.png)

- Chọn ngôn ngữ

![](./images/U_16_step_2.png)

- Chọn khu vực

![](./images/U_16_step_3.png)

- Loại ngôn ngữ bàn phím

![](./images/U_16_step_4.png)

- ```No```

![](./images/U_16_step_5.png)

- Loại keyboard

![](./images/U_16_step_6.png)

- Keyboard layout

![](./images/U_16_step_7.png)

- Chọn giao diện mạng

![](./images/U_16_step_8.png)

- Đổi tên hostname

![](./images/U_16_step_9.png)

- Tạo 1 user mới (nhập tên của user), user này có thể thực hiện các thao tác không cần quyền quản trị

![](./images/U_16_step_10.png)

- Username cho user trên

![](./images/U_16_step_11.png)

- Password cho user trên

![](./images/U_16_step_12.png)

- Nhập lại password

![](./images/U_16_step_13.png)

- Mã hóa thư mục home, chọn ```No```

![](./images/U_16_step_14.png)

- Phân vùng ổ cứng, chọn ```Guided - use entire disk```

![](./images/U_16_step_15.png)

- Chọn ổ đĩa muốn phân vùng

![](./images/U_16_step_16.png)

- Nếu ô đĩa đã có sẵn phân vùng từ hđh trước, ta có thể chọn ```Yes``` để xóa nó đi

![](./images/U_16_step_17.png)

- ```Yes```

![](./images/U_16_step_18.png)

- Thiết lập tasksel, ta chọn ```No automatic updates```

![](./images/U_16_step_19.png)

- Cài đặt hoàn tất, ```Continue``` để reboot

![](./images/U_16_step_20.png)

- Login vào sv

![](./images/U_16_step_21.png)

### Reset lại mật khẩu root trong Ubuntu

- Reboot

- Giữ phím ```Shift```, hệ thống sẽ đưa đến ```GRUB``` hoặc menu khởi động với các phiên bản nhân Linux khác nhau được hiển thị

- Chọn ```Advanced Options for Ubuntu```

![](./images/U_16_step_22.png)

- Chọn ```recovery mode```

![](./images/U_16_step_23.png)

- Chọn ```root```

![](./images/U_16_step_24.png)

- Nhấn ```Enter```

![](./images/U_16_step_25.png)

- Nhập lệnh

```sh
mount -o remount,rw /
```

- Đặt lại mật khẩu và khởi động lại

```sh
passwd root
reboot
```

![](./images/U_16_step_26.png)

- Thử login với mật khẩu vừa đặt

![](./images/U_16_step_27.png)
