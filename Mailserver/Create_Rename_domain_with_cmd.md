# Tạo domain và đổi tên domain bằng cmd

1. Tạo domain

Sử dụng lệnh 

```sh
zmprov createDomain newtubui.xyz
```

![](./images/zimbra_create_domain.png)

2. Đổi tên domain

```sh
zmprov -l renameDomain renametubui.xyz
```

![](./images/zimbra_rename_domain.png)

3. Xóa domain

```sh
zmprov dd renametubui.xyz
```

**Lưu ý:** cần phải xóa hết các tài khoản thuộc domain trước khi xóa domain đó