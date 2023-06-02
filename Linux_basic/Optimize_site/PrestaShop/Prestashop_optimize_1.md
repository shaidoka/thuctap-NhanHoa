# Tối ưu hiệu suất của PrestaShop

Trước khi thực hiện bất kỳ thay đổi nào trên website của bạn, mình khuyến khích các bạn nên thực hiện benchmark nó trước.

Mục đích của việc này là giúp chúng ta biết được hiệu suất cơ sở của website là bao nhiêu, nhờ đó có cái nhìn chính xác hơn là những thay đổi ta thực hiện đem lại kết quả tích cực hay ngược lại.

Hãy nhớ rằng: **Benchmark** -> **Thay đổi** -> **Lặp lại**

## 1. PHP

Điều chỉnh PHP rất quan trọng cho hiệu suất ứng dụng của bạn, bất kể bạn sử dụng PrestaShop hay bất kỳ ứng dụng PHP nào khác.

Đầu tiên, hãy sử dụng PHP version từ 7.0 trở lên. Những lập trình viên viết nên PHP đã thực hiện rất nhiều công việc để tối ưu hiệu suất ứng dụng kể từ phiên bản này, và nó có thể sẽ cung cấp 1 bước nhảy vọt về hiệu năng so với các phiên bản tiền nhiệm.

Nếu bạn đang sử dụng PHP-FPM, bạn sẽ phải kiểm tra cấu hình ```pool```, thường thì nó sẽ nằm ở ```/etc/php/7.x/fpm/pool.d/www.conf```. Trong khi đó nếu sử dụng FastCGI thì hãy thực hiện thiết lập ở ```/etc/php/7.1/apache2/php.ini```. Nói chung, hãy tìm kiếm file cấu hình tùy theo môi trường mà bạn sử dụng.

Hãy thay đổi thiết lập tối ưu hiệu suất như sau đây:

```sh
[Date]
date.timezone = Asia/Ho_Chi_Minh

[Session]
session.auto_start = 0

[PHP]
short_open_tag = Off
display_errors = Off

; Hãy tăng tham số dưới đây tùy vào hệ thống của bạn, không nên nhiều hơn 4096
memory_limit = 512M
max_execution_time = 300
max_input_time = 300
upload_max_filesize = 20M
post_max_size = 22M
max_input_vars = 20000
allow_url_fopen = on
```

## 2. PHP và file system

Chúng ta đều biết rằng PHP không quản lý file system quá tốt.

Đó là lý do có rất nhiều tùy chọn thay đổi hữu ích để tránh truy cập file system liên tục.

### realpath_cache

Ở mỗi lần truy cập file, mặc định PHP sẽ đầu tiên kiểm tra liệu file có còn ở vị trí đó không, tạo ra rất nhiều lệnh gọi hệ thống ```lstat```.

PHP cung cấp 1 tùy chọn để lưu trữ thông tin này trong cache, nhờ đó tránh lặp lại các lệnh gọi liên tục:

```sh
[PHP]
realpath_cache_size = 4096K
realpath_cache_ttl = 600
```

Hãy nhớ rằng, những tùy chọn trên không tương thích với các tham số như ```open_basedir``` và ```safe_mode```

Nếu bạn đang sử dụng storage từ xa như NAS hoặc bất kỳ giải pháp lưu trữ qua internet nào khác thì mình rất khuyến khích sử dụng setting này.

### opcache

Các thay đổi liên quan tới file system không dừng lại ở đó, ta không chỉ có thể cache đường dẫn của file, mà còn là nội dung của nó.

Tin tốt, OPCache sẽ không chỉ lưu trữ PHP file của bạn trong RAM, mà nó sẽ còn lưu trữ trong bytecode, điều này có nghĩa là ứng dụng đã được biên dịch, trong bộ nhớ dùng chung, có sẵn cho tất cả lệnh gọi của ứng dụng:

```sh
[opcache]
opcache.enable=1
opcache.enable_cli=0
opcache.memory_consumption=256
opcache.interned_strings_buffer=32
opcache.max_accelerated_files=16229
opcache.max_wasted_percentage=10
opcache.revalidate_freq=10
opcache.fast_shutdown=1
opcache.enable_file_override=0
opcache.max_file_size=0
```

Nếu bạn có thể quản lý nó, thì đây là 1 vài options bạn có thể thiết lập:

```sh
opcache.validate_timestamps=0
opcache.revalidate_path=0
```

