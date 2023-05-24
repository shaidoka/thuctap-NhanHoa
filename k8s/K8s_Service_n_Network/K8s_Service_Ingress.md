# Ingress

Ingress là 1 API object quản lý các truy cập từ bên ngoài đến các Services bên trong cluster, thường là qua giao thức http.

Ingress có thể cung cấp cân bằng tải (load balancing), kết nối SSL và virtual hosting dựa theo tên.

## Thuật ngữ

Dưới đây là một số thuật ngữ được sử dụng trong tài liệu này:
- **Node**: 1 máy worker trong K8s
- **Cluster**: 1 tập các node chạy các ứng dụng được quản lý bởi K8s
- **Edge router**: 1 Router áp đặt chính sách firewall cho cluster. Nó có thể là 1 gateway được quản lý bởi nhà cung cấp đám mây hoặc có thể là 1 phần cứng vật lý
- **Cluster network**: 1 tập các kết nối logic hoặc vật lý để hỗ trợ giao tiếp bên trong cluster theo mô hình network của K8s
- **Service**: dùng để xác định 1 tập các pod sử dụng label selector. Trừ khi được đề cập, nếu không các Services được giả định có VIP (Virtual IP) chỉ có thể route được bên trong cluster network

## Ingress là gì?

**Ingress** expose các route http và https từ bên ngoài cluster đến các service bên trong cluster. Việc route traffic được kiểm soát bởi các rule được định nghĩa trong tài nguyên Ingress.

![](./images/Service_7.png)

**Ingress nằm giữa Internet và Services**

Một Ingress có thể được cấu hình để làm cho các Services có thể truy cập được từ bên ngoài cluster thông qua URL, ngoài ra cũng có thể cân bằng tải traffic, hỗ trợ kết nối SSL/TLS và cung cấp virtual hosting dựa theo tên.

Một Ingress Controller chịu trách nhiệm thực hiện các chức năng của Ingress thường là với 1 bộ cân bằng tải, mặc dù nó cũng có thể cấu hình Edge Router hoặc cấu hình thêm các frontend để giúp quản lý traffic.

Một Ingress không expose tùy tiện các port hay protocol. Việc expose các Services ngoài HTTP và HTTPS ra internet thường sử dụng loại service ```Service.Type=NodePort``` hoặc ```Service.Type=LoadBalancer```.

## Prerequisites

Ta cần phải có 1 **Ingress Controller** để thực hiện các chức năng của Ingress. Việc chỉ tạo resource **Ingress** sẽ không có tác dụng gì.

