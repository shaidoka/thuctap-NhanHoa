# Thay đổi mật khẩu của account admin trong Zimbra

1. SSH vào mailserver với user zimbra

```sh
su zimbra
```

2. Kiểm tra những user có quyền admin

```sh
zmprov gaaa
```

![](./images/zimbra_zmprov_gaaa.png)

3. Thay đổi mật khẩu

```sh
zmprov sp admin@tubui.xyz 123456a@
```

