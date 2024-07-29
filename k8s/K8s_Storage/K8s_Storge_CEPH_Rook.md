# How to setup a CEPH cluster under K8s using Rook

[Rook](https://rook.io/) là 1 công cụ điều phối storage mà cung cấp 1 giải pháp cloudnative, mã nguồn mở cho nhiều loại storage provider khác nhau. Rook sử dụng sức mạnh của K8s để biến 1 storage system thành những self-mananging service mà cung cấp 1 trải nghiệm thông suốt và tiết kiệm cho K8s và triển khai.

Ceph là 1 giải pháp distributed storage có tính mở rộng rất cao, nó hỗ trợ object, block, và file storage. Ceph clusters được thiết kế để chạy trên bất kỳ phần cứng nào sử dụng thuật toán CRUSH (Controlled Replication Under Scalable Hashing)

Một lợi ích chính của triển khai này là bạn sẽ có 1 giải pháp storage có tính mở rộng cao của Ceph mà không phải cấu hình nó thủ công sử dụng Ceph command line, Rook sẽ lo phần đó cho bạn.
K8s applications có thể sau đó mount block devices và filesystems từ Rook cho PV/PVC.

Trong hướng dẫn này, bạn sẽ thiết lập 1 cụm Ceph sử dụng Rook và sử dụng nó để lưu trữ dữ liệu cho 1 MongoDB database.

### Prerequisites

- Bài viết này sẽ giả định là bạn đã có sẵn 1 cụm Kubernetes, với mỗi node có ít nhất 2 vCPUS, 4GB RAM
- Công cụ commandline để tương tác với k8s là **kubectl** đã được cài đặt
- Mỗi node cũng cần có thêm 1 ổ cứng 100GB để sử dụng cho CEPH

## Bước 1: Thiết lập Rook

Sau khi hoàn thành các bước bên trên, bạn đã sẵn sàng để thiết lập Rook.

Trong phần này, bạn sẽ clone Rook repository và deploy Rook operator trên K8s cluster. 1 Rook operator là 1 container mà tự động bootstraps storage cluster và giám sát storage daemons để đảm bảo cụm storage hoạt động ổn định.

Trước khi bắt đầu deploy Rook, đầu tiên bạn cần LVM package trên tất cả nodes của bạn vì nó được yêu cầu bởi Ceph.

```sh
apt-get update -y && apt-get install lvm2 -y
```

Giờ, hãy clone Rook repository:

```sh
git clone --single-branch --branch release-1.3 https://github.com/rook/rook.git
```

Lệnh này sẽ clone Rook repository từ GitHub và tạo 1 folder tên ```rook```. Hãy đi đến thư mục ceph với lệnh sau:

```sh
cd rook/cluster/examples/kubernetes/ceph
```