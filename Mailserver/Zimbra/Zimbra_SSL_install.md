# Cài đặt chứng chỉ SSL có trả phí cho Zimbra mailserver

### Đăng ký chứng chỉ

- Truy cập trang https://www.ssls.com/

- Chọn 1 chứng chỉ bất kỳ, ```try for free```

![](./images/zimbra_ssls.png)

- Checkout (bản dùng thử sẽ có tác dụng trong 30 ngày)

![](./images/zimbra_checkout.png)

- Nhập email

![](./images/zimbra_enter_email.png)

- Nhập thông tin cá nhân

![](./images/zimbra_checkout_info.png)

- Chọn ```ACTIVATE```

![](./images/zimbra_activate_ssl.png)

- Nhập vào tên miền của mailserver (lưu ý là cả www và không www)

![](./images/zimbra_mailserver_domain.png)

- Chọn ```Use my CSR``` và copy dòng lệnh để tạo CSR bằng command line

![](./images/zimbra_create_csr.png)

- Chạy đoạn lệnh vừa rồi ở server

![](./images/zimbra_create_csr_command.png)

- Copy và paste CSR vào trình duyệt rồi nhấn ```ONWARDS```

![](./images/zimbra_paste_csr.png)

- Chọn ```Create a DNS record``` và nhấn ```SUBMIT```

![](./images/zimbra_create_a_dns_record.png)

- Tạo bản ghi theo hướng dẫn

![](./images/zimbra_dns_record.png)

![](./images/zimbra_cname_record.png)

- Chờ đợi và tải file .zip về

![](./images/zimbra_certificate.png)

- Tạo file commercial.crt và copy nội dung chứng chỉ vào

```sh
cd /opt/zimbra/ssl/zimbra/commercial/
vi commercial.crt
```

![](./images/zimbra_commercial_crt.png)

- Tạo file commercial_ca.crt và copy nội dung chứng chỉ vào

```sh
vi commercial_ca.crt
```

![](./images/zimbra_commercial_ca_crt.png)

- Tạo file commercial.key lấy nội dung từ file mail_tubui_xyz.pem

```sh
cp mail_tubui_xyz.pem commercial.key
```

![](./images/zimbra_commercial_key.png)

- Verify chứng chỉ

```sh
chown zimbra:zimbra * -R
su zimbra
/opt/zimbra/bin/zmcertmgr verifycrt comm
```

![](./images/zimbra_verify.png)

- Deploy chứng chỉ

```sh
/opt/zimbra/bin/zmcertmgr deploycrt comm commercial.crt ./commercial_ca.crt
```

- Khởi động lại Zimbra

```sh
zmcontrol restart
```

- Kiểm tra chứng chỉ

![](./images/zimbra_done_ssl.png)