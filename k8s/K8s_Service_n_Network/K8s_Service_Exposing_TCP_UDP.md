# Exposing TCP and UDP services

Trong khi K8s ingress chỉ chính thức hỗ trợ định tuyến HTTP traffic đến service, ingress-nginx thậm chí có thể thiết lập để tiếp nhận TCP/UDP traffic từ những giao thức non-HTTP và định tuyến chúng đến internal service sử dụng ánh xạ TCP/UDP port mà được chỉ định trong 1 ConfigMap

Để hỗ trợ điều này, có 2 cờ là ```--tcp-services-configmap``` và ```--udp-services-configmap``` có thể được sử dụng để chỉ định 1 configmap khả dụng, nơi mà key là external port để sử dụng và value chỉ định service để expose với định dạng như sau: ```<namespace/service name>:<service port>:[PROXY]:[PROXY]```

Ta có thể sử dụng số hoặc tên port đều được. 2 trường cuối là optional. Thêm ```PROXY``` vào 1 trong 2 hoặc cả 2 trường cuối cùng chúng ta có thể sử dụng Proxy Protocol giải mã (lắng nghe) và/hoặc mã hóa (proxy_pass) trong 1 TCP service. Trường ```PROXY``` đầu tiên điều khiển giải mã của proxy protocol và trường thứ 2 thì điều khiển quá trình giải mã sử dụng proxy protocol. Điều này cho phép 1 incoming connection có thể được giải mã hoặc 1 outgoing connection có thể được mã hóa. Nó cũng cho phép xử lý giữa 2 proxy khác nhau bằng cách bật mã hóa và giải mã trên 1 TCP service

Ví dụ dưới đây sẽ biểu diễn cách để expose service ```example-go``` chạy ở namespace ```default``` trong port ```8080``` sử dụng port ```9000```:

```sh
apiVersion: v1
kind: ConfigMap
metadata:
  name: tcp-services
  namespace: ingress-nginx
data:
  9000: "default/example-go:8080"
```

Từ phiên bản 1.9.13 thì NGINX cung cấp UDP load balancing. Ví dụ sau đây thể hiện cách expose service ```kube-dns``` chạy ở namespace ```kube-system``` trong port ```53``` sử dụng port ```53```

```sh
apiVersion: v1
kind: ConfigMap
metadata:
  name: udp-services
  namespace: ingress-nginx
data:
  53: "kube-system/kube-dns:53"
```

Nếu TCP/UDP proxy support được sử dụng, vậy thì những port này cần được expose ở Service được định nghĩa cho Ingress

```sh
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  type: LoadBalancer
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
  - name: https
    porrt: 443
    targetPort: 443
    protocol: TCP
  - name: proxied-tcp-9000
    porrt: 9000
    targetPort: 9000
    protocol: TCP
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
```

Lưu ý rằng ConfigMap cần phải được thêm vào ingress controller của deployment args thì mới có tác dụng:

```sh
 args:
    - /nginx-ingress-controller
    - --tcp-services-configmap=ingress-nginx/tcp-services
```

