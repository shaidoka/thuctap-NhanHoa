# Tạo Email trên CWP

### Tạo Email bằng tài khoản quản trị Admin (root)

- Ở thanh **Navigation**, chọn ```Email``` -> ```Email Accounts```

- Chọn ```Add new domain mail```

![](./images/cwp_add_new_domain_mail.png)

- Chọn User, sau đó nhập thông tin cần thiết và nhấn ```Create Mail``` để tạo email

![](./images/cwp_email_account_in4.png)

### Tạo Email bằng tài khoản User

- Ở thanh **Navigation**, chọn ```Email Accounts``` -> ```Email Accounts```

- Chọn ```Add a New MailBox```, nhập thông tin để tạo email

![](./images/cwp_mail_user_in4.png)

- Nhấn ```Create``` để tạo

![](./images/cwp_mail_list.png)

### Truy cập Roundcube Webmail

- Tại giao diện Admin, ở thanh **Navigation**, chọn ```Email``` -> ```Roundcube Webmail```

![](./images/cwp_mail_roundcube.png)

- Tại giao diện User, ở thanh **Navigation**, chọn ```Email Accounts``` -> ```Roundcube Webmail```

![](./images/cwp_mail_user_roundcube.png)

- Đăng nhập bằng tài khoản Email vừa tạo

![](./images/cwp_mail_roundcube_login.png)

- Giao diện Roundcube Webmail

![](./images/cwp_mail_roundcube_main_menu.png)

### Kiểm tra gửi/nhận mail

- Gửi ok

![](./images/cwp_mail_send_ok.png)

- Nhận ok

![](./images/cwp_mail_recv_ok.png)

### Tạo bản ghi DKIM 

- Tại giao diện quản trị Admin, trên thanh **Navigation**, chọn ```Email``` -> ```MailServer Manager```

- Tích chọn ```Install DKIM & SPF```, nhập lại hostname của VPS, tên miền và nhấn ```Rebuild Mail Server```

![](./images/cwp_mail_rebuild_mail_server.png)

- Sau đó, trên thanh **Navigation**, chọn ```Email``` -> ```DKIM Manager```

- Chọn tên miền cần active DKIM, tích ```enable SPF``` (nếu chưa tích), nhấn vào ```Add DKIM``` và ```Edit Records``` để lấy bản ghi DKIM sau khi đã kích hoạt

![](./images/cwp_mail_dkim_active.png)

- Tạo bản ghi với thông tin bản ghi có được

![](./images/cwp_mail_dkim_record.png)

- Bản ghi DKIM trên nameserver

![](./images/cwp_mail_dkim_zonedns.png)

- Kiểm tra bản ghi DKIM

![](./images/cwp_mail_test_dkim.png)