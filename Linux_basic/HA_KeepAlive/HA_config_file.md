# Cấu trúc file cấu hình của HAProxy

File cấu hình của HA thường được tạo từ 4 thành phần chính bao gồm ```global```, ```defaults```, ```frontend```, ```backend```. Hãy cùng tìm hiểu từng thành phần để hiểu rõ hơn về HA.

## Cấu trúc

Có sự khác nhau giữa vị trí file cấu hình của 2 phiên bản EE - Enterprise Edition và CE - Community Edition. Trong bài này sử dụng phiên bản CE.

File cấu hình thường được lưu tại ```/etc/haproxy/haproxy.cfg``` với cấu trúc:

```sh
global
    # Các thiết lập tổng quan
defaults
    # Các thiết lập mặc định
frontend
    # Thiết lập điều phối các request
backend
    # Định nghĩa các server xử lý request
```

Khi sử dụng dịch vụ HA, các thiết lập tại ```global``` sẽ được sử dụng để định nghĩa cách HA được khởi tạo như số lượng kết nối tối đa, đường dẫn ghi file log, số process,.... Sau đó các thiết lập tại mục ```defaults``` sẽ được áp dụng cho tất cả mục ```frontend```, ```backend``` nằm phía sau (các cấu hình ở phần frontend và backend sẽ đè lên thiết lập mặc định). Có thể có nhiều mục ```frontend```, ```backend``` được định nghĩa trong file cấu hình. Mục ```frontend``` được định nghĩa để điều hướng các request nhận được tới các ```backend```. Mục ```backend``` để định nghĩa các danh sách máy chủ dịch vụ (webserver, database,...) là nơi request được xử lý

## Global

```global``` luôn đứng riêng 1 dòng và được định nghĩa 1 lần duy nhất trong file cấu hình

```sh
global
    log         127.0.0.1 local2
    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     4000
    user        haproxy
    group       haproxy
    daemon
    stats socket /var/lib/haproxy/stats
```

Trong đó
- **maxconn**: chỉ định giới hạn số kết nối mà HA có thể thiết lập. Sử dụng với mục đích bảo vệ load balancer khỏi vấn đề tràn RAM sử dụng
- **log**: bảo đảm các cảnh báo phát sinh tại HAProxy trong quá trình khởi động, vận hành sẽ được gửi tới syslog
- **stats socket**: định nghĩa runtime api, có thể sử dụng để disable server hoặc health check, đổi balancing weight của server
- **user / group**: chỉ định quyền sử dụng để khởi tạo tiến trình HAProxy. Linux yêu cầu xử lý bằng quyền root cho port nhỏ hơn 1024. Nếu không định nghĩa user và group thì HA sẽ tự động sử dụng root để thực thi tiến trình

## Defaults

Khi cấu hình tăng dần, phức tạp, khó đọc, các thiết lập cấu hình tại mục ```defaults``` giúp giảm các trùng lặp. Thiết lập tại mục ```defaults``` sẽ áp dụng cho tất cả mục ```frontend```, ```backend``` nằm sau nó (nhưng sẽ bị 2 mục này overwrite nếu có cùng thiết lập)

Có thể có nhiều mục ```defaults```. Chúng sẽ ghi đè lên nhau dựa theo vị trí (tức các mục ```defaults``` nằm sau sẽ ghi đè lên ```defaults``` nằm trước)

Ví dụ, nếu tại ```defaults``` có thiết lập **mode http** thì các mục ```frontend```, ```backend```, ```listen``` sau đó sẽ đều dùng **mode http** làm mặc định

```sh
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
    option                  http-server-close
    option forwardfor       except 127.0.0.0/8
    option                  redispatch
    retries                 3
    option  http-server-close
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          1m
    timeout server          1m
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000
```

Trong đó:
- ```timeout connect```: chỉ định thời gian HA đợi thiết lập kết nối TCP tới backend server. Ở đây thời gian timeout là 10 giây, nếu không có ```s``` thì sẽ là 10 mili giây
- ```timeout server``` chỉ định thời gian chờ kết nối tới backend server. Khi thiết lập ```mode tcp``` thời gian ```timeout server``` phải bằng ```timeout client```
- ```log global```: chỉ định frontend sẽ sử dụng log settings mặc định (trong mục ```global```)
- ```mode```: thiết lập ```mode``` định nghĩa HA sẽ sử dụng TCP proxy hay HTTP proxy. Cấu hình sẽ áp dụng với toàn ```frontend``` và ```backend``` khi bạn chỉ mong muốn sử dụng 1 mode mặc định trên toàn ```backend``` (có thể thiết lập lại giá trị tại ```backend```)
- ```maxconn```: thiết lập chỉ định số kết nối tối đa, mặc định bằng 2000
- ```option httplog```: bổ sung format log dành riêng cho các request http bao gồm (connection timers, session status, connections numbers, header,...). Nếu sử dụng cấu hình mặc định các tham số sẽ chỉ bao gồm địa chỉ nguồn và địa chỉ đích
- ```option http-server-close```: khi sử dụng kết nối dạng keep-alive, tùy chọn cho phép sử dụng lại các kênh kết nối tới máy chủ (có thể kết nối đã đóng) nhưng kênh kết nối vẫn tồn tại, thiết lập sẽ giảm độ trễ khi mở lại kết nối từ client tới server
- ```option dontlognull```: bỏ qua các log format không chứa dữ liệu
- ```option forwardfor```: sử dụng khi mong muốn backend server nhận được IP thực của người dùng kết nối tới. Mặc định backend server sẽ chỉ nhận được IP của HAProxy khi nhận được request. Header của request sẽ bổ sung thêm trường ```X-Forwarded-For``` khi sử dụng tùy chọn
- ```option redispatch```: trong mode HTTP, khi sử dụng kỹ thuật ```sticky session```, client sẽ luôn kết nối tới 1 backend server duy nhất, tuy nhiên khi backend server xảy ra sự cố, có thể client không thể kết nối tới backend server khác (trong bài toán load balancer). Sử dụng tùy chọn này cho phép HA phá vỡ kết nối giữa client và backend server đã xảy ra sự cố. Đồng thời, client này có thể khôi phục kết nối tới backend server ban đầu khi dịch vụ tại backend server đó trở lại bình thường
- ```retries```: số lần thử kết nối lại backend server trước khi HA đánh giá backend server đó gặp sự cố
- ```timeout check```: kiểm tra thời gian đóng kết nối (chỉ khi kết nối đã được thiết lập)
- ```timeout http-request```: thời gian chờ trước khi đóng kết nối HTTP
- ```timeout queue```: khi số lượng kết nối giữa client và HA đạt tối đa, các kết nối tiếp theo sẽ vào hàng đợi. Tùy chọn này sẽ làm sạch kết nối mỗi 1 khoảng thời gian được chỉ định (ví dụ ở đây là 1 phút)