Ta có thể triển khai Ingress Controller như [ingress-nginx](https://kubernetes.github.io/ingress-nginx/deploy/) hoặc ta có thể chọn các Ingress Controller khác.

Lý tưởng nhất, tất cả các Ingress Controller phải phù hợp với đặc tả tham chiếu. Trong thực tế các Ingress Controller khác nhau hoạt động khác nhau.

Cài đặt **ingress-nginx** bằng file YAML:

```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.1/deploy/static/provider/baremetal/deploy.yaml
```

## Ingress resource

1 ingress tối thiểu như sau:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
    paths:
    - path: /testpath
      pathType: Prefix
      backend:
        serviceName: test
        servicePort: 80
```

Ingress thường sử dụng annotation để cấu hình một số tùy chọn tùy thuộc ta sử dụng Ingress Controller nào, một ví dụ là rewrite-target annotation. Các ingress controller khác nhau hỗ trợ các annotation khác nhau

Đặc tả của Ingress có tất cả các thông tin cần thiết để cấu hình loadbalancer hoặc proxy server. Quan trọng nhất, nó chứa 1 danh sách các rule khớp với tất cả các incoming request. Tài nguyên Ingress chỉ hỗ trợ rule để điều hướng **HTTP** traffic.

### 1. Ingress rules

Mỗi HTTP rule chứa các thông tin sau:
- **1 host tùy chọn**: trong ví dụ trên, không có host (tên miền) nào được chỉ định nên rule sẽ được áp dụng vào tất cả HTTP traffic đi vào địa chỉ IP đã được chỉ định. Nếu có chỉ định host thì rule chỉ áp dụng với host đó thôi.
- **1 danh sách các đường dẫn (path)**: (ví dụ ```/testpath```), mỗi path có 1 backend gắn liền với nó được định nghĩa bởi ```serviceName``` và ```servicePort``. Cả host và path phải khớp với nội dung của incoming request trước khi bộ cân bằng tải điều hướng traffic đến Services mong muốn.
- **1 backend**: là 1 tổ hợp của tên Services và Port như đã mô tả trong tài liệu về Services. HTTP và HTTPS request đi đến Ingress và có URL khớp với host và path của rule sẽ được gửi đến danh sách các backend

Một backend mặc định thường được cấu hình trong Ingress Controller để phục vụ bát kỳ request nào không khớp với bất kỳ path nào trong đặc tả của Ingress.

### 2. Backend mặc định

Một Ingress không có rule nào sẽ gửi tất cả traffic đến 1 backend mặc định duy nhất. Backend mặc định thường là 1 cấu hình tùy chọn của Ingress Controller và không được chỉ định trong cấu hình của tài nguyên Ingress.

Nếu không có host và path nào khớp với HTTP request trong Ingress object thì traffic sẽ được route đến backend mặc định.

### 3. Path Type

Mỗi ```path``` trong đặc tả của Ingress có 1 ```pathType``` tương ứng. Có 3 ```pathType``` được hỗ trợ:
- ```ImplementationSpecific``` (mặc định): Với loại đường dẫn này, việc match sẽ tùy thuộc vào IngressClass. Các triển khai có thể xem đây là một ```pathType``` riêng biệt hoặc xử lý nó giống hệt với các loại đường dẫn ```Prefix``` hoặc ```Exact```
- ```Exact```: khớp với đường dẫn URL một cách chính xác tuyệt đối và phân biệt chữ hoa chữ thường
- ```Prefix```: khớp dựa trên tiền tố của đường dẫn URL được phân tách bởi dấu ```/```. Việc match là có case insesitive và được thực hiện từng thành phần của đường dẫn URL. Một thành phần của đường dẫn URL chính là 1 label được phân tách bằng dấu phân cách ```/``` trong đường dẫn URL (nghĩa là đường dẫn URL có thể bao gồm nhiều cấp phân tách nhau bởi dấu ```/```, mỗi chuỗi đứng giữa 2 dấu ```/``` chính là 1 label, mỗi label chính là 1 thành phần của đường dẫn URL). VD: ```/foo/bar``` match ```/foo/bar/baz``` và không match ```/foo/barbaz```

**Multiple Match**

Trong một số trường hợp, nhiều ```path``` bên trong Ingress sẽ khớp với đường dẫn của request URL. Trong những trường hợp đó, quyền ưu tiên sẽ được trao cho ```path``` khớp dài nhất đầu tiên. Nếu 2 ```path``` vẫn có độ dài khớp bằng nhau thì quyền ưu tiên sẽ được trao cho các đường dẫn có loại ```Exact``` thay vì ```Prefix```

## Ingress Class

Các Ingress có thể được cài đặt bởi các Controller khác nhau, thường với cấu hình khác nhau. Mỗi Ingress nên chỉ định một class, là một tham chiếu đến tài nguyên IngressClass có chứa cấu hình bổ sung bao gồm cả tên của Controller sẽ triển khai class.

```sh
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: external-lb
spec:
  controller: example.com/ingress-controller
  parameters:
    apiGroup: k8s.example.com/v1alpha
    kind: IngressParameters
    name: external-lb
```

Tài nguyên IngressClass chứa một trường ```parameters``` tùy chọn. Trường này có thể được sử dụng để tham chiếu đến cấu hình bổ sung cho class này.

### 1. Các annotation không còn được hỗ trợ

Trước khi tài nguyên IngressClass và trường ```ingressClassName``` được thêm vào trong K8s v1.18, các Ingress class được chỉ định với annotation ```k8s.io/ingress.class``` trong đặc tả của Ingress. Annotation này chưa bao giờ được định nghĩa chính thức, nhưng được hỗ trợ rộng rãi bởi các Ingress Controller.

Trường ```ingressClassName``` mới hơn trong đặc tả của Ingress là sự thay thế cho annotation đó, nhưng không phải là 1 sự tương đương trực tiếp. Mặc dù annotation thường được sử dụng để tham chiếu tên của Ingress Controller sẽ triển khai Ingress, trường ```ingressClassName``` này tham chiếu đến tài nguyên IngressClass có chứa cấu hình Ingress bổ sung, bao gồm tên của Ingress Controller.

### 2. Ingress Class mặc định

Ta có thể đánh dấu một IngressClass cụ thể làm mặc định cho cluster của mình. Thiết lập annotation ```ingressclass.kubernetes.io/is-default-class``` thành ```true``` trong tài nguyên IngressClass sẽ đảm bảo rằng các Ingress mới không có trường ```ingressClassName``` được chỉ định sẽ được gán IngressClass mặc định này.

**Lưu ý:** Để tránh mâu thuẫn, ta nên đảm bảo rằng chỉ có 1 IngressClass mặc định trong cluster.

## Ingress Type

### 1. Ingress đơn dịch vụ

Có các khái niệm trong K8s cho phép ta expose 1 Services duy nhất. Ta cũng có thể làm như vậy với Ingress bằng cách chỉ định backend mặc định và không có rule nào trong đặc tả của Ingress cả (không có **host** và **path** để match).

Ví dụ:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-nginx
            port:
              name: http
```

### 2. Simple fanout

Một cấu hình fanout sẽ route traffic từ 1 địa chỉ IP đến nhiều hơn 1 Services dựa trên HTTP URI được yêu cầu. Ingress cho phép ta giữ số lượng bộ cân bằng tải xuống mức tối thiểu. Ví dụ 1 thiết kế như sau:

```sh
foo.bar.com -> 178.91.123.132 -> /foo   service1:4200
                                 /bar   service2:8080
```

Sẽ yêu cầu Ingress như sau:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-fanout-example
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - path: /foo
        backend:
          serviceName: service1
          servicePort: 4200
      - path: /bar
        backend:
          serviceName: service2
          servicePort: 8080
```

Sau khi tạo Ingress trên với lệnh ```kubectl apply -f```, ta có thể xem chi tiết nó

```sh
kubectl describe ingress simple-fanout-example
```

Đầu ra có dạng

```sh
Name:             simple-fanout-example
Namespace:        default
Address:          178.91.123.132
Default backend:  default-http-backend:80 (10.8.2.3:8080)
Rules:
  Host         Path  Backends
  ----         ----  --------
  foo.bar.com
               /foo   service1:4200 (10.8.0.90:4200)
               /bar   service2:8080 (10.8.0.91:8080)
Annotations:
  nginx.ingress.kubernetes.io/rewrite-target:  /
Events:
  Type     Reason  Age                From                     Message
  ----     ------  ----               ----                     -------
  Normal   ADD     22s                loadbalancer-controller  default/test
```

Ingress Controller sẽ chuẩn bị (provision) 1 bộ cân bằng tải dành riêng cho việc phục vụ Ingress chừng nào Services (```service1``` và ```service2```) vẫn còn tồn tại. Khi Ingress Controller chuẩn bị xong, ta có thể thấy địa chỉ của bộ cân bằng tải trong trường ```Address```.

### 3. Virtual hosting theo tên

Virtual host dựa theo tên hỗ trợ route HTTP traffic đến nhiều hostname trên cùng 1 địa chỉ IP

Mô hình như sau:

```sh
foo.bar.com --|                 |-> foo.bar.com service1:80
              | 178.91.123.132  |
bar.foo.com --|                 |-> bar.foo.com service2:80
```

Đặc tả Ingress sau sẽ nói cho bộ cân bằng tải route các request dựa trên **host header**:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: name-virtual-host-ingress
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - backend:
          serviceName: service1
          servicePort: 80
  - host: bar.foo.com
    http:
      paths:
      - backend:
          serviceName: service2
          servicePort: 80
```

Nếu ta tạo tài nguyên Ingress mà không định nghĩa ```host``` trong phần ```rules``` thì bất kỳ web traffic nào đến địa chỉ IP của Ingress Controller đều có thể match mà không yêu cầu virtual host theo tên.

Ví dụ tài nguyên Ingress sau sẽ route traffic request cho ```ifrst.bar.com``` đến ```service1``` và ```second.foo.com``` đến ```service2```, ngoài ra, bất kỳ traffic nào đến IP mà không có hostname trong request header sẽ được route ```service3```:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: name-virtual-host-ingress
spec:
  rules:
  - host: first.bar.com
    http:
      paths:
      - backend:
          serviceName: service1
          servicePort: 80
  - host: second.foo.com
    http:
      paths:
      - backend:
          serviceName: service2
          servicePort: 80
  - http:
      paths:
      - backend:
          serviceName: service3 
          servicePort: 80
```

### 4. TLS

Ta có thể bảo mật Ingress bằng cách chỉ định 1 **Secret** có chứa TLS private key và certificate. Hiện tại Ingress chỉ hỗ trợ duy nhất TLS port 443 và là điểm kết thúc cho TLS. Nếu phần cấu hình TLS trong ingress chỉ định các host khác nhau,, chúng sẽ được ghép lại (multiplexed) trên cùng port tùy thuộc vào hostname được chỉ định thông qua phần mở rộng **SNI TLS** (với điều kiện Ingress Controller hỗ trợ SNI). TLS Secret phải chứa các trường với tên key là ```tls.crt``` và ```tls.key```, đây chính là certificate và private key để sử dụng cho TLS. Ví dụ:

```sh
apiVersion: v1
kind: Secret
metadata:
  name: testsecret-tls
  namespace: default
data:
  tls.crt: base64 encoded cert
  tls.key: base64 encoded key
type: kubernetes.io/tls
```

Việc tham chiếu Secret này trong đặc tả của Ingress sẽ nói cho Ingress Controller bảo mật kênh (channel) kết nối từ client đến bộ cân bằng tải sử dụng TLS. Ta cần phải đảm bảo TLS Secret đã tạo ra có chứa 1 Common Name (CN) còn được gọi là Tên miền đủ tiêu chuẩn (FQDN) cho ```sslexample.foo.com```:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-example-ingress
spec:
  tls:
  - hosts:
      - sslexample.foo.com
    secretName: testsecret-tls
  rules:
  - host: sslexample.foo.com
    http:
      paths:
      - path: /
        backend:
          serviceName: service1
          servicePort: 80
```

### 5. Cân bằng tải

Ingress Controller được khởi động với vài thiết lập về chính sách cân bằng tải sẽ được áp dụng cho tất cả Ingress, ví dụ như thuật toán cân bằng tải, mô hình trọng số của backend,... Các khái niệm cân bằng tải cao cấp hơn (như persistent sessions, dynamic weights) chưa được expose qua Ingress. Thay vào đó, ta có thể có các tính năng này thông qua bộ cân bằng tải sử dụng cho Services.

Cũng cần lưu ý rằng thậm chí việc kiểm tra health check cũng không được expose trực tiếp thông qua Ingress, vẫn có các khái niệm tồn tại song song trong K8s như **Readiness Probe** cho phép ta đạt được cùng 1 kết quả. Cần xem tài liệu của Ingress Controller cụ thể để biết cách chúng quản lý việc health check (nginx, GCE) như thế nào.

## Cập nhật Ingress

Để cập nhật 1 ingress hiện có và thêm vào host mới, ta có thể thực hiện bằng cách cập nhật tài nguyên như sau:

```sh
kubectl describe ingress test
```

```sh
Name:             test
Namespace:        default
Address:          178.91.123.132
Default backend:  default-http-backend:80 (10.8.2.3:8080)
Rules:
  Host         Path  Backends
  ----         ----  --------
  foo.bar.com
               /foo   service1:80 (10.8.0.90:80)
Annotations:
  nginx.ingress.kubernetes.io/rewrite-target:  /
Events:
  Type     Reason  Age                From                     Message
  ----     ------  ----               ----                     -------
  Normal   ADD     35s                loadbalancer-controller  default/test
```

```sh
kubectl edit ingress test
```

```sh
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - backend:
          serviceName: service1
          servicePort: 80
        path: /foo
  - host: bar.baz.com
    http:
      paths:
      - backend:
          serviceName: service2
          servicePort: 80
        path: /foo
```

```sh
Name:             test
Namespace:        default
Address:          178.91.123.132
Default backend:  default-http-backend:80 (10.8.2.3:8080)
Rules:
  Host         Path  Backends
  ----         ----  --------
  foo.bar.com
               /foo   service1:80 (10.8.0.90:80)
  bar.baz.com
               /foo   service2:80 (10.8.0.91:80)
Annotations:
  nginx.ingress.kubernetes.io/rewrite-target:  /
Events:
  Type     Reason  Age                From                     Message
  ----     ------  ----               ----                     -------
  Normal   ADD     45s                loadbalancer-controller  default/test
```

Ta cũng có thể đạt được cùng kết quả bằng lệnh ```kubectl replace -f``` nếu ta điều chỉnh file yaml mà muốn áp dụng nó.