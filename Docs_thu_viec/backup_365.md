# BACKUP 365 

## CentOS

1. Cài đặt Agent trên server

- Thực hiện các bước sau:

```sh
yum -y update
cd /etc/yum.repos.d
vi r1soft.repo

# Paste đoạn sau vào
[r1soft]
name=R1Soft Repository Server
#baseurl=http://repo.r1soft.com/yum/stable/$basearch/
baseurl=http://repo.r1soft.com/release/6.6.2/57/yum/stable/x86_64/
enabled=1
gpgcheck=0
```

- Tiếp tục thực hiện các lệnh sau:

```sh
yum install serverbackup-enterprise-agent
# Mở port 8282 và 1167 trên firewall theo chiều out
r1soft-setup --get-key http://45.117.82.8:8282
```

![](./images/r1_1.png)

2. Backup

- Đăng nhập vào trang quản trị backup 365 và tạo Machine mới điền các thông tin cần thiết:

![](./images/r1_2.png)

- Thêm disk cần backup:

![](./images/r1_3.png)

![](./images/r1_4.png)

- Thiết lập policy:

![](./images/r1_5.png)

![](./images/r1_6.png)

- Thiết lập bỏ qua directory nào:

![](./images/r1_7.png)

- Add MySQL Instance

![](./images/r1_8.png)

![](./images/r1_9.png)

![](./images/r1_10.png)

![](./images/r1_11.png)

- Next -> Next -> ...

![](./images/r1_12.png)

- Sau khi cấu hình xong policy thì ấn save để hoàn thành cấu hình backup cho máy chủ linux

- Tiến hành Backup

![](./images/r1_13.png)

3. Restore

- Open Revovery Points

![](./images/r1_14.png)

![](./images/r1_15.png)

- Restore theo từng tệp hoặc restore hết cả directory

![](./images/r1_16.png)

![](./images/r1_17.png)

- OK

![](./images/r1_18.png)

- Restore database

![](./images/r1_19.png)

![](./images/r1_20.png)

- Để default hết

![](./images/r1_21.png)