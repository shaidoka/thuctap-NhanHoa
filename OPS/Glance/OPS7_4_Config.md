# Tìm hiểu cách cấu hình Glance

## I. Các file cấu hình của Glance

Các tệp cấu hình của glance đều nằm trong thư mục ```/etc/glance```

Có tất cả 7 tệp cấu hình như sau:
- **glance-api.conf**: file cấu hình cho các api của image service
- **glance-registry.conf**: file cấu hình cho glance image registry - nơi lưu trữ metadata về các images
- **glance-api-paste.ini**: cấu hình cho các API middleware pipeline của Image service
- **glance-manage.conf**: là tệp cấu hình ghi chép tùy chỉnh. Các tùy chọn thiết lập trong tệp này sẽ ghi đè lên các section cùng tên trong các tệp **glance-registry.conf** và **glance-api.conf**. Tương tự như vậy, các tùy chọn thiết lập trong **glance-api.conf** sẽ ghi đè lên tùy chọn thiết lập trong **glance-registry.conf**
- **glance-registry-paste.ini**: tệp cấu hình middle pipeline cho các registry của Image service
- **glance-scrubber.conf**: tiện ích sử dụng để dọn sạch các images đã ở trạng thái **deleted**. Nhiều glance-scrubber có thể chạy trong triển khai, tuy nhiên chỉ có một scrubber được thiết lập để dọn dẹp cấu hình trong file ```scrubber.conf```. Cleanup scrubber này kết hợp với các scrubber khác bằng cách duy trì một hàng đợi chính của các images cần được loại bỏ. Tệp ```glance-scrubber.conf``` cũng đặc tả cấu hình các giá trị quan trọng như khoảng thời gian giữa các lần chạy, thời gian chờ của các images trước khi bị xóa. Glance-scrubber có thể chạy theo định kỳ hoặc có thể chạy như một daemon trong khoảng thời gian dài
- **policy.json**: file tùy chọn được thêm vào để điều khiển truy cập áp dụng với image service. Trong file ta có thể định nghĩa các roles và policies. Đó là tính năng bảo mật trong OpenStack Glance

## II. Cấu hình log của Glance

Mặc định Glance có 2 file nhật ký lưu trong thư mục ```/var/log/glance```:
- ```glance-api.log```: ghi lại lịch sử truy cập api server
- ```glance-registry.log```: ghi lại lịch sử liên quan tới reigstry server

Để thay đổi file log mặc định, thực hiện chỉnh sửa cấu hình trong file ```/etc/glance/glance-api.conf```. Thay đổi các tùy chọn về file ghi lại log trong section ```[DEFAULT]``` trong file cấu hình ```glance-api.conf```

```sh
[DEFAULT]
log_file = /var/log/glance/api.log
```

Một số option tùy chọn với log:
- ```log_file```: đường dẫn tới file được sử dụng để ghi log cho các glance server
- ```log_dir```: đường dẫn tới thư mục chứa các file ghi log
- ```log_date_format```: đinh dạng chuỗi hiển thị thời gian trong file log đầu ra. Mặc định là ```%Y-%m-%d %H:%M:%S```
- ```log_use_syslog```: lựa chọn có sử dụng các chức năng log của hệ thống hay không (mặc định là False)

## III. Cấu hình backend lưu trữ Glance

Có nhiều cách cấu hình các option trong glance để điều khiển việc lưu trữ các disk image. Những cấu hình này được xác định trong section ```[glance_store]``` của file cấu hình ```glance-api.conf```

```sh
default_store=<STORE>
```

Mặc định là ```file```, một số tùy chọn khả dụng là: filw, swift, sheepdog, cinder hoặc vsphere. Để có thể thiết lập là backend lưu trữ mặc định thì nó phải được liệt kê ở:

```sh
stores=<STORES>
```

Mặc định là file, http. Một vài giá trị khác khả dụng là: filesystem, http, rbd, swift, sheepdog, cinder, vmware_datastore (mỗi giá trị cách nhau bởi dấu ",")

### 1. Cấu hình backend filesystem

