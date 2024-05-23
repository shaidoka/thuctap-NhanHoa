# Glance - Image service

## Glance backends

### Overview

Glance có thể được triển khai sử dụng Kolla và hỗ trợ những loại backend sau:

- file
- ceph
- vmware
- swift

### File backend

Khi sử dụng ```file``` backend, images sẽ được lưu trữ local tại đường dẫn được chỉ định trong biến ```glance_file_datadir_volume```, thứ mà mặc định là 1 container gọi là ```glance```. Mặc định khi sử dụng ```file``` backend, chỉ có 1 ```glance-api``` container có thể chạy.

Để tăng tính tin cậy và hiệu suất, ```glance_file_datadir_volume``` nên được mount dưới 1 shared filesystem như NFS

Ví dụ, ta có thể cấu hình như sau:

```sh
glance_backend_file: "yes"
glance_file_datadir_volume: "/path/to/shared/storage/"
```

### Ceph backend

Để sử dụng ```ceph``` backend cho glance, đơn giản là enable external ceph. Lúc này, mặc định ceph backend cho glance sẽ được bật tự động. Hãy xem thêm về cách cấu hình External Ceph ở các bài sau.

Để enable ceph backend cho glance thủ công, hãy cấu hình tham số sau:

```sh
glance_backend_ceph: "yes"
```

### VMware backend

Để sử dụng VMware datastore cho glance backend, hãy enable ```glance_backend_vmware``` và xem thêm về cách cấu hình Vmware - Nova Virtualization Driver để biết thêm về cách cấu hình Vmware

Để bật vmware backend thủ công:

```sh
glance_backend_vmware: "yes"
```

### Glance with S3 Backend

Cấu hình Glance cho S3 bao gồm các bước sau:

1. Kích hoạt Glance S3 backend trong ```globals.yml```

```sh
glance_backend_s3: "yes"
```

2. Cấu hình kết nối S3 trong ```globals.yml```, ví dụ:

- ```cinder_backup_s3_url``` (VD: http://127.0.0.1:9000)
- ```cinder_backup_s3_access_key``` (VD: minio)
- ```cinder_backup_s3_bucket``` (VD: cinder)
- ```cinder_backup_s3_secret_key``` (VD: admin)

Nếu ta muốn sử dụng 1 S3 backend cho tất cả các dịch vụ được hỗ trợ, sử dụng các biến sau:

- ```s3_url```
- ```s3_access_key```
- ```s3_glance_bucket```
- ```s3_secret_key```

### Swift backend

Để lưu trữ glance images trong 1 swift cluster, ```swift``` backend nên được enable. Hãy xem thêm cách cấu hình Swift trong Kolla để biết thêm thông tin chi tiết. Nếu ceph được enabled, ceph sẽ được ưu tiên sử dụng làm backend cho glance hơn.

Để enable swift backend thủ công:

```sh
glance_backend_swift: "yes"
```

## Upgrade glance

### Overview

Glance có thể được upgrade với các phương pháp sau đây:

- Rolling upgrade
- Legacy upgrade

### Rolling upgrade

Từ bản Rocky, glance có thể được nâng cấp trong 1 rolling upgrade mode. Mode này sẽ giảm thời gian API downtime trong quá trình upgrade xuống tối thiểu bằng thời gian mà container restart.

Mặc định thì chế độ này bị disabled, vì vậy nếu muốn sử dụng nó, hãy cấu hình:

```sh
glance_enable_rolling_upgrade: "yes"
```

**Lưu ý: Khi sử dụng glance backend là file mà không sử dụng 1 shared filesystem, cách thức này sẽ không thể sử dụng hoặc sẽ dẫn đến trạng thái corrupt của glance service. Lý do cho điều này là glance api lúc này chỉ chạy trên 1 host, chặn sự điều phối của 1 rolling upgrade**

### Legacy upgrade

Cách thức upgrade này sẽ dừng APIs trong quá trình chuyển dịch database schema + thời gian container restarts.

Đây là chế độ mặc định, hãy đảm bảo rolling upgrade không được bật nếu muốn sử dụng legacy upgrade:

```sh
glance_enable_rolling_upgrade: "no"
```

## Các cấu hình khác

### Glance cache

Glance cache được disable theo mặc định, ta có thể bật nó lên bằng cách:

```sh
enable_glance_image_cache: "yes"
glance_cache_max_size: "10737418240" # 10GB by default
```

**Lưu ý: Khi sử dụng ceph backend thì không nên sử dụng glance cache, vì nova đã có 1 phiên bản cache của image đó rồi, và image được copy trực tiếp từ ceph thay vì từ glance api host. Bật glance cache lúc nãy sẽ chỉ khiến phí phạm tài nguyên lưu trữ**

Glance cache không được cleaned up tự động, glance team khuyên rằng người quản trị nên sử dụng cron để định kỳ clean cache.

Đọc thêm: [Glance image cache](https://docs.openstack.org/glance/latest/admin/cache.html)

### Property protection

[Property protection](https://docs.openstack.org/glance/latest/admin/property-protections.html) được disable theo mặc định, nó có thể enable lên bằng:

```sh
glance_enable_property_protection: "yes"
```

và định nghĩa ```property-protections-rules.conf``` bên dưới ```{{ node_custom_config }}/glance/```. Giá trị mặc định của ```property_protection_rule_format``` là ```roles``` nhưng nó có thể được ghi đè.

### Interoperable image import

[Interoperable image import](https://docs.openstack.org/glance/latest/admin/interoperable-image-import.html) được disable theo mặc định, nó có thể được enable bằng:

```sh
glance_enable_interoperable_image_import: "yes"
```

và định nghĩa ```glance-image-import.conf``` dưới ```{{ node_custom_config }}/glance/```