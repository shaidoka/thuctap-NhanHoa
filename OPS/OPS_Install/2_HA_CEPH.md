# Cài đặt node CEPH AIO (Luminous)

## Phần 1 - Chuẩn bị

**Phân hoạch IP:**
- Đường Management: eth0 - 172.16.10.19 - Sử dụng để truy cập vào quản trị, cài đặt
- Đường CephCOM: eth2 - 172.16.12.19 - Sử dụng để client kết nối đến, tương ứng đường storage trong OPS cluster
- Đường CephREP: eth1 - 172.16.11.19 - Sử dụng để cụm CEPH đồng bộ dữ liệu với nhau

**Setup node:**

```sh

```