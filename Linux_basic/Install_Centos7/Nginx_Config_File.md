# Tìm hiểu về tệp cấu hình của Nginx

## Cấu trúc và cách sử dụng tệp cấu hình

- Tất cả file cấu hình của nginx đều nằm trong thư mục ```/etc/nginx/```
- File cấu hình chính của nginx là ```/etc/nginx/nginx.conf```
- Document root directory ```/usr/share/nginx/html```
- Nginx bao gồm các module được điều khiển bởi các directive trong file cấu hình. "Directive" được định nghĩa như 1 instruction (chỉ dẫn) hay direct. Directives được chia thành các directive đơn giản và các block directive
    - Cấu trúc của 1 directive đơn giản gồm tên và tham số được phân tách bởi dấu cách và kết thúc bằng dấu chấm phẩy. VD ```worker_processes 1;```
    - 1 block directive có cấu trúc tương tự như 1 directive đơn giản nhưng thay vì sử dụng dấu ```;``` nó sẽ sử dụng cặp dấu ```{}``` để bắt đầu và kết thúc 1 block directive. 1 config file điển hình của nginx có thể được minh họa như hình dưới

![](./images/nginx_config_file_1.png)

- Một main context sẽ bao gồm nhiều directive đơn giản, nhiều context (VD: context A, context B) chứa các block directive

## Cách sử dụng config file hợp lí và hiệu quả

- Tạo 1 file cấu hình riêng cho mỗi tên miền sẽ giúp server dễ quản lý và hiệu quả hơn
- Nginx không có virtual host, thay vào đó là ```Server Blocks``` sử dụng ```server_name``` và nghe các chỉ thị để liên kết với các tcp sockets. Tất cả các file server block phải có định dạng là ```.conf``` và được lưu trong thư mục ```/etc/nginx/conf.d``` hoặc ```etc/nginx/conf```
- Nếu bạn có 1 domain là ```mydomain.com``` thì bạn nên đặt tên file cấu hình là ```mydomain.com.conf```
- Nếu bạn sử dụng các phân đoạn cấu hình có thể lặp lại trong các khối máy chủ tên miền của mình, bạn nên cấu trúc lại các phân đoạn đó thành các đoạn
- Các file nhật ký nginx (access.log và error.log) được đặt trong thư mục ```/var/log/nginx/```. Nếu có 1 tệp nhật ký access và error khác nhau cho mỗi server block
- Bạn có thể đặt document root directory của tên miền của bạn đến bất kỳ vị trí nào bạn muốn. 1 số vị trí thường được dùng cho webroot bao gồm:
    - /home/<user_name>/<site_name>
    - /var/www/<site_name>
    - /var/www/html/<site_name>
    - /opt/<site_name>
    - /usr/share/nginx/html

## Các thao tác cần thực hiện trước và sau khi chỉnh sửa config file

- Trước khi thay đổi cấu hình, sao lưu lại file cấu hình

```sh
cp /etc/nginx/conf/nginx.conf /etc/nginx/conf/nginx.conf.backup
```

- Định kỳ sao lưu tập tin cấu hình nginx

```sh
cp /etc/nginx/conf/nginx.conf /etc/nginx/conf/nginx.conf.$(date "+%b_%d_%Y_%H.%M.%S")
```

- Sau khi thực hiện thay đổi cấu hình trong file cấu hình, restart lại service 

```sh
systemctl restart nginx
```

**Chú ý:**
- Tất cả những dòng có dấu "#" phía trước là những dòng chú thích (comment) được sử dụng để giải thích những khối lệnh dùng làm gì hoặc để lại ý kiến làm thế nào chỉnh sửa giá trị
- Ngoài ra, bạn cũng có thể thêm riêng những comment theo ý của mình. Bạn có thể cho đoạn mã đó được kích hoạt bằng cách loại bỏ các ```#```
- Cài đặt bắt đầu với những tên biến và sau đó 1 đối hay một loạt các đối số cách nhau bởi dấu cách
- Một số thiết lập được đặt trong 1 cặp dấu ngoặc nhọn ({}). Các dấu ngoặc nhọn có thể được lồng vào nhau cho nhiều khối lệnh, cần nhớ là khi đã mở ngoặc nhọn thì phải đóng nó lại không thì nginx sẽ không thể chạy được
- Sử dụng tab hay space để phân cấp đoạn mã sẽ giúp dễ dàng chỉnh sửa hay tìm ra lỗi

## Tìm hiểu chi tiết về config file

**Core Contexts**

Đây là nhóm đầu tiên của contexts, được nginx sử dụng để tạo ra 1 cây phân cấp và tách biệt các cấu hình giữa các block. Trong đây cũng bao gồm các cấu hình chính của nginx

**Main Context**

Cũng có thể coi là global context. Đây là context chung nhất bao gồm tất cả các directive đơn giản, block directive và các context khác

