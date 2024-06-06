# Getting started with octavia-ingress-controller for Kubernetes

Bài này sẽ giải thích cách để triển khai và cấu hình octavia-ingress-controller trong K8s cluster trên nền tảng OpenStack cloud.

## What is an Ingress Controller?

Trong K8s, Ingress cho phép các người dùng bên ngoài và ứng dụng client truy nhập đến HTTP services. Ingress bao gồm 2 thành phần:

- ```Ingress resource```: là 1 tập các luật để traffic đi vào có thể được đưa tới Service chính xác.
- ```Ingress controller```: thứ mà hoạt động theo các rules đã được đặt bởi Ingress Resource, thường là thông qua HTTP hoặc L7 loadbalancer

Chi tiết hơn về Ingress tại: [Ingress](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Service_n_Network/K8s_Service_Ingress.md)

## Why octavia-ingress-controller?

Sau khi tạo 1 K8s cluster, cách thức thông thường nhất để expose ứng dụng ra ngoài cluster là sử dụng LoadBalancer service type. Trong OpenStack cloud, Octavia (hay LBaaS v2) là triển khai mặc định của dịch vụ LoadBalancer, do đó, mỗi khi có 1 LB service type được tạo, sẽ có 1 bộ cân bằng tải được tạo ra ở tài khoản của cloud tenant. Có 1 vài vấn đề cho việc này:

- Chi phí cho K8s Service cao hơn 1 chút nếu tạo Service loại LB và Octavia LB theo tỉ lệ 1:1 như vậy, người dùng sẽ phải trả phí cho mỗi bộ cân bằng tải mà họ tạo ra cho mỗi service, rất tốn kém
- Không có bộ lọc, định tuyến,... cho service. Điều này có nghĩa là bạn có thể gửi hầu hết các loại traffic đến nó, như HTTP, TCP, UDP, Websockets, gRPC, hoặc bất kể gì đi chăng nữa
- Các ingress controller truyền thống (như NGINX ingress controller, HAProxy, Traefik,...) không hợp lý khi đặt trong môi trường cloud vì chúng vẫn phụ thuộc vào dịch vụ cân bằng tải của cloud để expose chúng đằng sau 1 Service loại LoadBalancer, đấy là còn chưa nói đến các phát sinh khi phải quản lý thêm nhiều phần mềm khác

Và đó, octavia-ingress-controller có thể giải quyết tất cả vấn đề trên trong OpenStack environment bằng cách tạo 1 bộ cân bằng tải cho nhiều ```NodePort``` type service trong 1 ingress. Để sử dụng octavia-ingress-controller trong K8s cluster, hãy đặt annotation ```kubernetes.io/ingress.class``` trong phần ```metadata``` của Ingress resource như dưới đây:

```sh
annotations:
  kubernetes.io/ingress.class: "openstack"
```

## Requirements

```octavia-ingress-controller``` triển khi dựa trên OpenStack Octavia, vì vậy:

- Giao tiếp giữa octavia-ingress-controller và Octavia là cần thiết
- Octavia bản stable hoặc queens trở lên
- OpenStack Key Manager (Barbican) cần thiết cho TLS Ingress, nếu không thì Ingress sẽ tạo lỗi

## Deploy octavia-ingress-controller in the Kubernetes cluster

Trong hướng dẫn này, chúng ta sẽ deploy ```octavia-ingress-controller``` như 1 StatefulSet (với 1 pod) trong kube-system namespace trong cluster. Còn nếu không thì ta có thể triển khai controller như 1 static pod bằng việc cung cấp 1 manifest file trong ```/etc/kubernetes/manifests``` folder trong 1 cụm K8s mà được cài bằng ```kubeadm```. Tất cả manifest file trong hướng dẫn này đều được lưu ở ```/etc/kubernetes/octavia-ingress-controller``` folder, vì vậy tạo folder này trước với:

```sh
mkdir -p /etc/kubernetes/octavia-ingress-controller
```

### Create service account and grant permissions

Với mục đích kiểm thử, chúng ta cần cấp quyền cluster admin cho serviceacount đã tạo

