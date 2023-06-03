# Tối ưu hóa cấu hình Apache httpd

## 1. Nén dữ liệu

Có thể bạn đã biết, hầu hết dữ liệu vận chuyển từ webserver (ngoại trừ hình ảnh) đều là text-based.

Và text file thì lại là dữ liệu hiệu quả nhất để nén lại. Mặc dù vậy thì việc nén dữ liệu lại bị mặc định disable đi, kích hoạt điều này lên là 1 cách nhanh nhất để giảm thiểu trễ trên đường vận chuyển và tăng tốc cho website lên đến 80%.

Đầu tiên, hãy chắc chắn là Module httpd đã được kích hoạt:

```sh
LoadModule deflate_module modules/mod_deflate.so
```

Hoặc

```sh
a2enmod deflate_module
```

Sau đó, hãy thêm đoạn cấu hình này vào httpd configuration file, hoặc module configuration fule:

```sh
<IfModule deflate_module>
  AddOutputFilterByType DEFLATE text/plain
  AddOutputFilterByType DEFLATE text/css
  AddOutputFilterByType DEFLATE application/json application/x-javascript  text/javascript application/javascript text/js
  AddOutputFilterByType DEFLATE text/xml application/xml application/xml+rss text/javascript application/javascript
  AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>
```

## 2. Kích hoạt browser caching

Mặc định, trình duyệt sẽ lưu trữ local các dữ liệu của website để tránh thu thập nó nhiều lần khi bạn truy cập lại cùng 1 trang đó.

Mỗi trình duyệt lại có cơ chế riêng, tuy nhiên webserver có thể cung cấp khả năng điều khiển cache và expiration dates của cache ngay trong headers khi phản hồi lại trình duyệt.

### Cache control

Hãy kích hoạt module ```mod_headers``` (hoặc ```headers```) của Apache:

```sh
LoadModule headers_module modules/mod_headers.so
```

Sau đó bạn có thể thêm cấu hình như sau:

```sh
<IfModule mod_headers.c>
 <FilesMatch "\.(ico|jpe?g|png|gif|css|woff2)$">
   Header set Cache-Control "max-age=2592000, public"
 </FilesMatch>
</IfModule>
```

### Expire

Kích hoạt module ```mod_expires``` (hoặc ```expires```) của Apache:

```sh
LoadModule expires_module modules/mod_expires.so
```

Và sử dụng cấu hình như sau:

```sh
<IfModule mod_expires.c>
  AddType application/x-font-woff .woff
  AddType image/svg+xml .svg

  ExpiresActive On

  ExpiresDefault "access plus 7200 seconds"
  ExpiresByType image/jpg "access plus 1 month"
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/gif "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/x-icon "access plus 1 month"
  ExpiresByType application/x-font-woff "access plus 1 month"
  <FilesMatch \.php$>
    # Không nên cho phép cache PHP scripts trừ khi chúng tự gửi cache headers.
    ExpiresActive Off
  </FilesMatch>
</IfModule>
```

## 3. Kết luận

Trong bài này, Nhân Hòa đã giới thiệu về 2 cách cơ bản nhất để tối ưu tốc độ tải website của Apache httpd. 

Tuy nhiên tối ưu hóa website là câu chuyện không bao giờ có hồi kết, do đó, hãy tiếp tục theo dõi [Wiki Nhân Hòa](wiki.nhanhoa.com) để biết thêm về những tip and trick thú vị nhé.

Chúc các bạn luôn may mắn và thành công trong công việc!