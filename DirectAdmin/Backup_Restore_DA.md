# Thực hiện Backup và Restore database trên DirectAdmin

#### 1. Tạo 1 vài bài viết trên WordPress

![](./images/create_new_post.png)

#### 2. Tạo file backup

- Đăng nhập vào trang quản trị DA -> Tại User Level, chọn ```Create/Restore Backups```

- Chọn những thông tin muốn backup và nhấn ```Create Backup```

![](./images/create_backup.png)

- Sau đó, chờ vài phút để hệ thống tiến hành tạo file backup, sau khi hoàn thành sẽ có tin nhắn gửi về phần ```Message System```

![](./images/you_backup_ready.png)

- Kiểm tra file backup ở ```FileManager >> /backups```

![](./images/backups.png)

#### 3. Xóa 1 vài bài viết trước khi thực hiện Restore

![](./images/delete_post.png)

#### 4. Restore database

- Tại menu ```Create/Restore Backups```, chọn file backup muốn thực hiện Restore và nhấn ```Select Restore Options```

![](./images/select_n_restore.png)

- Chọn những thông tin muốn Restore và nhấn ```Restore Selected Items```

![](./images/select_items_to_restore.png)

- Khi quá trình Restore hoàn tất sẽ có tín nhắn gửi về ```System Message```

![](./images/restore_complete.png)

- Các bài viết đã quay trở lại

![](./images/and_it_back.png)