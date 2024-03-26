# Sử dụng Service Tokens

Khi 1 người dùng khởi tạo 1 request mà xử lý liên quan đến nhiều services (chẳng hạn, 1 boot-from-volume request đến Compute Service sẽ yêu cầu xử lý bởi Block Storage Service, và có thể là cả Image Service nữa), token của người dùng này được "truyền tay" từ service này sang service khác. Điều này đảm bảo rằng người yêu cầu được theo dõi chính xác để xác thực và cũng chắc chắn là người yêu cầu có đúng quyền hạn để thực hiện công việc nào đó với các services khác.

Có 1 vài trường hợp mà chúng ta cần phải phân biệt giữa 1 request đến từ người dùng và request đến từ Openstack service khác trên danh nghĩa người dùng:
- **Vì mục đích bảo mật:** có một vài operation trong Block Storage service yêu cầu normal operation, mà có thể bị khai thác bởi malicious user để lấy quyền truy nhập vào các tài nguyên thuộc về người dùng khác. Bằng cách phân biệt request nào đến từ người dùng, request nào đến từ Openstack service khác, Cinder có thể bảo vệ triển khai của mình
- Để bảo vệ những job cần thời gian dài để hoàn thành: Nếu chuỗi operations kéo quá dài, token của người dùng có thể expire trước khi hành động được hoàn thành, dẫn đến request gốc của người này bị fail

Có 1 cách để xử lý vấn đề trên là tăng life-time của token lên trong Keystone. Nhưng nó cũng có thể là vấn đề do các policies về security hiện nay thường yêu cầu short-life user token. Bắt đầu từ bản Queens, 1 giải pháp thay thế khác đã khả dụng. Bạn có khả năng để cấu hình một vài services (cụ thể là Nova và Cinder) để gửi 1 "service token" bên cạnh user's token. Khi cấu hình chính xác, Identity Service sẽ xác thực 1 expired user token khi nó đi kèm với 1 service token. Theo đó, nếu token của người dùng expired ở công đoạn nào đó trong chuỗi operations giữa các OpenStack services, operations đó vẫn có thể tiếp tục.

## Cấu hình

Để cấu hình 1 Openstack service mà hỗ trợ Service Token, như Nova và Cinder, để gửi 1 "service token" cùng với user's token khi nó thực hiện 1 request từ service khác, bạn cần làm các việc sau:

- Cấu hình "sender" services để gửi token khi gọi các Openstack services khác
- Cấu hình mỗi service's user để có 1 service role trong Keystone
- Cấu hình "receiver" services để nhận token và xác thực nó một cách thích hợp khi nhận được

### Gửi service token

Để gửi token chúng ta cần thêm ```[service_user]``` vào cấu hình của service. Trong hầu hết trường hợp chúng ta sẽ sử dụng cùng user và cấu hình với ```[keystone_authtoken]```. Ví dụ:

```sh
[service_user]
send_service_user_token = True

# Copy following options from [keystone_authtoken] section
project_domain_name = Default
project_name = service
user_domain_name = Default
password = abc123
username = nova
auth_url = http://192.168.121.66/identity
auth_type = password
```

### Service role

1 service role không gì hơn là 1 Keystone role mà cho phép 1 triển khai có thể xác minh với 1 service mà không cần khiến họ thành admin, bằng cách này, ta không cần thay đổi quyền hạn nhưng vẫn có thể xác minh requst đến từ các service khác và không phải 1 user.

Service role mặc định là **service**, nhưng ta có thể sử dụng 1 tên khác hoặc thậm chí nhiều service roles. Để đơn giản thì chúng tôi khuyên rằng bạn chỉ cần sử dụng **service** thôi.

Chúng ta cần chắc chắn rằng người dùng được cấu hình trong ```[service_user]``` cho 1 project có 1 service role.

Giả sử người dùng của chúng ta là **nova** và **cinder** từ project **service** và service role cũng mặc định là **service** đi. Chúng ta cần check xem role này có tồn tại không:

```sh
openstack role show service
```

Nếu không, hãy tạo nó

```sh
openstack role create service
```

Kiểm tra người dùng đã được cấp role trên chưa

```sh
openstack role assignment list --user cinder --project service --names
openstack role assignment list --user nova --project service --names
```

Và đương nhiên, nếu họ chưa được cấp role thì ta hãy thực hiện điều đó

```sh
openstack role add --user cinder --project service service
openstack role add --user nova --project service service
```

### Nhận service token

Bây giờ chúng ta cần phải khiến service xác minh service token khi nhận được nó.

Có 2 tùy chọn cấu hình trong ```[keystone_authoken]``` liên quan đến nhận service token là ```service_token_roles``` và ```service_token_roles_required```.

```service_token_roles``` chứa 1 danh sách các roles mà chúng ta cân nhắc để thuộc về services. Service user phải thuộc về ít nhất 1 trong số chúng để là 1 service token khả dụng. Giá trị mặc định là **service**, vì vậy chúng ta không cần phải thiết lập nó nếu đó là giá tị mà ta đang sử dụng

Bây giờ chúng ta cần nói với keystone middleware để thực sự xác minh service token và confirm rằng nó không phải token duy nhất hợp lệ, nhưng nó có 1 roles đặt trong ```service_token_roles```. Chúng ta làm điều này bằng cách thiết lập ```service_token_roles_required``` thành true.

Vì vậy, chúng ta sẽ phải cấu hình ```[keystone_authtoken]``` như sau

```sh
[keystone_authtoken]
service_token_roles = service
service_token_roles_required = true
```

