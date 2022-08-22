# Backup và Restore trong Zimbra mailserver

### 1. Backup

- Đăng nhập bằng user zimbra và dừng các chương trình đang chạy

```sh
su zimbra
zmcontrol stop
```

- Tạo bản sao lưu:
    - Đảm bảo rằng vị trí sao lưu có đủ dung lượng để chứa bản sao
    - Tất cả thành phần mà Zimbra cần đều nằm trong thư mục chính, nên việc backup trong Zimbra được thực hiện bằng cách copy toàn bộ thư mục này sang 1 vị trí khác

```sh
cp -rp /opt/zimbra /mnt/zimbra_backup.$(date "+%Y%m%d")
```

### 2. Restore

- Tương tự khi Backup, ta dừng tất cả tiến trình của zimbra

```sh
su zimbra
zmcontrol stop
```

- Sao chép bản sao lưu trước đó vào thư muc ```/opt``` và đặt tên là ```zimbra```

```sh
cp -rp /mnt/zimbra_backup/ /opt
mv /opt/zimbra_backup /opt/zimbra
```

- Cài đặt lại Zimbra

```sh
cd zcs-9.0.0_GA_1.RHEL7_64.20200411070311.tgz
./install.sh
```

- Khi có thông báo ```Do you wish to upgrade? [Y]``` thì nhập Y để đồng ý. Trình cài đặt sẽ xóa bỏ các gói hiện tại và cài đặt lại chúng, nó sẽ dừng dịch vụ Zimbra cũ và chạy với những file đã sao lưu

- Đặt lại quyền

```sh
chown -R zimbra:zimbra /opt/zimbra/store
chown -R zimbra:zimbra /opt/zimbra/index
/opt/zimbra/libexec/zmfixperms
```