Lưu ý rằng nếu bạn tắt ```validate_timestamps```. OPCache sẽ không bao giờ cập nhật code của bạn, trừ khi bạn cho nó biết khi nào nên làm điều này (bằng các hàm hoặc bằng việc restart web server).

## 3. Composer

Class loader được sử dụng trong khi phát triển ứng dụng được tối ưu hóa để tìm các lớp mới và đã thay đổi. Trên production server, PHP file không nên được thay đổi, trừ khi có 1 phiên bản mới của ứng dụng được triển khai. Đó là lý do tại sao bạn nên tối ưu Composser autoloader để quét toàn bộ ứng dụng một lần và xây dựng 1 "class map". Nó là 1 mảng lớn chứa toàn bộ vị trí của các class, lưu trữ ở ```vendor/composer/autoload_classmap.php```

Thực thi lệnh sau để tạo class map

```sh
composer dump-autoload --optimize --no-dev --classmap-authoriative
```

Trong đó:
- ```--optimize```: dump mọi lớn PSR-0 và PSR-4 tương thích sử dụng trong ứng dụng của bạn
- ```--no-dev```: loại trừ những class mà chỉ cần thiết trong môi trường phát triển (ví dụ: tests)
- ```--classmap-authoriative```: ngăn Composer quét file system mà không tìm thấy trong class map

*Lưu ý: Nếu bạn cài đặt 1 module mới, bạn sẽ cần thực thi lệnh này lại*

## 4. Apache

Nếu bạn đang sử dụng PHP-FPM, bạn nên kích hoạt Apache mpm_event module. Sử dụng cấu hình như sau:

```sh
   ServerLimit             16
   MaxClients              400
   StartServers            3
   ThreadLimit             64
   ThreadsPerChild         25
   MaxRequestWorkers       400
   MaxConnectionsPerChild  0
```

## 5. MySQL/MariaDB

Các thay đổi cho MySQL hay MariaDB cũng rất quan trọng. Trong phần này chúng ta sẽ tập trung vào tối ưu thông lượng của database bằng cách thêm vào cache.

Đối với PHP, nó cho phép service làm việc trong RAM nhiều nhất có thể và tránh truy cập ổ cứng, nhờ đó giảm độ trễ.

### Caching

Những tham số này cho phép cache thông tin tốt hơn cho việc sử dụng lại, đầu tiên hãy kích hoạt nó, sau đó là tăng kích thước lên. Một lần nữa, ý tưởng ta muốn làm ở đây là giữ kết quả truy vấn trong RAM thay vì ở các ổ đĩa cứng, thứ mà sẽ tăng độ trễ.

Các giá trị sau đây thực sự nên thay đổi để phù hợp với môi trường mà bạn sử dụng:

```sh
query_cache_limit = 128K 
query_cache_size = 32M
query_cache_type = ON
table_open_cache = 4000
thread_cache_size = 80
```

### Buffering

Buffering gần như là 1 cách nói khác của caching.

Vì vậy, việc chúng ta làm ở đây với RAM là giữ cache data cho InnoDB tables, indexes, và các buffer phụ trợ khác.

Các thông số sau nên được thay đổi cho phù hợp với hệ thống bạn sử dụng:

```sh
read_buffer_size			= 2M 
read_rnd_buffer_size		= 1M
join_buffer_size			= 2M 
sort_buffer_size 			= 2M
innodb_buffer_pool_size 	= 1G
```

Thiết lập ```innodb_buffer_pool_size``` lên 1G có thể khá nhiều, hãy chắc chắn bạn có đủ RAM để cung cấp cho nó. Điều quan trọng là, nếu có thể, hãy đưa ```innodb_buffer_pool_size``` lên giá trị **cao hơn** kích thước database của bạn.

### Các tham số khác

Dưới đây là 1 vài tham số để cải thiện hiệu suất MySQL, như tắt performance schema (sử dụng cho monitoring), memory tables và tối ưu truy vấn GROUP BY.

## 6. Kết luận

Tối ưu hóa là một bài toán không bao giờ có lời giải chính xác, do đó các phương án đưa ra bên trên chỉ là phần nào giúp cho ứng dụng của bạn tốt hơn mà thôi.

Hãy tiếp tục theo dõi các bài viết khác tại [Wiki Nhân Hòa](wiki.nhanhoa.com) để hiểu thêm về tối ưu hóa và nhiều kiến thức khác nhé.

Chúc các bạn luôn thành công và may mắn trong công việc!