```sh
filesystem_store_datadir = PATH
```

- Xác định đường dẫn tới thư mục lưu trữ image nếu sử dụng backend là ```filesystem```. Mặc định là trong thư mục: ```/var/lib/glance/images/```
- Nếu thiết lập một đường dẫn tới một thư mục chưa tồn tại, thì sau khi khởi động lại **glance-api** thì thư mục sẽ tự động được tạo

### 2. Cấu hình backend filesystem với nhiều thư mục lưu trữ (multiple stores)

Thêm tùy chọn như sau:

```sh
filesystem_store_datadirs=PATH:PRIORITY
```

Ban đầu, mặc định thư mục ```/var/lib/glance/images/:1``` được gán với độ ưu tiên là 1

VD:

```sh
filesystem_store_datadirs = /var/glance/store
filesystem_store_datadirs = /var/glance/store1:100
filesystem_store_datadirs = /var/glance/store2:200
```

Option này chỉ sử dụng với **backend filesystem**

Tùy chọn ```filesystem_store_datadirs``` cho phép người quản trị admin cấu hình đa thư mục lưu trữ để lưu trữ các glance image trong hệ thống backend filesystem. Mỗi thư mục được kết hợp với độ ưu tiên (sau dấu ":") để xác định mức độ ưu tiên khi thêm image (số càng lớn ưu tiên càng cao)

## IV. Cấu hình size image

Cấu hình trong section ```[DEFAULT]``` file ```glance-api.conf```:

```sh
image_size_cap=<SIZE>
```

Mặc định là 1TB

Giá trị kích thước lớn nhất của image (tính theo byte) có thể upload thông qua glance API server (bắt buộc phải nhỏ hơn 8EB)

## V. Configuring glance user storage quota

Cấu hình tùy chọn trong section ```[DEFAULT]``` file ```glace-api.conf```:

```sh
user_storage_quota=<value>
```

Mặc định là 0 (không giới hạn)

Giá trị này xác định lượng data nhiều nhất mà user có thể lưu trữ trong hệ thống lưu trữ (đơn vị là B, KB, MB, GB hoặc TB)

VD: ```user_storage_quota=20GB```

## VI. Cấu hình image cache

### 1. Cấu hình sử dụng glance cache

Để kích hoạt hay tắt glance cache, tiến hành cấu hình trong file ```/etc/glance/glance-api.conf```. Để kích hoạt cached, tìm tới dòng sau và cấu hình:

```sh
[paste_deploy]
flavor = keystone+cachemanagement
```

Tắt glance cache:

```sh
[paste_deploy]
flavor = keystone
```

Glance cache được cấu hình trong 2 file: ```glance-api.conf``` để cấu hình cho glance-api server, và file ```glance-cache.conf``` cấu hình cho các tiện ích dùng glance

### 2. Một số cấu hình tùy chọn cho file glance-api.conf

- ```image_cache_dir```: Đường dẫn tới thư mục lưu trữ dữ liệu cache của glance (yêu cầu phải được thiết lập, không có giá trị mặc định)

- ```image_cache_sqlite_db```: Đường dẫn tới file sqlite file database quản lý cache. Thư mục này liên quan tới thư mục image_cache_dir (mặc định là: cache.db)

- ```image_cache_driver```: backend hỗ trợ cho quản lý cache (mặc định là sqlite)

- ```image_cache_max_size```: thiết lập kích thước tối đa cho phép lưu trữ trước khi glance-cache-pruner xóa đi những image cũ nhất (mặc định là 10GB)

- ```image_cache_stall_time``` thiết lập thời gian mà một image chưa hoàn thành được lưu trong cache. Sau thời gian đó mà image chưa hoàn thành thì sẽ bị xóa (mặc định là 1 ngày)

### 3. Cấu hình cho glance-cache.conf

- ```admin_user```: username cho tài khoản người dùng admin, để có thể lấy các dữ liệu của image từ cache

- ```admin_password```: password cho tài khoản admin

- ```admin_tenant_name```: tenant của admin (project)

