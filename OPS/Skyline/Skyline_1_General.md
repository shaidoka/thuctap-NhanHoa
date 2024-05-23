# Skyline API Server

Skyline là 1 OpenStack dashboard được tối ưu bởi UI và UE, hỗ trợ OpenStack Train trở lên. Nó có 1 kiến trúc công nghệ hiện đại, và dễ dàng cho developers có thể bảo trì và vận hành, cũng như có hiệu suất tốt hơn nhiều.

## Quick Start

### Prerequisites

- 1 OpenStack environment mà đang có ít nhất là các thành phần trong core project của OpenStack
- 1 Linux Server với container engine được cài đặt (docker hay podman đều ok)

### Configure

1. Chỉnh sửa file ```/etc/skyline/skyline.yaml``` trên linux server:

Bạn có thể tìm file mẫu ở đây [sample file](https://opendev.org/openstack/skyline-apiserver/src/branch/master/etc/skyline.yaml.sample), và chỉnh sửa các tham số sau theo môi trường cụ thể:

- database_url
- keystone_url
- default_region
- interface_type
- system_project_domain
- system_project
- system_user_domain
- system_user_name
- system_user_pasword

### Deployment with Sqlite

1. Chạy skyline_bootstrap container để bootstrap:

```sh
rm -rf /tmp/skyline && mkdir /tmp/skyline && mkdir /var/log/skyline

docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

# Check bootstrap is normal `exit 0`
docker logs skyline_bootstrap
```

2. Chạy skyline service sau khi bootstrap thành công

```sh
docker rm -f skyline_bootstrap
```

Nếu bạn cần thay đổi skyline port, hãy thêm ```-e LISTEN_ADDRESS=<ip:port>``` trong lệnh triển khai. Nếu bạn cần thay đổi các rule chính sách của service, hãy thêm ```-v /etc/skyline/policy:/etc/skyline/policy``` trong lệnh triển khai. Hãy đổi tên serivce policy yaml file thành ```<service_name>_policy.yaml```, và đặt nó dưới ```/etc/skyline/policy```.

```sh
docker run -d --name skyline --restart=always -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest
```

### Deployment with MariaDB

1. Tạo database

```sh
mysql
```

```sh
CREATE DATABASE skyline DEFAULT CHARACTER SET \
  utf8 DEFAULT COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' \
  IDENTIFIED BY 'WB12MWPlbt0uVnYa2BxCwg7rwoQZRCQhvwHZNxjr';
GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%' \
  IDENTIFIED BY 'WB12MWPlbt0uVnYa2BxCwg7rwoQZRCQhvwHZNxjr';
FLUSH PRIVILEGES;
exit
```

2. Source admin credentials

```sh
source admin-openrc
```

3. Tạo service credentials

```sh
openstack user create --domain default --password-prompt skyline
```

```sh
openstack role add --project service --user skyline admin
```

4. Pull Skyline APIServer image từ Docker Hub

```sh
sudo docker pull 99cloud/skyline:latest
```

5. Tạo các folder dùng cho skyline-apiserver

```sh
sudo mkdir -p /etc/skyline /var/log/skyline /var/lib/skyline /var/log/nginx
```

6. Đặt tất cả giá trị trong đây: [Settings Reference](https://docs.openstack.org/skyline-apiserver/latest/configuration/settings.html#configuration-settings) vào file cấu hình ```/etc/skyline/skyline.yaml```

**Lưu ý là cấu hình các tham số sau cho đúng:**

```sh
default:
  database_url: mysql://skyline:<SKYLINE_DBPASS>@<DB_SERVER>:3306/skyline
  debug: true
  log_dir: /var/log/skyline
openstack:
  keystone_url: http://<KEYSTONE_SERVER>:5000/v3/
  system_user_password: <SKYLINE_SERVICE_PASSWORD>
```

7. Cuối cùng, chạy bootstrap server

```sh
sudo docker run -d --name skyline_bootstrap \
  -e KOLLA_BOOTSTRAP="" \
  -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml \
  -v /var/log:/var/log \
  --net=host 99cloud/skyline:latest
```

Cleanup bootstrap server

```sh
sudo docker rm -f skyline_bootstrap
```

Chạy skyline-apiserver

```sh
sudo docker run -d --name skyline --restart=always \
  -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml \
  -v /var/log:/var/log \
  --net=host 99cloud/skyline:latest
```