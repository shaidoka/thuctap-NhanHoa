# Cài đặt Icinga

Update packages

```sh
apt-get update -y && apt-get upgrade -y
```

Cài đặt dependency

```sh
apt install software-properties-common ca-certificates lsb-release apt-transport-https wget gnupg -y
```

```sh
wget http://ftp.hk.debian.org/debian/pool/main/b/boost1.71/libboost1.71-dev_1.71.0-6~bpo10+1_amd64.deb
dpkg -i libboost1.71-dev_1.71.0-6~bpo10+1_amd64.deb
```

Thêm Ondrej PPA vào hệ thống

```sh
LC_ALL=C.UTF-8 sudo add-apt-repository ppa:ondrej/php
```

Cập nhật Apt package

```sh
apt update -y
```

Cài đặt php 8.1

```sh
apt install php8.1 -y
```

**Lưu ý:** Để thay đổi phiên bản php default, ta dùng lệnh ```update-alternatives --config php```

Cài đặt php modules, apache2, mariadb

```sh
apt install apache2 mariadb-server mariadb-client mariadb-common php8.1-gd php8.1-mbstring php8.1-mysqlnd php8.1-curl php8.1-xml php8.1-cli php8.1-soap php8.1-xmlrpc php8.1-zip  php8.1-common php8.1-opcache php8.1-gmp php8.1-imagick php8.1-pgsql php8.1-intl -y
```

Khởi động apache2, mariadb

```sh
systemctl enable {apache2,mariadb} --now
```

Setup mariadb

```sh
mysql_secure_installation
```

Chỉnh sửa 1 vài thông số trong file php.ini

```sh
vi /etc/php/8.1/apache2/php.ini

memory_limit = 256M 
post_max_size = 64M
upload_max_filesize = 100M	
max_execution_time = 300
default_charset = "UTF-8"
date.timezone = "Asia/Ho_Chi_Minh"
cgi.fix_pathinfo=0
```

Restart apache2

```sh
systemctl restart apache2
```

Cài đặt Icinga2:

Thêm GPG-key

```sh
wget -O - https://packages.icinga.com/icinga.key | gpg --dearmor -o /usr/share/keyrings/icinga-archive-keyring.gpg
```

Thêm Icinga repo

```sh
. /etc/os-release; if [ ! -z ${UBUNTU_CODENAME+x} ]; then DIST="${UBUNTU_CODENAME}"; else DIST="$(lsb_release -c| awk '{print $2}')"; fi; \
 echo "deb [signed-by=/usr/share/keyrings/icinga-archive-keyring.gpg] https://packages.icinga.com/ubuntu icinga-${DIST} main" > \
 /etc/apt/sources.list.d/${DIST}-icinga.list
 echo "deb-src [signed-by=/usr/share/keyrings/icinga-archive-keyring.gpg] https://packages.icinga.com/ubuntu icinga-${DIST} main" >> \
 /etc/apt/sources.list.d/${DIST}-icinga.list
```

```sh
apt update -y
```

Cài đặt Icinga2

```sh
apt install icinga2 -y
```

Cài đặt monitor plugin

```sh
apt install monitoring-plugins -y
```

Khởi động icinga2

```sh
systemctl enable icinga2 --now
```

Cài đặt Icinga2 IDO Module

Icinga2 Data Output xuất tất cả thông tin về cấu hình và trạng thái vào 1 database. IDO database sau đó sử dụng bởi Icinga Web để làm backend

```sh
apt install icinga2-ido-mysql -y
```

Chọn ```Yes``` để bật tính năng ```ido-mysql``` của Icinga2

![](./images/Icinga_1.png)


```icinga2-ido-mysql``` package yêu cầu 1 database được cài đặt và cấu hình. Điều này có thể được thực hiện tự động với ```dbconfig-common```, nhưng ta có thể tự tạo thủ công, nên ta chọn ```No``` ở đây

![](./images/Icinga_2.png)

Tiếp đến, đăng nhập vào MariaDB database server

```sh
mysql -u root -p
```

Tạo database và database user

```sh
CREATE DATABASE icinga_ido_db;
GRANT ALL ON icinga_ido_db.* TO 'icinga_ido_user'@'localhost' IDENTIFIED BY 'ghjlarewsngjlan';
FLUSH PRIVILEGES;
EXIT;
```

Import **Icinga2 IDO schema**

```sh
mysql -u root -p icinga_ido_db < /usr/share/icinga2-ido-mysql/schema/mysql.sql
```

Kích hoạt Icinga2 IDO Module

Để kích hoạt ```icinga2-ido-mysql``` với Icinga Web 2, ta thực hiện thay đổi file cấu hình mặc định của feature

```sh
vi /etc/icinga2/features-available/ido-mysql.conf
```

Sửa các thông tin sau

```sh
object IdoMysqlConnection "ido-mysql" {
  user = "icinga_ido_user"
  password = "ghjlarewsngjlan"
  host = "localhost"
  database = "icinga_ido_db"
}
```

Kích hoạt feature

```sh
icinga2 feature enable ido-mysql
```

Restart service icinga2

```sh
systemctl restart icinga2
```

Cài đặt và thiết lập IcingaWeb2

Cài đặt **icingaweb2** và **Icinga CLI**

```sh
apt install icingaweb2 icingacli -y
```

Tạo database cho IcingaWeb2

```sh
mysql -u root -p
```

```sh
CREATE DATABASE icingaweb2;
GRANT ALL ON icingaweb2.* TO 'icingaweb2user'@'localhost' IDENTIFIED BY 'gbjraeswbgj';
FLUSH PRIVILEGES;
EXIT;
```

Tạo 1 token để sử dụng cho quá trình thiết lập **Icinga2 Web**

```sh
icingacli setup token create
```

Nếu quên token, ta có thể dùng lệnh sau để show

```sh
icingacli setup token show
```