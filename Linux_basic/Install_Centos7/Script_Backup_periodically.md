# Tạo script sao lưu dữ liệu trên Linux

Trong quá trình vận hành máy chủ hay website. Backup dữ liệu luôn là vấn đề hàng đầu được ưu tiên. Việc backup dữ liệu website thường xuyên khiến bạn luôn có phương pháp dự phòng cho trường hợp xấu nhất có thể xảy ra

## Các bước thực hiện

#### Bước 1: SSH vào máy chủ Linux

Việc đầu tiên phải làm chắc chắn là SSH vào server với quyền root

#### Bước 2: Tạo script backup dữ liệu (source + database)

- Tạo file chứa script

```sh
vi /bin/auto-backup
```

- Thêm đoạn script sau vào file đã tạo

```sh
#!/bin/bash

echo "Backup website tubui.xyz"
####### Tạo đường dẫn chứa File Backup
mkdir /home/backup/$(date +"%Y-%m-%d")/
mkdir /home/backup/$(date +"%Y-%m-%d")/baotrung.xyz/

####### Backup Database
echo "Starting backup database for baotrung.xyz..."
mysqldump --single-transaction --routines --triggers --add-drop-table --extended-insert -u admindb -p'123456a@' db_baotrung | gzip -9 > /home/backup/$(date +"%Y-%m-%d")/baotrung.xyz/Database_$(date +"%Y-%m-%d").sql.gz

####### Backup Source
echo "Starting backup files for baotrung.xyz..."
zip -r /home/backup/$(date +"%Y-%m-%d")/baotrung.xyz/Source_$(date +"%Y-%m-%d").zip /home/baotrung/public_html/ -q

echo "Backup Database & Source thanh cong vao luc $(date +"%Y-%m-%d")!"
echo "File backup da duoc luu tai: /home/backup/tubui.xyz"
```

- Trong đó:
    - Tên website cần backup: baotrung.xyz
    - Đường dẫn lưu file backup: /home/backup/baotrung.xyz
    - User database: admindb
    - Password: 123456a@
    - Tên database: db_baotrung
    - Đường dẫn lưu file backup Source + Database: /home/backup
    - Tên file backup source: Source.zip
    - Tên file backup database: database.sql.zip

- Sau đó ta tiến hành phân quyền cho file auto-backup

```sh
chmod +x /bin/auto-backup
```

- Tạo đường dẫn chứa file backup

```sh
mkdir /home/backup
```

Sau khi phân quyền xong, bạn hãy thử gõ tên file script để kiểm tra xem script có hoạt động hay không

#### Bước 3: Tạo cron để thiết lập thời gian chạy script

- Thiết lập cron với cấu trúc như sau

```sh
crontab -e
0 0 * * * auto-backup >> /home/backup/log-backup.txt
```

- Khởi động lại cron

```sh
systemctl restart crond
systemctl enable crond
```

- Kiểm tra xem cron đã được tạo thành công chưa

```sh
cat /var/spool/cron/root
#hoặc
crontab -l
```

#### Bước 4: Tạo cron xóa backup định kỳ

- Do script này sẽ lưu trữ file trực tiếp trên VPS nên về lâu dài sẽ chiếm dung lượng của VPS. Vì thế chúng ta cần thiết lập cron để xóa các file backup cũ định kỳ, ví dụ ở đây mỗi 1h sáng hàng ngày sẽ xóa các file backup cũ vào chỉ giữ lại 3 bản backup gần nhất

```sh
crontab -e
0 1 * * * find /home/backup -type d -mtime +3 -exec rm -rf {} +
systemctl restart crond
```