1 config file của nginx sẽ trông như thế lày:

```sh
#user   nobody;
worker_processes    1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include         mime.types;
    default_type    application/octet-stream;
    
    #log_format main    '$remote_addr - $remote_user [$time_local] "$request"'
    #                   '$status $body_bytes_sent "$http_referer"'
    #                   '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log logs/access.log main;

    sendfile    on;
    #tcp_nopush on;

    #keepalive_timeout  0;
    keepalive_timeout   65;

    #gzip   on;

    server {
        listen      80;
        server_name localhost;

        #charset    koi8-r;

        #access_log logs/host.access.log    main

        location / {
            root    html;
            index   index.html  index.htm;
        }

        #error_page 404     /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page  500 502 503 504 /50x.html;
        location = /50x.html {
            root    html;
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        # location ~ \.php$ {
        #    proxy_pass http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        # location ~ \.php$ {
        #    proxy_pass http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        # location ~ \.php$ {
        #    root            html;
        #    fastcgi_pass    127.0.0.1:9000;
        #    fastcgi_index   index.php;
        #    fast_param      SCRIPT_FILENAME     /scripts$fastcgi_script_name;
        #    include         fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny    all;
        #}
    }

    # another virtual host using mix of IP-, name-, and port-based configuration
    #
    #server {
    #    listen      8000;
    #    listen      somename:8000;
    #    server_name somename    alisas  another.alias;

    #    location / {
    #        root    html;
    #        index   index.html  index.htm;
    #    }
    #}

    # HTTPS server
    #
    #server {
    #    listen      443 ssl;
    #    server_name localhost;

    #    ssl_certificate     cert.pem;
    #    ssl_certificate_key cert.key;

    #    ssl_session_cache   share:SSL:1m;
    #    ssl_session_timeout 5m;

    #    ssl_ciphers HIGH:!aNULL:!MD5;
    #    ssl_prefer_server_ciphers   on;

    #    location / {
    #        root    html;
    #        index   index.html  index.htm;
    #    }
    #}
}
```

- File bắt đầu cùng với 4 directives: user, worker_precesses, error_log, và pid. Chúng nằm ngoài bất kỳ block hay context cụ thể nào do đó nằm trong main context (bối cảnh chính). Các event và http block là khu vực cho các directives bổ sung do đó chúng cũng nằm trong main context. Xem NGINX docs để xem giải thích cụ thể về những directive này và các giá trị directive khác trong main context
- Giải thích cụ thể:
    - ````user````: định nghĩa cho biết người dùng hệ thống Linux nào sẽ có quyền chạy các máy chủ Nginx. Có những trường hợp sử dụng nhất định mà được hưởng lợi từ việc thay đổi người dùng. Ví dụ, bạn chạy 2 máy chủ web cùng 1 lúc, hoặc cần người sử dụng của 1 chương trình khác để có thể kiểm soát Nginx
    - ```worker_precess```: có giá trị mặc định là 1. Nó định nghĩa số lượng worker process nên được set bằng giá trị với số core của CPU. Ví dụ với các webserver hay sử dụng về SSL, gzip thì ta nên đặt chỉ số worker_processes này lên cao hơn. Nếu website của bạn có số lượng các tên tin tĩnh nhiều, và dung lượng của chúng lớn hơn bộ nhớ RAM thì việc tăng worker_processes sẽ tối ưu băng thông đĩa của hệ thống. Để xác định số cores của CPU của hệ thống ta có thể thực hiện lệnh: ```cat /proc/cpuinfo | grep processor```
    - ```access_log``` & ```error_log```: những file mà Nginx sử dụng để log lại toàn bộ error và access request. Phần log này thường được sử dụng để debug
    - ```pid```: xác định nơi nginx sẽ ghi lại master process ID, hoặc PID. PID được sử dụng bởi hđh để theo dõi và gửi tín hiệu đến Nginx process. Có thể xác định thông tin về PID (master process và worker process) của nginx bằng câu lệnh ```ps -ax | grep nginx```
    - ```worker_connections```: cho biết số lượng connection mà mỗi worker_process có thể xử lý. Mặc định, số lượng connection này được thiết lập là 1024. Để xem về mức giới hạn sử dụng của hệ thống, bạn có thể sử dụng lệnh ```ulimi -n```. Con số thiết lập của worker_connections nên nhỏ hơn hoặc bằng giới hạn này
    - ```max clients``` = ```worker_connections``` + ```worker_processes```

**Event Context**

```sh
events {
    worker_connections  1024;
}
```

- Nginx sử dụng mô hình xử lý kết nối dựa trên sự kiện nên các directive được định nghĩa trong context này sẽ ảnh hưởng đến connection processing được chỉ định. VD ở trên là cấu hình số worker connection mà mỗi worker process có thể xử lý được

