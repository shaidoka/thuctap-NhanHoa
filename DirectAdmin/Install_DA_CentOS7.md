# Cài DirectAdmin trên CentOS 7

1. Cài đặt các gói cần thiết cho DA

```sh
yum install wget gcc gcc-c++ flex bison make bind bind-libs bind-utils openssl openssl-devel perl quota libaio libcom_err-devel libcurl-devel gd zlib-devel zip unzip libcap-devel cronie bzip2 cyrus-sasl-devel perl-ExtUtils-Embed autoconf automake libtool which patch mailx bzip2-devel lsof glibc-headers kernel-devel expat-devel
```

```sh
yum install -y psmisc net-tools systemd-devel libdb-devel perl-DBI xfsprogs rsyslog logrotate crontabs file
```

2. Tải DA và cài đặt

```sh
get http://www.directadmin.com/setup.sh
chmod 755 setup.sh
./setup.sh
```

**Lưu ý:** Nhập License Key được cung cấp khi đăng ký DA nếu được hỏi trong quá trình cài đặt

3. Sau khi cài đặt, vào đường dẫn sau để lấy thông tin đăng nhập trang quản trị

```vi /usr/local/directadmin/scripts/setup.txt```

4. Truy cập vào trang quản trị DA bằng đường dẫn tubui.xyz:2222