```sh
cat <<EOF > /etc/kubernetes/octavia-ingress-controller/serviceaccount.yaml
---
kind: ServiceAccount
apiVersion: v1
metadata:
  name: octavia-ingress-controller
  namespace: kube-system
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: octavia-ingress-controller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: octavia-ingress-controller
    namespace: kube-system
EOF
kubectl apply -f /etc/kubernetes/octavia-ingress-controller/serviceaccount.yaml
```

## Prepare octavia-ingress-controller configuration

Octavia-ingress-controller cần phải giao tiếp được với OpenStack cloud để tạo resources liên quan đến K8s ingress resource, vì vậy credentials của 1 OpenStack user (không cần thiết phải là admin user) cần phải được cung cấp trong ```openstack``` section. Thêm vào đó, để phân biệt các ingress giữa các k8s cluster, ```cluster-name``` cần phải là độc nhất

```sh
cat <<EOF > /etc/kubernetes/octavia-ingress-controller/config.yaml
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: octavia-ingress-controller-config
  namespace: kube-system
data:
  config: |
    cluster-name: ${cluster_name}
    openstack:
      auth-url: ${auth_url}
      domain-name: ${domain-name}
      username: ${user_name}
      # user-id: ${user_id}
      password: ${password}
      project-id: ${project_id}
      region: ${region}
    octavia:
      subnet-id: ${subnet_id}
      floating-network-id: ${public_net_id}
EOF
kubectl apply -f /etc/kubernetes/octavia-ingress-controller/config.yaml
```

Dưới đây là 1 vài config tùy chọn khác:

- Tùy chọn cho kết nối đến k8s cluster. Cấu hình bên trên sẽ tận dụng service account credential mà sẽ được thêm vào trong pod tự động. Tuy nhiên, có vài lý do để ta chỉ định cấu hình này riêng biệt:

```sh
kubernetes:
  api-host: https://127.0.0.1:6443
  kubeconfig: /home/ubuntu/.kube/config
```

- Các tùy chọn cho security group management. Octavia-ingress-controller tạo 1 bộ cân bằng tải Octavia mỗi Ingress và thêm worker nodes làm members của loadbalancer. Để Octavia amphorae giao tiếp được tới Service NodePort, người quản trị k8s cluster sẽ phải quản lý thủ công security group cho worker nodes hoặc để cho octavia-ingress-controller tự lo điều này với cấu hình sau:

```sh
octavia:
  manage-security-groups: true
```

Lưu ý cho security group:

-
   - Tên của security group sẽ phải theo dạng: ```kube-ingress_<cluster-name>_<ingress-namespace>_<ingress-name>```
   - Mô tả của security group phải có dạng: ```Security group created for Ingress <ingress-namespace>/<ingress-name> from cluster <cluster-name>```
   - Security group có các thẻ: ```["octavia.ingress.kubernetes.io", "<ingress-namespace>_<ingress-name>"]```
   - Security group được tổ chức với tất cả Neutron ports của Kubernetes worker nodes

- Các tùy chọn để chọn với 1 flavor id. Octavia-ingress-controller sẽ sử dụng flavor đó để tạo Octavia loadbalancer. Nếu không được chỉ định, flavor mặc định sẽ được dùng

```sh
octavia:
  flavor-id: a07528cf-4a99-4f8a-94de-691e0b3e2076
```

- Tùy chọn để thiết lập Octavia provider sẽ sử dụng. Nếu không thiết lập, ```octavia-ingress-controller``` sẽ tạo các bộ cân bằng tải với provider mặc định theo cấu hình của OpenStack cloud đó. Ta có thể sử dụng ```openstack loadbalancer provider list``` để kiểm tra các Octavia provider khả dụng. 

```sh
octavia:
  provider: amphora
```

- Tùy chọn để chỉ định Octavia provider không hỗ trợ tạo fully-populated loadbalancers sử dụng 1 API call. Thiết lập tùy chọn này thành true sẽ tạo các bộ cân bằng tải sử dụng serial API calls mà đầu tiên tạo 1 unpopulated loadbalancer, sau đó mới đến listeners, pools, và members của nó. Đây là 1 tùy chọn thích hợp khi gặp sự quá tải của OpenStack API

