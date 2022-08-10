# Backup và Restore database

1. Tạo thư mục lưu trữ file backup

```sh
mkdir /mnt/backup
cd /mnt/backup
```

2. Sao lưu database vào file backup.sql, lưu tại /mnt/backup

```mysqldump -u root -p forwordpress > backup.sql```

3. Restore database

Bài viết "Born to be deleted" bị xóa trước khi restore

![](./images/delete_post_wp.png)

Sau khi restore bằng lệnh

```mysql -u root -p -D forwordpress < backup.sql```

![](./images/after_restore_wp.png)

