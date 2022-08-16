# Tạo email trên DA

1. Login vào user muốn tạo email

![](./images/menu_user.png)

2. Tạo tài khoản email

Tại menu user, chọn ```E-mail Accounts``` -> ```Create mail account```

![](./images/mail_account_setting.png)

Nhập thông tin và chọn ```Create``` để tạo mail account

3. Kiểm tra gửi nhận mail

Tại giao diện menu, chọn ```Webmail: RoundCube``` hoặc truy cập đường dẫn ```tubui.xyz/roundcube```

Đăng nhập với tài khoản email vừa tạo

![](./images/webmail_roundcube.png)

Gửi thư kiểm tra

![](./images/test_mail.png)

Nhận thư thành công

![](./images/mail_recv.png)

**Lưu ý:** Để gửi được mail phải thêm những bản ghi sau

- Host ```mail```, type ```A```, value ```103.170.123.26```
- Host ```@```, type ```MX```, value ```mail.tubui.xyz```
- Host ```_dmarc```, type ```TXT```, value ```"v=DMARC1; p=none; rua=mailto:mailauth-reports@mail.tubui.xyz"```
- Host ```@```, type ```TXT```, value ```"v=spf1 +a +mx +ip4:103.170.123.26 ~all"```

