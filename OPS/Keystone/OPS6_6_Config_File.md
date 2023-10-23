# File config của Keystone

File cấu hình mặc định của keystone nằm tại ```/etc/keystone/keystone.conf```

## Cấu trúc file config

OpenStack sử dụng INI file format cho file config

INI file là 1 file text đơn giản thể hiện các options theo các cặp giá trị ```key = value```, chúng được nhóm lại thành section

**Section:**

Các tùy chọn cài đặt được nhóm lại thành các section. Thông thường hầu hết các file config của OpenStack đều có 2 section ```[DEFAULT]``` và ```[database]```

Các options có thể có các giá trị khác nhau, dưới đây là các loại thường được sử dụng bởi OpenStack
- ```boolean```
- ```float```
- ```integer```
- ```list```
- ```multi valued```: là 1 string value có thể gán nhiều hơn 1 giá trị, tất cả sẽ đều được sử dụng
- ```string```

**Substitution**

File config hỗ trợ variable substitution. Sau khi thiết lập, tùy chọn cấu hình đó có thể được dùng lại trong các tùy chọn khác bằng dấu ```$```, VD như ```rabbit_hosts = $rabbit_host:$rabbit_port```

Để tránh substitution, dùng ```$$```. VD ```ldap_dns_password = $$g23b45kj```

**Whitespace**

Để sử dụng khoảng trắng trong phần value, sử dụng dấu nháy đơn ```''```

VD: ```ldap_dns_password='a password with spaces'```

**Lưu ý:** Hầu hết các service sẽ load file cấu hình khi khởi động. Để thay đổi nơi đặt file cấu hình, thêm tùy chọn ```--config-file FILE``` vào khi start dịch vụ hoặc dùng câu lệnh ```*-manage```

## II. API configuration options

### Section ```[DEFAULT]```

|Option|Type|Description|
|:-|:-|:-|
|```admin_token = <None>```|string|Không nên sử dụng giá trị này. Giá trị của tùy chọn này là một đoạn mã dùng để khởi động Keystone thông qua API. Token này không được hiểu là user và nó có thể vượt qua hầu hết các công đoạn kiểm tra quyền hạn|
|```public_endpoint = <None>```|URI|URL Endpoint cơ sở của Keystone cho Client. Chỉ nên set option này trong trường hợp giá trị của base URL chứa đường dẫn mà Keystone không thể tự suy luận hoặc endpoint ở server khác|
|```max_project_tree_depth = 5```|integer|Số lượng tối đa của cây project. Lưu ý: đặt giá trị cao có thể làm ảnh hưởng đến hiệu suất|
|```max_param_size = 64```|integer|Giới hạn kích thước của ID/names|
|```max_token_size = 255```|integer|Giới hạn kích thước Token. Mặc định là 255 dành cho Fernet token|
|```list_limit = <None>```|integer|Số lượng entities lớn nhất có thể được trả lại trong 1 collection. Với những hệ thống lớn nên set option này để tránh những câu lệnh hiển thị danh sách users, projects cho ra quá nhiều dữ liệu không cần thiết|
|```strict_password_check = false```|boolean|Nếu được set thành true, Keystone sẽ kiểm soát nghiêm ngặt thao tác với mật khẩu, nếu mật khẩu quá chiều dài tối đa, nó sẽ không được chấp nhận. Còn đặt False thì mật khẩu sẽ tự động bị cắt ngắn đến độ dài tối đa|

### Section ```[endpoint_filter]```

|Option|Type|Description|
|:-|:-|:-|
|```driver = sql```|string|backend driver cho dịch vụ của Keystone|
|```return_all_endpoints_if_no_filter = True```|boolean|Trả lại toàn bộ active endpoints nếu không có endpoints nào được tìm thấy theo yêu cầu|

### Section ```[eventlet_server]```

|Option|Type|Description|
|:-|:-|:-|
|```admin_bind_host = 0.0.0.0```|host address|Địa chỉ IP của cổng mạng cho admin service lắng nghe|
|```admin_port = 35357```|port number|port mà admin service lắng nghe|
|```admin_workers = None```|integer|Số lượng CPU phục vụ công việc quản trị|
|```client_socket_timeout = 900```|integer|Thời gian tồn tại kết nối bằng câu lệnh socket trên phía client. Giá trị "0" có nghĩa là phải chờ mãi mãi|
|```public_bind_host = 0.0.0.0```|host address|Địa chỉ IP của cổng mạng cho public service lắng nghe|
|```public_port = 5000```|integer|port mà public service lắng nghe|
|```public_workers = None```|integer|Số lượng CPU phục vụ các ứng dụng public|

### Section ```[oslo_middleware]```

|Option|Type|Description|
|:-|:-|:-|
|```max_request_body_size = 114688```|integer|Kích thước tối đa cho mỗi request (tính bằng bytes)|

### Section ```[resource]```

|Option|Type|Description|
|:-|:-|:-|
|```admin_project_domain_name = None```|string|Tên của domain sở hữu admin_project_name|
|```caching = True```|boolean|Không có tác dụng cho tới khi global caching được kích hoạt|
|```domain_name_url_safe = off```|string|3 giá trị được set: ```off```, ```new```, ```strict```. Điều này kiểm soát xem tên miền có bị hạn chế chứa các ký tự dành riêng URL không. Nếu không đặt thành ```new```, các nỗ lực tạo hoặc cập nhật tên miền có tên không an toàn URL sẽ không thành công. Nếu đặt thành ```strict```, mọi cố gắng sử dụng token với URL không an toàn sẽ bị fail nên buộc tên miền phải cập nhật thành an toàn|

## III. Assignment configuration options

### Section ```[assignment]```

|Option|Type|Description|
|:-|:-|:-|
|```driver = sql```|string|Trình điều khiển phụ trợ (nơi lưu trữ phân công vai trò) trong Keystone assignment|
|```prohibited_implied_role```|list|Danh sách các role bị cấm trở thành implied role|

## IV. Authorization configuration options

### Section ```[auth]```

|Option|Type|Description|
|:-|:-|:-|
|```external = <None>```|string|Điểm vào cho auth plugin module, mặc định sẽ là Default Domain|
|```methods = external,password,token,oauth1,mapped,application_credential```|list|Các phương thức xác thực được phép sử dụng|
|```oauth1 = <None>```|string|Điểm vào cho OAuth 1.0 auth plugin module|
|```password = <None>```|string|Điểm vào cho module xác thực mật khẩu|
|```token = <None>```|string|Điểm vào cho module xác thực bằng token|

## V. Catalog configuration

### Section ```[catalog]```

|Option|Type|Description|
|:-|:-|:-|
|```cache_time = <None>```|integer|Thời gian để cache dữ liệu catalog (đơn vị giây). Tùy chọn này sẽ không có hiệu lực cho đến khi global và catalog caching được kích hoạt|
|```caching = true```|boolean|Kích hoạt catalog caching, nó sẽ không có tác dụng cho tới khi global caching được kích hoạt|
|```driver = sql```|string|Điểm vào cho catalog backend driver|
|```list_limit = <None>```|integer|Số lượng thực thể tối đa được trả về trong catalog. Thông thường không có lý do để đặt điều này, vì sẽ là bất thường khi 1 triển khai lại đặt giới hạn số lượng services hay endpoints|
|```template_file = default_catalog.templates```|string|Catalog template file name để sử dụng với template catalog backend|

## VI. Common configuration options

### Section ```[DEFAULT]```

|Option|Type|Description|
|:-|:-|:-|
|```executor_thread_pool_size = 64```|integer|Kích thước của nhóm luồng thực thi khi thuực thi là luồng hoặc sự kiện|