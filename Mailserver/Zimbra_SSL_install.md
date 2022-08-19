# Cài đặt chứng chỉ SSL có trả phí cho Zimbra mailserver

1. Đầu tiên, vào trang ssls.com để đăng ký 1 chứng chỉ

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

- 