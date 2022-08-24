# Cài đặt SSL Let's Encrypt cho mailserver Kerio

- ```Configuration``` -> ```SSL Certificates``` -> ```New``` -> ```New Let's Encrypt Certificate```

![](./images/kerio_new_ssl_lets_encrypt.png)

- Điền hostname

![](./images/kerio_ssl_host_name.png)

- ```New``` -> ```New Certificate Request```

![](./images/kerio_new_cert_request.png)

- Điền thông tin

![](./images/kerio_new_cert_request_in4.png)

- Chuột phải vào SSL Let's encrypt đã tạo trước đó, chọn ```Export``` và export cả key và certificate về máy

![](./images/kerio_ssl_export_key.png)

- Tại Request đã tạo trước đó, chuột phải chọn ```Import``` -> ```Import a New Certificate```

![](./images/kerio_ssl_import_new_certificate.png)

- Select và dẫn tới key cùng certificate vừa tải về

![](./images/kerio_import_ssl_cert.png)

- Để máy chủ sử dụng chứng chỉ này, chuột phải vào certificate và chọn ```Set as Default```

![](./images/kerio_ssl_set_as_default.png)

- Kiểm tra

![](./images/kerio_ssl_check.png)

![](./images/kerio_ssl_check_2.png)