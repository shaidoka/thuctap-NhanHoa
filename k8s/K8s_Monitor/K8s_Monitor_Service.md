# Service Monitor

Trong phần trước ta đã tìm hiểu về cách cài đặt và sử dụng Grafana - Prometheus - Alert Manager stack trên K8s. Vậy bây giờ hãy đi sâu vào:
- Cách cấu hình lấy metric một ứng dụng bằng cấu hình job trong scrapeConfig
- Cách cấu hình lấy metric một ứng dụng bằng Service Monitor
- Cách cài một ứng dụng hỗ trợ sẵn metric và serviceMonitor
- Cách troubleshoot các vấn đề phát sinh khi cấu hình

Kiến trúc tổng quan:

![](./images/K8s_Monitor_Service_1.png)

Mô tả:
- Prometheus lấy thông tin metric từ các đối tượng cần giám sát, chia làm 2 loại:
   - Một loại hỗ trợ expose metric tương thích với Prometheus, nghĩa là nó có sẵn api cho việc lấy metric và ta chỉ cần cấu hình prometheus lấy metric từ đó
   - Một loại không hỗ trợ sẵn metric mà ta sẽ phải cài thêm một exporter (node-exporter là một ví dụ về exporter để lấy metric của node)
   - Note: Việc prometheus lấy dữ liệu từ đối tượng nào được gọi là các **job**. Các job này chứa thông tin đối tượng nó cần lấy metric cũng như cách lấy metric (tần suất, thời gian lưu,...). Và để tạo các job này có 2 cách:
      - Cấu hình **scrape-config** cho prometheus: Cách này là cách truyền thống và quản lý sẽ rất vất vả nếu số lượng job lớn do file cấu hình phình to. Hơn nữa mỗi lần update là phải update cả stack để nó nhận cấu hình mới
      - Cấu hình **service monitor**: Cách này hiệu quả hơn vì cho khả năng kiểm soát tốt hơn với từng đối tượng giám sát sẽ tương ứng một file yaml cấu hình riêng cho nó. Hơn nữa không phải đổi lại cấu hình của prometheus server (không cần update stack)
- Khi lấy được metric thì nó sẽ hoàn thiên thông tin của metric đó, như gán label namespace, jobname, servicename,... để phân loại và ghi vào database của Prometheus
- Prometheus đọc các prometheus rule (là các hàm so sánh giá trị metric với các ngưỡng xác định) để quyết định những rule nào cần cảnh báo để đẩy về Alert Manager
- Alert Manager sẽ có config riêng của nó để thực hiện việc phân luồng cảnh báo tới các người nhận khác nhau, việc này được gọi là "route". Thông tin người nhận (gọi là receiver) được cấu hình ở Alert Manager, hỗ trợ khá đa dạng từ email, slack, telegram,...

## Prometheus Job và Service monitor

Là đối tượng lưu thông tin về cách thức lấy dữ liệu metric của một đối tượng cần giám sát, có thể là service, node,... thông tin của job, được cấu hình trong scrape-config của Prometheus. Một số tham số cấu hình của job có thể không khai báo thì sẽ lấy mặc định ở khai báo global. Với bộ **kube-prometheus-stack** thì việc khai báo job trong scrapeConfig được thực hiện ở phần cấu hình trong helm-value như sau:

```sh
additionalScrapeConfigs:
- job_name: minio-job
  scrape_interval: 30s
  scrape_timeout: 5s
  bearer_token: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJwcm9tZXRoZXVzIiwic3ViIjoiNU1ReTcxYTlrVGxGdHpyaCIsImV4cCI6NDgzOTAxOTA2Mn0.v2aOUHXcPom9mgZAgrPFPjuQRjc-hoWlB6xU0HHLObtfjiVd4eMCCc1scF8c7voxgoCJxvgzXIk5t9q-ixFFng
  metrics_path: /minio/v2/metrics/cluster
  scheme: http
  static_configs:
  - targets: ['10.99.161.246:9000']
```

Sau đó upgrade lại stack để cập nhật giá trị mới:

```sh
helm -n monitoring upgrade prometheus-stack -f values-prometheus-clusterIP.yaml kube-prometheus-stack
```