- ```auth_url```: URL được sử dụng để xác thực với Keystone. Đây sẽ là token trong biến môi trường nếu đã được thiết lập

- ```filesystem_store_datadir```: thiết lập thư mục lưu trữ image nếu sử dụng backend là filesystem

- ```filesystem_store_datadirs```: multiple directories trong backend filesystem

- ```registry_host```: URL tới glance registry

### 4. Kiểm soát kích thước của glance cache

- Glance image cache được cấu hình lưu trữ tối đa bao nhiêu trong option ```image_cache_max_size``` trong file ```glance-api.conf```

- Khi các image được trả về thành công từ lời gọi ```GET /images/<IMAGE_ID>```, image cache được tự động viết các file image vào cache, miễn là khi đó cache vẫn còn khả năng lưu trữ

- Để kiểm soát kích thước của cache, cần thường xuyên sử dụng câu lệnh sau để ngăn không cho kích thước cache vượt quá mức cho phép

```sh
glance-cache-pruner
```

- Để xóa các image cũ, chạy câu lệnh

```sh
glance-cache-cleaner
```

Khuyến cáo nên sử dụng cron để chạy tự động các câu lệnh trên để quản lý và kiểm soát glance image cache

### 5. Prefetching images into the image cache

Một vài image có thể được thường xuyên sử dụng để boot các máy ảo. Khi chyaj một API server mới, người quản trị có thể muốn lấy các image này vào trong local image cache để đảm bảo rằng sẽ có những image phổ biến được đưa vào trong local cache
- Để queue một image để prefetching, có thể sử dụng câu lệnh sau để đưa image đó vào queue:

```sh
glance-cache-manage --host=<HOST> queue-image <IMAGE_ID>
```

- Sau khi đã queue được image mà muốn prefetch, có thể sử dụng câu lệnh sau để đưa image đó vào local cache:

```sh
glance-cache-prefetcher
```

## VII. Cấu hình glance registry

Thực hiện cấu hình trong file ```glance-registry.conf``` tại section ```[DEFAULT]```

*(lưu ý: glance-registry chỉ được sử dụng để kết hợp dịch vụ glance-api khi client sử dụng v1 REST API)*

```sh
sql_connection=<CONNECTION_STRING (or --sql-connection on command line)>
```

Mặc định là None. Có thể xác định trong file cấu hình hoặc câu lệnh glance-manage

```sh
sql_timeout=<SECONDS>
```

Mặc định là 3600s, thời gian tồn tại kết nối sau khi không có hoạt động gì tương tác với lưu trữ dữ liệu

```sh
enable_v1_registry=<True|False>
enable_v2_registry=<True|False>
```

Giá trị mặc định cho 2 option trên là True. Xác định loại version mà registry API kích hoạt
- Nếu glance API server được thiết lập ```enable_v1_api``` là ```True``` thì ```enable_v1_registry``` cũng phải là ```True```
- Nếu glance API server thiết lập ```enable_v2_api``` là ```True``` và ```data_api``` là ```glance.db.registry.api``` thì tùy chọn ```enable_v2_registry``` cũng thiết lập là ```True```

## VIII. Cấu hình glance API

Dịch vụ glance-api phục vụ 2 version 1 và 2 của Openstack image API. Để disable bất kì image API nào sử dụng các option sau tại section ```[DEFAULT]```

```sh
enable_v1_api=<True|False>
enable_v2_api=<True|False>
```

Mặc định là True

Để sử dụng v2 registry trong v2 API, phải thiết lập ```data_api=glance.db.registry.api```

## IX. Cấu hình image format

Chỉnh sửa trong section ```[image_format]``` trong file ```glance-api.conf```

Cấu hình các giá trị có thể được liệt kê, phân tác bởi dấu ","

Liệt kê các container_format được hỗ trợ:

```sh
container_formats = ami, ari, aki, bare, ovf, ova, docker
```

Liệt kê các disk_format được hỗ trợ:

```sh
disk_formats = ami, ari, aki, vhd, vhdx, vmdk, raw, qcow2, vdi, iso, ploop
```