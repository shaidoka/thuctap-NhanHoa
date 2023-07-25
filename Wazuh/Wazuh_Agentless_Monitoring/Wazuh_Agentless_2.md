# Tạo kết nối

Wazuh cung cấp 1 script tên ```register_host.sh``` để kết nối agentless endpoint với Wazuh server sử dụng xác thực SSH. Script này đặt tại ```/var/ossec/agentless/``` ở Wazuh server. Ta có thể thêm endpoint và danh sách các endpoint được liên kết với tùy chọn ```add``` và ```list```

## Thêm 1 endpoint

Tùy chọn ```add``` của ```register_host.sh``` script thêm 1 agentless endpoint vào Wazuh server. Chỉ định tùy chọn ```NOPASS``` để sử dụng public key authentication thay vì sử dụng password.

### Endpoint với public key authentication

Để thêm agentless endpoint sử dụng public key authentication, thực hiện các bước sau ở trên Wazuh server:

1. Tạo public key

```sh
sudo -u wazuh ssh-keygen
```

2. Chạy lệnh sau để copy public key đến endpoint được giám sát:

```sh
ssh-copy-id -i /var/ossec/.ssh/id_rsa.pub root@103.159.51.184
```

3. Thêm endpoinnt bằng cách chạy lệnh sau trên Wazuh server

```sh
/var/ossec/agentless/register_host.sh add root@103.159.51.184 NOPASS
```

Đầu ra có dạng:

```sh
*Host root@103.159.51.184 added.
```

**Đối với các endpoint không sử dụng ssh port 22**

1. Tạo public key...

2. Copy public key sang endpoint...

3. Thêm file sau

```sh
cat << EOF > /var/ossec/.ssh/config
host 12334
user root
port 226
hostname 103.170.123.34
EOF
```

4. Đảm bảo wazuh có thể đọc được file

```sh
chown wazuh:wazuh /var/ossec/.ssh -R
```

5. Add host

```sh
/var/ossec/agentless/register_host.sh add 12334 example_password
```

### Endpoint với password authentication

Chạy lệnh sau để thêm agentless endpoint đến Wazuh server sử dụng password authentication:

```sh
/var/ossec/agentless/register_host.sh add root@103.159.51.184 test_password
```

Đầu ra có dạng

```sh
*Host root@103.159.51.184 added.
```

### Cisco PIX

Với các thiết bị Cisco, như router hay firewall, sử dụng ```enablepass``` để chỉ định kích hoạt password

Thêm Cisco device sử dụng lệnh thiết lập như ví dụ dưới đây:

```sh
/var/ossec/agentless/register_host.sh add pix@example_address.com example_password enablepass
```

Đầu ra có dạng

```sh
*Host pix@example_address.com added.
```

### Liệt kê danh sách endpoint được liên kết

Tùy chọn ```list``` của script ```register_host.sh``` cho phép hiển thị tất cả agentless endpoints kết nối đến Wazuh server. Sử dụng lệnh sau đây để hiển thị các endpoint được kết nối:

```sh
/var/ossec/agentless/register_host.sh list
```

Đầu ra có dạng

```sh
*Available hosts:
user@example_address.com
pix@example_address.com
```

### Xóa agentless endpoint

Các credential của agentless endpoint đặt tại ```/var/ossec/agentless/.passlist``` trên Wazuh server. File này phải được xóa để loại bỏ cấu hình agentless, hiện tại **không có cách nào để loại bỏ 1 endpoint độc lập**

Thực hiện các bước sau đây trên Wazuh server để loại bỏ cấu hình agentless và password:

1. Xóa agentless monitoring setting trong tệp ```/var/ossec/etc/ossec.conf```

2. Xóa tệp ```/var/ossec/agentless/.passlist```

3. Restart wazuh manager

```sh
systemctl restart wazuh-manager
```