```sh
octavia:
  provider-requires-serial-api-calls: true
```

## Deploy octavia-ingress-controller

```sh
image="registry.k8s.io/provider-os/octavia-ingress-controller:v1.30.0"

cat <<EOF > /etc/kubernetes/octavia-ingress-controller/deployment.yaml
---
kind: StatefulSet
apiVersion: apps/v1
metadata:
  name: octavia-ingress-controller
  namespace: kube-system
  labels:
    k8s-app: octavia-ingress-controller
spec:
  replicas: 1
  selector:
    matchLabels:
      k8s-app: octavia-ingress-controller
  serviceName: octavia-ingress-controller
  template:
    metadata:
      labels:
        k8s-app: octavia-ingress-controller
    spec:
      serviceAccountName: octavia-ingress-controller
      tolerations:
        - effect: NoSchedule # Make sure the pod can be scheduled on master kubelet.
          operator: Exists
        - key: CriticalAddonsOnly # Mark the pod as a critical add-on for rescheduling.
          operator: Exists
        - effect: NoExecute
          operator: Exists
      containers:
        - name: octavia-ingress-controller
          image: ${image}
          imagePullPolicy: IfNotPresent
          args:
            - /bin/octavia-ingress-controller
            - --config=/etc/config/octavia-ingress-controller-config.yaml
          volumeMounts:
            - mountPath: /etc/kubernetes
              name: kubernetes-config
              readOnly: true
            - name: ingress-config
              mountPath: /etc/config
      hostNetwork: true
      volumes:
        - name: kubernetes-config
          hostPath:
            path: /etc/kubernetes
            type: Directory
        - name: ingress-config
          configMap:
            name: octavia-ingress-controller-config
            items:
              - key: config
                path: octavia-ingress-controller-config.yaml
EOF
kubectl apply -f /etc/kubernetes/octavia-ingress-controller/deployment.yaml
```

## Setting up HTTP Load Balancing with Ingress

### Create a backend service

Tạo 1 web service đơn giản mà lắng nghe trên port HTTP 8080:

```sh
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webserver
  namespace: default
  labels:
    app: webserver
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webserver
  template:
    metadata:
      labels:
        app: webserver
    spec:
      containers:
      - name: webserver
        image: lingxiankong/alpine-test
        imagePullPolicy: IfNotPresent
        ports:
          - containerPort: 8080
EOF
kubectl expose deployment webserver --type=NodePort --target-port=8080
kubectl get svc
```

Khi tạo 1 Service của loại NodePort, K8s khiến Service của bạn khả dụng trên 1 high port bất kỳ trên toàn bộ cluster. Tuy vậy nếu K8s nodes không thể truy cập được từ bên ngoài, tạo Service với loại này không thể khiến ứng dụng của bạn có thể truy cập được từ Internet. Tuy vậy, chúng ta có thể kiểm tra trạng thái của service sử dụng clusterIP của nó khi đang trên master nodes:

```sh
$ ip=10.105.129.150
$ curl http://$ip:8080
webserver-58fcfb75fb-dz5kn
```

### Create 1 Ingress resource

Lệnh sau định nghĩa 1 Ingress resource mà forwards traffic mà request tới ```http://foo.bar.com/ping``` đến webserver:

```sh
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-octavia-ingress
  annotations:
    kubernetes.io/ingress.class: "openstack"
    octavia.ingress.kubernetes.io/internal: "false"
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - path: /ping
        pathType: Exact
        backend:
          service:
            name: webserver
            port:
              number: 8080
EOF
```

K8s tạo 1 Ingress resource trên cluster của bạn. Octavia-ingress-controller service chạy bên trong cluster chịu trách nhiệm tạo/bảo trì các tài nguyên liên quan trong Octavia để định tuyến tất cả external HTTP traffic (trên port 80) đến webserver NodePort Service bạn đã expose.