## Frontend

Mục ```frontend``` định nghĩa địa chỉ IP và port mà client có thể kết nối tới. Có thể có nhiều mục ```frontend``` tùy ý, chỉ cần đặt label của chúng khác nhau

Ví dụ:

```sh
frontend www.mysite.com
    bind 10.0.0.3:80
    bind 10.0.0.3:443 ssl crt /etc/ssl/certs/mysite.pem
    http-request redirect scheme https unless { ssl_fc }
    use_backend api_servers if { path_beg /api/ }
    default_backend web_servers
```

Trong đó:
- ```bind```: IP và port HA sẽ lắng nghe để mở kết nối. IP có thể bind tất cả địa chỉ sẵn có hoặc chỉ 1 địa chỉ duy nhất, port có thể là một port hoặc nhiều port (1 khoảng hoặc 1 list)
- ```http-request redirect```: phản hồi tới client với đường dẫn khác. Ứng dụng khi client sử dụng http và phản hồi từ HA là https, điều hướng người dùng sang giao thức https
- ```use_backend```: chỉ định backend sẽ xử lý request nếu thỏa mãn điều kiện (khi sử dụng ACL)
- ```default_backend```: backend mặc định sẽ xử lý request (nếu request không thỏa mãn bất kỳ điều hướng nào)

## Backend

Mục ```backend``` định nghĩa tập server sẽ được cân bằng tải khi có các kết nối tới (VD tập các server chạy dịch vụ web giống nhau)

Ví dụ:

```sh
backend web_servers
    balance roundrobin
    cookie SERVERUSED insert indirect nocache
    option httpchk HEAD /
    default-server check max conn 20
    server node1 10.10.10.86:80 cookie node1
    server node2 10.10.10.87:80 cookie node2
```

Trong đó:
- ```balance```: kiểm soát cách HA nhận, điều phối request tới các backend server. Đây chính là các thuật toán cân bằng tải
- ```cookie```: sử dụng cookie-based. Cấu hình sẽ khiến HA gửi cookie tên SERVERUSED tới client, liên kết backend server với client. Từ đó các request xuất phát từ client sẽ tiếp tục phiên với server chỉ định. Cần thêm tùy chọn ```cookie``` ở dòng khai báo server backend nữa thì mới hoạt động được.
- ```option httpchk```: với tùy chọn này, HA sẽ sử dụng ```health check``` dạng HTTP (layer 7) thay vì kiếm trả kết nối dạng TCP (Layer 4). Và khi server không phản hồi request http, HA sẽ thực hiện TCP check tới IP Port. Health check sẽ tự động loại bỏ các backend server lỗi, khi không có backend server sẵn sàng xử lý request, HA sẽ phản hồi mã 500 Server Error. Mặc định HTTP check sẽ kiểm tra root path ```/``` (có thể thay đổi). Và nếu phản hồi health check là 2xx, 3xx sẽ được coi là thành công
- ```default-server```: bổ sung tùy chọn cho bất kỳ backend server nào thuộc backend label này (như health check, max connection,...)
- ```serrver```: tùy chọn quan trọng nhất trong ```backend``` section. Tùy chọn đi kèm bao gồm **tên**, **IP:port**. Có thể dùng domain thay cho IP

## Listen

```Listen``` là sự kết hợp của cả 2 mục ```frontend``` và ```backend```. Vì ```listen``` kết hợp cả 2 tính năng ```backend```, ```frontend```, vì vậy có thể dùng ```listen``` thay cho 2 mục kia cũng đc

Ví dụ:

```sh
listen web-backend
    bind 10.10.10.89:80
    balance leastconn
    cookie SERVERID insert indirect nocache
    mode http
    option forwardfor
    option httpchk GET / HTTP/1.0
    option httpclose
    option httplog
    timeout client 3h
    timeout server 3h
    server node1 10.10.10.86:80 weight 1 check cookie s1
    server node2 10.10.10.87:80 weight 1 check cookie s2
    server node3 10.10.10.88:80 weight 1 check cookie s3
```

Cú pháp thường dùng:

```sh
listen web-backend
    ...
    server node1 10.10.10.86:80 inter <time> rise <number> fall <number>
```

Trong đó:
- ```inter```: khoảng thời gian giữa 2 lần check liên tiếp
- ```rise```: số lần kiểm tra backend server thành công trước khi HA đánh giá nó đang hoạt động bình thường và bắt đầu điều hướng request tới
- ```fall```: số lần kiểm tra backend server bị tính là thất bại trước khi HA đánh giá nó xảy ra sự cố và không điều hướng request tới 