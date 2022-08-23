# Thay đổi title webapp của Zimbra

Sau khi cài đặt, webapp của Zimbra sẽ có phần title được set mặc định, điều này hoàn toàn có thể thay đổi để phù hợp hơn với những đơn vị, tổ chức riêng

![](./images/zimbra_web_title.png)

### 1. Thay đổi title mailbox login webapp

- Chỉnh sửa file ```ZmMsg.properties```

```sh
cd /opt/zimbra/jetty/webapps/zimbra/WEB-INF/classes/messages
vi ZmMsg.properties
```

- Tìm và sửa trường ```zimbraLoginTitle```

![](./images/zimbra_login_title.png)

- Khởi động lại ```mailboxd```

```sh
su zimbra
zmmailboxdctl restart
```

- Title của webapp sau khi đổi:

![](./images/zimbra_web_title_after.png)

### 2. Thay đổi title của mailbox webapp

![](./images/zimbra_mailbox_title_before.png)

- Tiếp tục tìm đến file ```ZmMsg.properties``` và chỉnh sửa trường ```zimbraTitle```

![](./images/zimbra_title.png)

- Khởi động lại ```mailboxd```

```sh
su zimbra
zmmailboxdctl restart
```

- Title của mailbox sau khi sửa:

![](./images/zimbra_mailbox_title_after.png)

### 3. Thay đổi title của trang quản trị Zimbra

![](./images/zimbra_admin_title_before.png)

- Chỉnh sửa file ```ZabMsg.properties```

```sh
cd /opt/zimbra/jetty_base/webapps/zimbraAdmin/WEB-INF/classes/messages
vi ZabMsg.properties
```

- Tìm trường ```zimbraAdminTitle``` và chỉnh sửa

![](./images/zimbra_admin_title.png)

- Title của trang quản trị sau khi sửa:

![](./images/zimbra_admin_title_after.png)