**HTTP Context**

- Khi cấu hình Nginx như 1 webserver hoặc reverse proxy, http context sẽ giữ phần lớn cấu hình. Context này sẽ chứa tất cả các directive và những context (block directive) cần thiết khác để xác định cách chương trình sẽ xử lý các kết nối HTTP và HTTPS
- Giải thích 1 số directive:
    - ```include```: chỉ thị include (include /etc/nginx/mime.types) của nginx có vai trò trong việc thêm nội dung từ 1 file khác vào trong cấu hình nginx. Điều này có nghĩa là bất cứ điều gì được viết trong tập tin mime.types sẽ được hiểu là nó được viết bên trong khối http {} mà không gây lộn xộn lên các tập tin cấu hình chính. Và nó giúp tránh quá nhiều dòng mã cho mục đích dễ đọc. Bạn luôn có thể bao gồm (include) tất cả các tập tin trong 1 thư mục nhất định với các chỉ thị: ```include /etc/nginx/conf/*```. Bạn cũng có thể bao gồm tất cả các file theo 1 định dạng nào đó, như ```include /etc/nginx/conf/*.conf``` -> Nó sẽ bao gồm các tập tin có đuôi .conf
    - ```gzip```: chỉ thị gzip sẽ giúp nén các dữ liệu trước khi chuyển chúng tới Client, hạn chế số lượng băng thông sử dụng và tăng tốc độ dịch chuyển dữ liệu. Điều này tương đương với mod_deflate của Apache. 1 số chỉ thị sau đây có thể thêm vào để tăng hiệu quả của gzip:

```sh
gzip_vary       on;
gzip_proxied    any;
gzip_comp_level 6;
gzip_buffers    116 8k;
gzip_http_version   1.1;
gzip_types  text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;
```

**Server Context**

- Được khai báo trong http context. Đây cũng là 1 ví dụ về context lồng nhau được đặt trong ngoặc. Đây cũng là context đầu tiên cho phép khai báo nhiều lần
- Định dạng chung của server context có thể trông như này:

```sh
# main context
http {
    # http context
    server {
        # first server context
    }
    server {
        # second server context
    }
}
```

- Dựa vào yêu cầu từ phía client, nginx sẽ sử dụng thuật toán lựa chọn để quyết định server context nào được sử dụng. Các directive được sử dụng để quyết định server context nào được sử dụng là:
    - ```listen```: tổng hợp các IP/port mà server block này được thiết kế để đáp ứng. Nếu 1 yêu cầu từ phía client phù hợp với giá trị này, block này có thể được lựa chọn để xử lý kết nối 
    - ```server_name```: nếu có nhiều server block đáp ứng được yêu cầu của directive, nginx sau đó sẽ tiến hành phân tích cú pháp tiêu đề "Host" của yêu cầu và lựa chọn block phù hợp

**Location Context**

- Được đặt trong server context
- Sau khi đã chọn được server context nào sẽ tiếp nhận request này thì nginx sẽ tiếp tục phân tích URI của request để tìm ra hướng xử lí của request dựa vào các location context có syntax như sau:

```sh
location optional_modifier location_match {
    ...
}
```

- Trong đó:
    - ```optional_modifier```: có thể hiểu là kiểu so sánh để tìm và đối chiếu với ```location_match```
    - ```location_match```: có vài loại location_match sau
        - ```(none)```: nếu không khai báo gì thì nginx sẽ hiểu là tất cả các request có URI bắt đầu bằng phần location_match sẽ được chuyển cho location block này xử lí
        - ```=```: khai báo này chỉ ra rằng URI phải có chính xác giống như location_match
        - ```~```: sử dụng regular expression cho các URI
        - ```~*```: sử dụng regular expression cho các URI không phân biệt chữ hoa chữ thường

- VD:

```sh
location /site {
    ...
}
```

- Các request có URI dạng như sau ```/site```, ```/site/page/1```, ```site/index.html``` sẽ được xử lí thông qua location này

```sh
location = /site {
    ...
}
```

- Với khai báo như bên trên thì chỉ có ```/site``` sẽ có thể được xử lí, còn ```/site/page/1``` hay ```site/index.html``` thì không

```sh
location ~ \.(jpe?g|png|gif|ico)$ {
    ...
}
```

- Các request có đuôi .jpg, .jpeg, .png, .png, .gif, .ico có thể pass qua location này nhưng .PNG thì không

```sh
location ~* \.(jpe?g|png|gif|ico)$ {
    ...
}
```

- Giống bên trên nhưng pass cả chữ hoa vs chữ thường

- Thông thường khi mà location block được dùng để phục vụ 1 request nào đó thì action sẽ hoàn toàn nằm trong context của nó (bên trong dấu {}). Và nó sẽ chỉ nhảy sang các block khác hay chuyển hướng xử lí request khi có yêu cầu từ chính bên trong context của nó. 1 vài directive có thể redirective request như:
    - index
    - try_files
    - rewrite
    - error_page

