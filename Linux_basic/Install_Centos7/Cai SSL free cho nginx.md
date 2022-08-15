# Cài đặt SSL Let's Encrypt

## Apache webserver

1. Cài đặt Epel repository

```yum -y install epel-release```

2. Cài đặt certbot cho apache

```yum -y install certbot python2-certbot-apache mod_ssl```

3. Cài đặt SSL Let's Encrypt

```certbot --apache -d tubui.xyz -d www.tubui.xyz```

Nhập vào email -> Chọn **Y** để đồng ý điều khoản dịch vụ -> Chọn **N** để từ chối nhận thông tin tiếp thị

Đường dẫn lưu file chứng chỉ: ```/etc/letsencrypt/live/tubui.xyz/fullchain.pem

4. Kiểm tra

Kiểm tra ở địa chỉ [SSL Checker](https://www.sslshopper.com/ssl-checker.html)

## Nginx webserver

Với Nginx, chúng ta thực hiện tương tự, chỉ khác ở 2 lệnh:

```sh
#Cài đặt certbot
yum install -y cerbot-nginx
#Cài đặt SSL Let't Encrypt
certbot --nginx -d tubui.xyz -d www.tubui.xyz
```