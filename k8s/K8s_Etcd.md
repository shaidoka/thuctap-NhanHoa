# Etcdctl và cách backup restore etcd trên K8s

Trong bài này sẽ giới thiệu cách backup hệ thống cơ sở dữ liệu của cụm k8s bằng snapshot etcd, giúp dễ dàng khôi phục khi hệ thống gặp sự cố.

# Etcd

Etcd là một dạng CSDL dạng key-value được dùng để lưu trữ dữ liệu hệ thống, tài nguyên và cấu hình k8s cluster. Khi ta tạo mới ứng dụng bao gồm những deployment, pod, service,... thì những thông tin định nghĩa này sẽ được lưu vào etcd

Etcd được chạy dưới dạng cluster và số lượng lớn member trong cluster là lẻ. Theo tài liệu của etcd thì recommend cho production là nên cài 5 node etcd để đảm bảo tính sẵn sàng.

Để thao tác với etcd thì ta nên sử dụng **etcdctl**, nó tương tự như công cụ dòng lệnh kubectl để giao tiếp với k8s. Để sử dụng etcdctl thì ta cần cài đặt và cấu hình certificate cho nó có thể giao tiếp được với etcd cluster.

Cú pháp sử dụng etcdctl như sau:

```sh
ETCDCTL_API=3 etcdctl <etcd-command> \
--endpoints=https://127.0.0.1:2379 \
--cacert=<trusted-ca-file> \
--cert=<cert-file> \
--key=<key-file>
```

## Cài đặt và sử dụng etcdctl

### Cài đặt etcdctl

Cài đặt các gói phụ trợ

```sh
apt -y install wget curl jq
```

Download gói cài đặt của etcd trên centos:

```sh
curl -s https://api.github.com/repos/etcd-io/etcd/releases/latest \
  | grep browser_download_url \
  | grep linux-amd64 \
  | cut -d '"' -f 4 \
  | wget -i -
```

Copy các file binary vào thư mục chứa file thực thi của hệ điều hành:

```sh
tar -xzvf etcd-v*.tar.gz
cd etcd-*/
sudo cp etcd* /usr/local/bin/
sudo cp etcd* /usr/bin/
cd ..
rm -rf etcd*
```

Kiểm tra

```sh
etcdctl version
```

![](./images/K8s_Etcd_1.png)

### Cấu hình etcdctl

Để kết nối tới etcd cluster ta cần các thông tin như: IP/Port của etcd endpoints, các file cert sử dụng để kết nối

Để lấy các thông tin này, ta có thể lấy từ mô tả của pod **kube-api-server**, vì nó là thành phần duy nhất kết nối trực tiếp với etcd trong K8s cluster

Thực hiện lệnh sau để lấy các tham số command của kube-api-server (lưu ý tên pod đúng trong cluster)

```sh
kubectl -n kube-system get pod kube-apiserver-k8s-master1 -o=jsonpath='{.spec.containers[0].command}' | jq '.' | grep etcd
```

Kết quả trả về có dạng:

```sh
  "--etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt",
  "--etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt",
  "--etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key",
  "--etcd-servers=https://127.0.0.1:2379",
```

*Note: Ở đây đường dẫn etcd cert và key file phải là /etc/kubernetes/pki/etcd/server.crt chứ không phải như trên kia*

Như vậy ta đã có thông tin về endpoint và đường dẫn tới các file cert trên node master1. Nhưng các file này có owner là root, do đó user mà ta đang dùng không phải root thì sẽ không đọc được. Ta chỉ cần đơn giản copy nó sang 1 đường dẫn khác và chown thành user mà bản thân sử dụng

Giờ ta có thể sử dụng lệnh etcd bằng cú pháp như sau:

```sh
ETCDCTL_API=3 etcdctl [some-command] \
--endpoints=https://127.0.0.1:2379 \
--cacert=/home/ubuntu/yaml-files/etcd/credentials/ca.crt \
--cert=/home/ubuntu/yaml-files/etcd/credentials/server.crt \
--key=/home/ubuntu/yaml-files/etcd/credentials/server.key
```

Nhưng làm như sau thì sẽ ngắn gọn hơn nhiều

```sh
export ETCDCTL_CACERT=/home/ubuntu/yaml-files/etcd/credentials/ca.crt
export ETCDCTL_CERT=/home/ubuntu/yaml-files/etcd/credentials/server.crt
export ETCDCTL_KEY=/home/ubuntu/yaml-files/etcd/credentials/server.key
export ETCDCTL_API=3
etcdctl [some-command]
```

Trước hết, ta kiểm tra danh sách node trong etcd cluster bằng lệnh "member list" như sau:

```sh
etcdctl member list
````

