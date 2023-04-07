# Access Cluster

Bài viết này sẽ giới thiệu một số cách để tương tác với cluster

## Truy cập lần đầu với kubectl

Khi truy cập K8s API lần đầu, ta nên sử dụng K8s CLI là ```kubectl```

Để truy cập vào cluster, ta cần phải biết vị trí của cluster và có credentials để truy cập nó. Thông thường, điều này được thiết lập tự động.

Kiểm tra vị trí và credential mà kubectl biết về với lệnh sau

```sh
kubectl config view
```

## Truy cập trực tiếp qua REST API

Kubectl xử lý định vị và xác thực đến apiserver. Nếu ta muốn trực tiếp truy cập REST API với 1 http client như curl hay wget, hoặc 1 browser, có 1 vài cách để làm điều này:
- Chạy kubectl trong chế độ proxy:
  - Đây là cách được khuyến nghị
  - Sử dụng kho lưu trữ vị trí apiserver
  - Xác định danh tính của apiserver sử dụng self-signed cert. Như vậy sẽ tránh đc man-in-the-middle
  - Xác thực đến apiserver
  - Trong tương lai, có thể cải tiến cân bằng tải và tính chịu lỗi ở phía client
- Cung cấp vị trí và credentials trực tiếp đến http client
  - Không khuyến nghị
  - Hoạt động với 1 vài dạng client mà code không sử dụng được proxy
  - Cần phải import 1 root cert vào browser để bảo vệ khỏi MITM

### 1. Sử dụng kubectl proxy

Những lệnh sau chạy kubectl trong chế độ hoạt động như 1 reverse proxy. Nó xử lý định vị apiserver và xác thực.

```sh
kubectl proxy --port=8080
```

Chi tiết có thể xem tại đây: [kubectl proxy](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands/#proxy)

Sau đó ta có thể kiểm thử API với curl, wget hoặc 1 browser (thay phần ```localhost``` thành ```[::1]``` cho IPv6)

```sh
curl http://localhost:8080/api/
```

Đầu ra có dạng như sau:

```sh
{
  "kind": "APIVersions",
  "versions": [
    "v1"
  ],
  "serverAddressByClientCIDRs": [
    {
      "clientCIDR": "0.0.0.0/0",
      "serverAddress": "10.0.1.149:443"
    }
  ]
}
```

### 2. Không sử dụng kubectl proxy

Sử dụng ```kubectl apply``` và ```kubectl describe secret...``` để tạo 1 token cho service account mặc định với grep/cut:

Đầu tiên, tạo 1 Secret, request 1 token cho ServiceAccount mặc định

```sh
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata
  name: default-token
  annotations:
    kubernetes.io/service-account.name: default
type: kubernetes.io/service-account-token
EOF
```

Tiếp đến, chờ token controller để thực thi Secret với 1 token

```sh
while ! kubectl describe secret default-token | grep -E '^token' >/dev/null; do
  echo "waiting for token..." >&2
  sleep 1
done
```

Lấy và sử dụng token vừa được khởi tạo

```sh
APISERVER=$(kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " ")
TOKEN=$(kubectl describe secret default-token | grep -E '^token' | cut -f2 -d':' | tr -d " ")

curl $APISERVER/api --header "Authorization: Bearer $TOKEN" --insecure
```

Đầu ra sẽ có dạng:

```sh
{
  "kind": "APIVersions",
  "versions": [
    "v1"
  ],
  "serverAddressByClientCIDRs": [
    {
      "clientCIDR": "0.0.0.0/0",
      "serverAddress": "10.0.1.149:443"
    }
  ]
}
```

Ví dụ trên sử dụng cờ ```--insecure```. Điều này để lại lỗi hổng cho tấn công MITM. Khi kubectl truy cập cluster nó sử dụng 1 root certificate và client certificate được lưu trữ để truy cập máy chủ (đường dẫn tại ```~/.kube```). Trong khi cluster certificate thường là self-signed, nó có thể cần cấu hình đặc biệt để http client có thể sử dụng root certificate.

## Lập trình truy cập đến API

K8s hỗ trợ Golang và Python client libraries.

Chi tiết được đề cập tại [Programmatic access to the API](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/#programmatic-access-to-the-api)

## Truy cập API từ 1 Pod

Khi truy cập API từ pod, định vị và xác thực đến API server sẽ có đôi chút khác biệt.

Chi tiết được đề cập ở đây: [Accessing the API from within a Pod](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/)

## Truy cập service chạy trên cluster

Những phần bên trên mô tả các cách để kết nối đến K8s API server. Đối với việc kết nối đến các dịch vụ chạy trên 1 K8s cluster, xem [Access Cluster Services](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster-services/)

## Truy cập vào Cluster bằng Container

Để truy cập vào một cluster trong K8s bằng container thì trong container đó phải có các công cụ như kubectl hoặc API K8s. Sau khi container được triển khai trong cluster, ta có thể sử dụng các công cụ này để tương tác với cluster và triển khai một container chứa công cụ kubectl, ta có thể sử dụng image bitnami/kubectl và chạy lệnh sau để triển khai container:

```sh
kubectl run kubectl-container --image=bitnami/kubectl --restart=Never --command -- sleep infinity
```

Lệnh trên sẽ triển khai một container mới với tên "kubectl-container" sử dụng image bitnami/kubectl, và chạy lệnh ```sleep infinity``` để container không bao giờ dừng lại. Sau đó, bạn có thể sử dụng lệnh ```kubectl exec``` để truy cập vào container và sử dụng công cụ kubectl để tương tác với cluster. VD:

```sh
kubectl exec -it kubectl-container -- sh
```

Lệnh trên sẽ mở một phiên bản shell trong container và cho phép sử dụng công cụ kubectl để tương tác với cluster.

Tuy nhiên cách thức truy cập này có vẻ không được an toàn.