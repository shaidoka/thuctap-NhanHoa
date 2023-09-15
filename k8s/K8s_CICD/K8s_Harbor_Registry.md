# Harbor Registry

Trong bài viết này chúng ta sẽ cùng tìm hiểu cách dựng Docker Registry sử dụng Private Docker Registry và Harbor Registry trên Ubuntu 20.04. Tùy theo nhu cầu mà chọn cái nào phù hợp để sử dụng.

## Giới thiệu

Thông thường khi client được cài đặt Docker, ta có thể pull image bằng câu lệnh

```sh
docker pull <image-name>:version
```

Khi đó docker client sẽ thực hiện kết nối tới Docker Hub mặc định để tìm kiếm và pull docker image đó về máy client. Docker Hub là dịch vụ của Docker cho việc tìm kiếm và chia sẻ các Docker Image dành cho mọi người. Tuy nhiên khi triển khai một dự án và yêu cầu không được public image, hoặc do điều kiện mà client không có kết nối Internet. Lúc đó ta sẽ cần phải xây dựng 1 Docker Registry riêng. Private Docker Registry giúp chúng ta quản lý các Docker Image và chia sẻ với mọi người trong team. Nó cũng giúp việc chia sẻ/tải về các Docker image chỉ dùng kết nối nội bộ mà không yêu cầu phải có Internet.

Việc này cũng giúp giảm thời gian triển khai do băng thông của mạng nội bộ lớn hơn rất nhiều băng thông Internet. Cũng như việc các công ty sẽ không lưu image lên các nền tảng public mà sẽ phải có hệ thống quản lý riêng.

## Cài đặt Harbor Registry

### Tạo thư mục cài đặt và chứa dữ liệu

Thư mục cài đặt được tạo ở ```/home/sysadmin/open-sources/harbor_registry``` và data directory tại ```/data/harbor_data```

```sh
mkdir -p /data/harbor_data
mkdir -p /home/sysadmin/open-sources/harbor_registry
cd /home/sysadmin/open-sources/harbor_registry
curl -s https://api.github.com/repos/goharbor/harbor/releases/latest | grep browser_download_url | cut -d '"' -f 4 | grep '\.tgz$' | wget -i -
tar xvzf harbor-offline-installer*.tgz
cd harbor
cp harbor.yml.tmpl harbor.yml
```

### Tạo self-signed SSL

#### Tạo CA

Tạo private key cho CA:

```sh
openssl genrsa -des3 -out rootCA.key 2048
```

Tạo file pem từ private key:

```sh
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1825 -out rootCA.pem
```

#### Tạo SSL cho ứng dụng web

Tạo 1 file ```openssl.cnf``` để cấu hình thêm thông tin SAN như sau:

```sh
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
[req_distinguished_name]
countryName = VN
countryName_default = VN
stateOrProvinceName = HN
stateOrProvinceName_default = HN
localityName = HN
localityName_default = HN
organizationalUnitName = NhanHoa
organizationalUnitName_default = IT
commonName = *.baotrung.xyz
commonName_max = 64
[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = *.monitor.baotrung.xyz
DNS.2 = *.prod.baotrung.xyz
DNS.3 = *.demo.baotrung.xyz
```

Tạo file key:

```sh
sudo openssl genrsa -out app.key 2048
```

Tạo CSR từ file key và config trên:

```sh
sudo openssl req -new -out app.csr -key app.key -config openssl.cnf
```

Giờ đóng dấu cho file CSR vừa tạo:

```sh
sudo openssl x509 -req -days 3650 -in app.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out app.crt -extensions v3_req -extfile openssl.cnf
```

### Cấu hình và cài đặt harbor.yaml

Vào lại thư mục chứa file cấu hình của Harbor và chỉnh sửa

```sh
cd /home/sysadmin/open-sources/harbor_registry
cd harbor 
vi harbor.yml
```

Các tham số cần sửa đổi bao gồm:

```sh
hostname: harbor.baotrung.xyz
certificate: /root/SSL/app.crt
private_key: /root/SSL/app.key
harbor_admin_password: Harbor_123
database:
  password: root_123
data_volume: /data/harbor_data
```

Sau khi cấu hình xong xuôi thì thực hiện cài đặt bằng script có sẵn:

```sh
cd /home/sysadmin/open-sources/harbor_registry/harbor
./install.sh
```

Sau khi chạy thì kiểm tra kết quả bằng lệnh

```sh
docker-compose ps
```