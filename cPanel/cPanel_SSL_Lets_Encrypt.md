# Cài đặt chứng chỉ SSL Let's Encrypt

- Truy cập trang quản lý của user qua cổng 2083 và đăng nhập với tài khoản tương ứng với tên miền cần cài SSL

![](./images/cp_21.png)

- Trước tiên, ta gỡ SSL self-sign có sẵn trên tên miền: tại tab **Security**, chọn ```SSL/TLS```

![](./images/cp_22.png)

- Chọn ```Manage SSL sites```

![](./images/cp_23.png)

- Chọn ```Uninstall``` để xóa đi các chứng chỉ cũ

![](./images/cp_24.png)

- Quay trở lại trang chính, vẫn tại tab **Security**, chọn ```SSL/TLS Status```

![](./images/cp_25.png)

- Tick chọn những domain muốn cài SSL rồi nhấn ```Run AutoSSL```

![](./images/cp_26.png)

- OK

![](./images/cp_27.png)

- Kiểm tra chứng chỉ

![](./images/cp_28.png)