*Nếu bạn không muốn Ingress có thể được truy cập từ public internet, bạn có thể đặt annotation ```octavia.ingress.kubernetes.io/internal``` thành true*

Đảm bảo là Ingress Resource đã được tạo. Lưu ý rằng địa chỉ IP cho Ingress Resource sẽ không được định nghĩa ngay lập tức:

```sh
$ kubectl get ing
NAME                   CLASS    HOSTS         ADDRESS   PORTS   AGE
test-octavia-ingress   <none>   foo.bar.com             80      12s
$ # Wait until the ingress gets an IP address
$ kubectl get ing
NAME                   CLASS    HOSTS         ADDRESS          PORTS   AGE
test-octavia-ingress   <none>   foo.bar.com   103.197.62.239   80      25s
```

Giờ ta có thể từ bất kỳ đâu truy cập vào IP của ingress:

```sh
$ ip=103.197.62.239
$ curl -H "Host: foo.bar.com" http://$ip/ping
webserver-58fcfb75fb-dz5kn
```

## Create TLS Ingress

Để sử dụng SSL/TLS cho Ingress, ta có thể tạo Ingress như sau:

```sh
$ cat <<EOF | kubectl apply -f -
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-octavia-ingress
  annotations:
    kubernetes.io/ingress.class: "openstack"
    octavia.ingress.kubernetes.io/internal: "false"
spec:
  defaultBackend:
    service:
      name: default-http-backend
      port:
        number: 80
  tls:
    - secretName: tls-secret
  rules:
    - host: foo.bar.com
      http:
        paths:
        - path: /ping
          pathType: Exact
          backend:
            service:
              name: webserver
              port:
                number: 8080
EOF
$ kubectl get ing
NAME                   HOSTS             ADDRESS        PORTS     AGE
test-octavia-ingress   foo.bar.com       172.24.5.178   80, 443   2m55s
```

Ta có thể test bằng lệnh curl như này:

```sh
$ ip=172.24.5.178
$ curl --cacert ca.crt --resolve foo.bar.com:443:$ip https://foo.bar.com/ping
webserver-58fcfb75fb-dz5kn
```

## Allow CIDRs

Bằng cách sử dụng annotation ```octavia.ingress.kubernetes.io/whitelist-source-range```, ta có thể hạn chế truy cập đến 1 hoặc nhiều dải IP cụ thể (cách nhau bở idaasu phẩy). VD:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-octavia-ingress
  annotations:
    kubernetes.io/ingress.class: "openstack"
    octavia.ingress.kubernetes.io/internal: "false"
    octavia.ingress.kubernetes.io/whitelist-source-range: 192.168.1.0/23
spec:
  rules:
    - host: foo.bar.com
      http:
        paths:
        - path: /ping
          pathType: Exact
          backend:
            service:
              name: webserver
              port:
                number: 8080
```

## Creating Ingress by specifying a floating IP

Đôi khi thì sử dụng 1 floating IP có sẵn vẫn tốt hơn là tạo mới, đặc biệt là trong bối cảnh tự động. Ở ví dụ này, IP 122.112.219.229 là 1 floating IP có sẵn đã tạo trong OpenStack

Bạn có thể chỉ định không xóa floating khi ingress bị xóa. Mặc định, nếu không chỉ định, floating IP sẽ bị xóa với bộ cân bằng tải khi ingress bị xóa khỏi k8s

Tạo 1 deployment mới:

```sh
kubectl create deployment test-web --replicas 3 --image nginx --port 80
```

Tạo 1 service type NodePort

```sh
kubectl expose deployment test-web --type NodePort
```

Tạo 1 ingress và chỉ định floating IP:

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-web-ingress
  annotations:
    kubernetes.io/ingress.class: "openstack"
    octavia.ingress.kubernetes.io/internal: "false"
    octavia.ingress.kubernetes.io/keep-floatingip: "true"        # floating ip will not be deleted when ingress is deleted
    octavia.ingress.kubernetes.io/floatingip: "122.112.219.229"  # define the floating to use 
spec:
  rules:
  - host: test-web.foo.bar.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: test-web
            port:
              number: 80
```