Và để cấu hình được prometheus job thì ta cần nắm rõ thông tin về đối tượng sẽ lấy metric để khai báo tham số, quan trọng nhất là **metrics_path** và **targets**

Chi tiết được đề cập tại [Prometheus document](https://prometheus.io/docs/)

Tuy nhiên vấn đề đặt ra là ta không thể nào cứ cấu hình thủ công từng metric 1 như vậy, nếu sau này cluster lớn dần ra thì ta sẽ không thể kiểm soát được. Hơn nữa mỗi lần cập nhật cấu hình lại phải upgrade lại helm chart và sau đó ngồi chờ 10 15p để helm cập nhật thì không hợp lý chút nào.

Và do đó Service Monitor ra đời để giải quyết vấn đề này.

## Service Monitor

Service Monitor là một đối tượng của K8s giúp cho Prometheus có thể tự động phát hiện được các đối tượng cần lấy metric. Nó sẽ chứa các thông tin về đối tượng cần giám sát tương tự như cấu hình job trong scrape-config.

Về nguyên lý hoạt động, hãy quan sát hình vẽ sau

![](./images/K8s_Monitor_Service_2.png)

Cách thức hoạt động:
- Prometheus sẽ đọc thông tin job ở scrapeConfig và từ các ServiceMonitor, tất cả các đối tượng này sẽ hiển thị ở phần **targets** của Prometheus
   - Việc đọc từ scrapeConfig là mặc định
   - Đọc ServiceMonitor thì dựa vào cấu hình của Prometheus gồm 2 tham số:
      - **serviceMonitorNamespaceSelector:** là cấu hình chỉ đọc các ServiceMonitor ở một số namespace nhất định, mặc định là đọc từ tất cả namespace
      - **serviceMonitorSelector:** là cấu hình về cách chọn các ServiceMonitor sẽ được đọc để lưu cấu hình job cho Prometheus. Có thể cấu hình theo nhiều rule khác nhau, trong bài này sẽ sử dụng cách cấu hình theo **label** của **ServiceMonitor**, cũng là cách đơn giản nhất
- Trong cấu hình của ServiceMonitor sẽ có thông tin **label** của nó (dùng cho Prometheus select như trên) và các thông tin tới đối tượng cần giám sát (giống các thông tin khai báo cho job trong scrapeConfig)

Như vậy trước tiên ta cần cấu hình lại Prometheus để update cấu hình Service Monitor selector. Ở đây ta sẽ select từ tất cả namespace, và sẽ filter các ServiceMonitor có gán label ```app.kubernets.io/instance``` tương ứng với giá trị ta sẽ set cho các serviceMonitor khai báo sau này ```service-monitor```

Sửa lại tham số ```serviceMonitorSelector``` trong helm value của kube-prometheus-stack như sau:

```sh
serviceMonitorSelector:
  matchExpressions:
  - key: app.kubernetes.io/instance
    operator: In
    values:
    - service-monitor
    - nginx-ingress-controller
    - prometheus-stack
```

Cập nhật cấu hình stack prometheus:

```sh
helm -n monitoring upgrade prometheus-stack -f values-prometheus-clusterIP.yaml kube-prometheus-stack
```

Như vậy tất cả các serviceMonitor ở tất cả các namespace nếu có gán label ```app.kubernetes.io/instance``` với 1 trong các giá trị như trên thì sẽ được Prometheus đọc và nạp vào cấu hình của nó.

Đến đây thì việc giám sát thêm 10 hay 20 service mới đã không còn là vấn đề nữa. Ta chỉ cần thống nhất 1 label sẽ gán cho toàn bộ các serviceMonitor mới sau này trùng với cấu hình serviceMonitorSelector của Prometheus là nó sẽ tự động được đọc và không cần phải update gì với Prometheus nữa cả. Ngoài ra, với phương thức này, mỗi service cần giám sát ta sẽ chỉ cần tạo 1 file serviceMonitor dạng yaml rất tiện lợi cho việc quản lý, cập nhật và tái sử dụng sau này.

Đây là mẫu cấu hình của Service Monitor để giám sát service minio, tương tự với cấu hình scrapeConfig đã đề cập trước đó. Tạo file servicemonitor-minio.yaml như sau:

```sh
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: minio-monitor
  namespace: monitor
  labels:
    app.kubernetes.io/instance: service-monitor
spec:
  endpoints:
  - port: 9000
    interval: 15s
    scheme: http
    metrics_path: /minio/v2/metrics/cluster
  namespaceSelector:
    matchNames:
    - monitor
  selector:
    matchLabels:
      app.kubernetes.io/instance: minio
```

Apply và kiểm tra kết quả:

```sh
kubectl apply -f serviceMonitor-minio.yaml
kubectl -n monitor get servicemonitors.monitoring.coreos.com -l "app.kubernetes.io/instance=service-monitor"
```

Với cấu hình trên thì đối tượng serviceMonitor có tên là **minio-monitor** sẽ được deploy vào namespace là **monitor**, và có gán key ```app.kubernetes.io/instance: service-monitor``` thỏa mãn điều kiện trong cấu hình serviceMonitorSelector của Prometheus nên nó sẽ được Prometheus nạp vào cấu hình của nó.

Tiếp đến, trong cấu hình của serviceMonitor này sẽ có phần cấu hình **spec** bao gồm thông tin lấy metric từ đối tượng cần giám sát, gồm thông tin **endpoints** (port/metric_path) và thông tin object cần giám sát (**namespaceSelector** và **selector**)

Để làm rõ chỗ này, ta thực hiện lệnh get service theo thông tin selector bên trên trong cấu hình serviceMonitor sẽ rõ. Nó sẽ tìm đến service ở namespace là **monitor** có gán label ```app.kubernetes.io/instance=minio```

```sh
kubectl -n monitor get service -l "app.kubernetes.io/instance=minio"

NAME    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
minio   ClusterIP   10.233.19.122   <none>        9000/TCP,9001/TCP   21d
```

Chỗ này cần lưu ý về đối tượng giám sát có 2 loại như đã nói bên trên: loại hỗ trợ metric và loại dùng exporter. Trong trường hợp này minio hỗ trợ sẵn metric nên ta sẽ kết nối tới service minio ở port và path mà nó cung cấp metric.

Với trường hợp service không hỗ trợ metric mà phải dùng exporter thì ta sẽ cần cấu hình phần endpoints và selector bên trên tới thông tin service exporter

## Cài service hỗ trợ sẵn cả metric và serviceMonitor (redis)

Có một điều tuyệt vời là nhiều open-source cài qua helm chart ngoài hỗ trợ sẵn metric còn hỗ trợ luôn cả template tạo serviceMonitor và PrometheusRule luôn. Ở đây ta cài thử **redis** bằng helm. 

```sh
mkdir -p /home/sysadmin/open-sources
cd /home/sysadmin/open-sources
mkdir redis
cd redis
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo redis
helm pull bitnami/redis-cluster
ls -lrt
tar -xzf redis-cluster-7.5.1.tgz
cp redis-cluster/values.yaml values-redis.yaml
vi values-redis.yaml
```

Sửa 1 vài tham số như sau để enable metric và serviceMonitor:

```sh
usePassword: false
redis: "30101"
type: NodePort
storageClass: "longhorn"
size: 1Gi

metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: "monitor"
    labels:
      app.kubernetes.io/instance: service-monitor
```

Sau khi cập nhật giá trị trong file values-redis.yaml thì thực hiện cài đặt

```sh
helm -n prod install redis-cluster -f values-redis.yaml redis-cluster
```

Kiểm tra

```sh
kubectl -n prod get pods -l " app.kubernetes.io/instance=redis-cluster"

NAME              READY   STATUS    RESTARTS      AGE
redis-cluster-0   2/2     Running   1 (40s ago)   3m47s
redis-cluster-1   2/2     Running   2 (58s ago)   3m47s
redis-cluster-2   2/2     Running   1 (31s ago)   3m46s
redis-cluster-3   2/2     Running   1 (43s ago)   3m46s
redis-cluster-4   2/2     Running   2 (29s ago)   3m46s
redis-cluster-5   2/2     Running   1 (61s ago)   3m46s
```

```sh
kubectl -n prod get service -l " app.kubernetes.io/instance=redis-cluster"

NAME                     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)              AGE
redis-cluster            NodePort    10.103.63.133   <none>        6379:30101/TCP       3m31s
redis-cluster-headless   ClusterIP   None            <none>        6379/TCP,16379/TCP   3m31s
redis-cluster-metrics    ClusterIP   10.100.243.76   <none>        9121/TCP             3m31s
```

```sh
kubectl -n monitor get servicemonitors.monitoring.coreos.com redis-cluster

NAME            AGE
redis-cluster   4m13s
```

Như vậy là ta có 1 cụm redis-cluster gồm 6 pods, 3 service ở namespace **prod** và một object serviceMonitor là **redis-cluster** được tạo ở namespace **monitor**

Kiểm tra xem serviceMonitor của redis có gì:

```sh
kubectl -n monitor describe servicemonitors.monitoring.coreos.com redis-cluster

Name:         redis-cluster
Namespace:    monitor
Labels:       app.kubernetes.io/instance=service-monitor
              app.kubernetes.io/managed-by=Helm
              app.kubernetes.io/name=redis-cluster
              helm.sh/chart=redis-cluster-8.6.2
Annotations:  meta.helm.sh/release-name: redis-cluster
              meta.helm.sh/release-namespace: prod
API Version:  monitoring.coreos.com/v1
Kind:         ServiceMonitor
Metadata:
  Creation Timestamp:  2023-05-30T08:15:52Z
  Generation:          1
  Resource Version:    7584982
  UID:                 259ec53b-cf1c-406f-afb2-5a052b55f68e
Spec:
  Endpoints:
    Port:  metrics
  Namespace Selector:
    Match Names:
      prod
  Selector:
    Match Labels:
      app.kubernetes.io/component:  metrics
      app.kubernetes.io/instance:   redis-cluster
      app.kubernetes.io/name:       redis-cluster
Events:                             <none>
```

Trong đó ta thấy một vài thông tin quan trọng như:
- **Labels: app.kubernetes.io/instance=service-monitor** => Đây là thông tin label để Prometheus lựa chọn lấy metric. Với mỗi serviceMonitor mới ta sẽ đều thêm label này để được đọc tự động vào Prometheus.
- **Thông tin spec:** Là thông tin tới đối tượng cần lấy metric. Ở đây nó tự hiểu cần kết nối tới service ở namespace prod mà có gán các Label như bên dưới, ở port tên là metrics.

```sh
Spec:
  Endpoints:
    Port:  metrics
  Namespace Selector:
    Match Names:
      prod
  Selector:
    Match Labels:
      app.kubernetes.io/component:  metrics
      app.kubernetes.io/instance:   redis-cluster
      app.kubernetes.io/name:       redis-cluster
```

Kiểm tra thông tin service được chỉ định theo spec trên bằng lệnh:

```sh
kubectl -n prod get service -l "app.kubernetes.io/component=metrics" -l "app.kubernetes.io/instance=redis-cluster" -l "app.kubernetes.io/name=redis-cluster"

NAME                     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)              AGE
redis-cluster            NodePort    10.103.63.133   <none>        6379:30101/TCP       17m
redis-cluster-headless   ClusterIP   None            <none>        6379/TCP,16379/TCP   17m
redis-cluster-metrics    ClusterIP   10.100.243.76   <none>        9121/TCP             17m
```

Truy cập trang Prometheus sẽ thấy có target liên quan

![](./images/K8s_Monitor_Service_3.png)

Giờ kiếm dashboard rồi import vào thôi, trong bài viết này sẽ sử dụng dashboard ID **11835**

![](./images/K8s_Monitor_Service_4.png)

## Longhorn storage

Để cấu hình serviceMonitor lấy metric Longhorn của tất cả các node, ta sử dụng file cấu hình ServiceMonitor như sau:

```sh
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: longhorn-prometheus-servicemonitor
  namespace: monitor
  labels:
    name: longhorn-prometheus-servicemonitor
    release:  prometheus-grafana-stack
    k8s-app: longhorn
    app: kube-prometheus-stack
    app.kubernetes.io/instance: service-monitor
spec:
  selector:
    matchLabels:
      app: longhorn-manager
  namespaceSelector:
    matchNames:
    - storage
  endpoints:
  - port: manager
```

Trong bài này sẽ sử dụng Dashboard ID **13032**

![](./images/K8s_Monitor_Service_5.png)