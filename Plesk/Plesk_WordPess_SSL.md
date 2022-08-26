# Cài đặt WordPress và cài SSL Let's Encrypt trêm Plesk

## Cài đặt WordPress

- Tại Control Panel, chọn ```WordPress``` -> ```Install WordPress```

![](./images/pl_install_wordpress.png)

- Điền các thông tin cơ bản để tạo wordpress

![](./images/pl_wp_in4.png)

- Thông tin về WordPress được hiển thị

![](./images/pl_wp.png)

- Trang quản trị WordPress

![](./images/pl_wp_admin.png)

## Cài đặt SSL Let's Encrypt trên Plesk

- Trong Plesk Control Panel, vào ```Websites & Domains``` -> ```SSL/TLS Certificate```

![](./images/pl_ssl_tls.png)

- Chọn "Install a free basic certificate provided by Let's Encrypt"

![](./images/pl_install_ssl_free.png)

- Lựa chọn domain và subdomain muốn chứng nhận rồi nhấn ```Get it free```

![](./images/pl_ssl_free_options.png)

- Thêm bản ghi TXT vào máy chủ DNS theo hướng dẫn và nhấn ```Reload```

- Chứng nhận thành công:

![](./images/pl_ssl_free_success.png)

- Kiểm tra

![](./images/pl_ssl_free_check.png)

