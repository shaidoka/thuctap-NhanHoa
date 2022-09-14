# Chặn email trong Zimbra mailserver

### 1. Chặn thư từ 1 địa chỉ IP/tên miền cố dịnh bất kỳ gửi đến Zimbra mailserver

- Tạo danh sách IP block

```sh
cd /opt/zimbra/conf/
vi postfix_reject_sender
```

- Thêm vào IP/domain cần block

```sh
shaizabrim@tubui.xyz REJECT
mail.tubui.xyz REJECT
```

- Truy cập vào user Zimbra và thực hiện lệnh:

```sh
su zimbra
zmprov ms mail.tubui.xyz +zimbraMtaSmtpdSenderRestrictions "check_sender_access lmdb:/opt/zimbra/conf/postfix_reject_sender"
```

- Postmap với file đã tạo và khởi động lại zmmtactl

```sh
/opt/zimbra/common/sbin/postmap /opt/zimbra/conf/postfix_reject_sender
zmmtactl restart
```

- Kiểm tra gửi thư từ ```shaizabrim@tubui.xyz``` đến ```shaizimbra@tubui.xyz```

![](./images/zimbra_blocked_mail.png)

### 2. Chặn thư từ tài khoản gmail đến Zimbra mailserver

- Chỉnh sửa tệp ```postfix_reject_sender```

```sh
vi postfix_reject_sender
#Thêm dòng sau vào
shaidokun@gmail.com REJECT
```

- Khởi động lại ```zmmtactl```

```sh
zmmtactl restart
```

### 3. Chặn thư từ gmail đến Zimbra mailserver

- Tiếp tục chỉnh sửa tệp ```opt/zimbra/conf/postfix/reject/sender```

```sh
vi postfix_reject_sender
#Thêm dòng sau vào
gmail.com REJECT
```

- Khởi động lại ```zmmtactl```

```sh
zmmtactl restart
```