**index directive**

index direct nằm bên trong location luôn được nginx trỏ tới đầu tiên khi xử lí điều hướng request. Định nghĩa trang mặc định mà nginx sẽ phục vụ nếu không có tên tập tin được chỉ rõ trong yêu cầu (nói cách khác, trang chỉ mục). Chúng ta có thể chỉ rõ nhiều tên tập tin và tập tin đầu tiên được tìm thấy sẽ được sử dụng. Nếu không có tập tin cụ thể nào được tìm thấy, nginx sẽ hoặc là tự động sinh 1 chỉ mục 

```sh
location = / {
    index index.html;
}
```

**try_files directive**

Cố gắng phục vụ các tập tin được chỉ rõ (các tham số từ 1 đến N-1 trong chỉ thị), nếu không có tập tin nào tồn tại, nhảy đến khối location được khai báo (tham số cuối cùng trong chỉ thị) hoặc phục vụ 1 URI được chỉ định

```sh
location / {
    try_files $uri $uri.html $uri/ /fallback/index.html;
}
```

**rewrite directive**

Khác với Apache, nginx không sử dụng file .htaccess nên khi bạn cần rewrite url sẽ phải convert qua rule của nginx. VD:

```sh
location /download/ {
    rewrite ^(/download/.*)/media/(.*)\..*$ $1/mp3/$2.mp3 break;
    rewrite ^(/download/.*)/audio/(.*)\..*$ $1/mp3/$2.ra break;
    return 403;
}
```

**error_page directive**

Chỉ thị khi không tìm thấy file tham chiếu

```sh
location / {
    error_page 404 = @fallback;
}

location @fallback {
    proxy_pass http://backend;
}
```

- Xử lý trong location context:
    - Nginx sẽ đọc root directive để xác định thư mục chứa trang client yêu cầu. Thứ tự các trang được ưu tiên sẽ được khai báo trong index directive
    - Nếu không tìm được nội dung mà client yêu cầu, nginx sẽ điều hướng sang location context khác và thông báo lỗi cho người dùng

- VD1:

```sh
location / {
    root html;
    index index.html index.htm;
}
```

- Trong ví dụ này, document root là thư mục ```html/```. Trong cài đặt mặc định của nginx, đường dẫn đầy đủ đến thư mục này là ```/etc/nginx/html/```. Do đó nếu Request đến là ```http://example.com/blog/includes/style.css``` thì nginx sẽ tìm đến tệp tin ```/etc/nginx/html/blog/includes/style.css```

- VD2:

```sh
location / {
    root /srv/www/example.com/public_html;
    index index.html index.htm;
}
location ~ \.pl$ {
    gzip off;
    include /etc/nginx/fastcgi_params;
    fastcgi_pass unix:/var/run/fcgiwrap.socket;
    fastcgi_index index.pl;
    fastcgi_param SCRIPT_FILENAME
    /srv/www/example.com/public_html$fastcgi_script_name;
}
```

- Trong ví dụ này, tất cả các yêu cầu tài nguyên kết thúc bằng phần mở rộng .pl được xử lý bởi location context thứ 2, chỉ định trình xử lý fastcgi cho các yêu cầu này. Mặt khác, nginx sử dụng chỉ thị vị trí đầu tiên. Tài nguyên được đặt trên hệ thống tệp tại thư mục ```/srv/www/example.com/public_html/```. Nếu không tìm thấy tệp chỉ mục, máy chủ sẽ trả về lỗi 404. Cụ thể:
    - **Request**: ```http://example.com/```
    -> **Return**: ```/srv/www/example.com/public_html/index.html``` nếu nó tồn tại. Nếu file .html không tồn tại, file ```/srv/www/example.com/public_html/index.htm``` sẽ được sử dụng. Nếu cả 2 file không tồn tại thì trả về 404 error
    - **Request**: ```http://example.com/blog/```
    -> **Return**: ```/srv/www/example.com/public_html/blog/index.html``` nếu nó tồn tại. Nếu file ```.html``` không tồn tajim nó sẽ sử dụng ```srv/www/example.com/public_html/blog/index.htm```. Nếu cả 2 không tồn tại thì trả về 404 error
    - **Request**: ```http://example.com/tasks.pl```
    -> **Return**: nginx sẽ sử dụng FastCGI handler để thực thi file có tại ```/srv/www/example.com/public_html/tasks.pl``` và trả về kết quả
    - **Request**: ```http://example.com/username/roster.pl```
    -> **Return**: nginx sẽ sử dụng FastCGI handler để thực thi file có tại ```/srv/www/example.com/public_html/username/roster.pl``` và trả về kết quả
