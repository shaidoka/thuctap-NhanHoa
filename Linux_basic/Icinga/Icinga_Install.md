# Cài đặt Icinga

Cài đặt dependency

```sh
apt install software-properties-common ca-certificates lsb-release apt-transport-https libboost-coroutine-dev
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
apt update 
```

Cài đặt php 7.4

```sh
apt install php7.4
```

**Lưu ý:** Để thay đổi phiên bản php default, ta dùng lệnh ```update-alternatives --config php```

