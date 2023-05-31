# Monitoring trên K8s Cluster dùng Prometheus và Grafana

Prometheus và Grafana là các phần mềm monitor open source được sử dụng rất rộng rãi ở thời điểm hiện tại, không ngoại trừ K8s. 

## Giới thiệu về Prometheus

Prometheus là một phần mềm giám sát mã nguồn mở, và đang ngày 1 trở nên phổ biến. Prometheus rất mạnh và lại đặc biệt phù hợp để dùng cho việc giám sát các dịch vụ trên K8s vì nó hỗ trợ sẵn rất nhiều các bộ template giám sát với các service opensource, giúp việc triển khai và cấu hình giám sát nhanh chóng và hiệu quả. Đi kèm với Prometheus (đóng vai trò giám sát) thì cần có thêm Alert Manager (đóng vai trò cảnh báo) giúp người quản trị thuận tiện hơn rất nhiều.

### Kiến trúc của Prometheus

Thành phần chính của Prometheus được gọi là Prometheus Server gồm các thành phần có nhiệm vụ:
- **Time Series Database:** là nơi lưu trữ thông tin metrics của các đối tượng được giám sát
- **Data Retrieval Worker:** có nhiệm vụ lấy tất cả thông tin metric từ các đối tượng được giám sát như server, services, ứng dụng... và lưu vào database
- **HTTP Server API:** là nơi tiếp nhận các truy vấn lấy dữ liệu được lưu ở DB, nó được sử dụng để hiển thị dữ liệu lên dashboard.

![](./images/K8s_Monitor_1.png)

### Cách thức hoạt động của Prometheus trên K8s

Cách thức hoạt động của Prometheus khá rõ ràng. Nó sẽ định kỳ lấy các thông tin metrics từ **target**, lưu thông tin đó vào DB. HTTP API Server sẽ thực hiện lắng nghe các request từ client (ví dụ Prometheus Dashboard hay Grafana) để lấy thông tin từ DB và trả về kết quả cho client hiển thị lên dashboard.

Prometheus cho phép cấu hình các quy tắc sinh cảnh báo (rule), khi các giá trị thỏa mãn các điều kiện đó thì cảnh báo sẽ được sinh ra và gửi tới **Alert Manager**. Tại Alert Manager sẽ tiếp tục là nơi xử lý gửi cảnh báo tới các nơi nhận, gọi là **receiver**, ví dụ như email, telegram,...

**Cấu hình hoạt động của Prometheus gồm các tham số chính:**
- **global:** Các tham số chung về hoạt động của Prometheus, ví dụ là khoảng thời gian định kỳ pull dữ liệu metric về chẳng hạn
- **alerting:** Thông tin kết nối tới Alert Manager. Ta có thể cấu hình 1 hoặc nhiều Alert Manager tùy vào mục đích sử dụng.
- **rule_files:** Đây là phần quan trọng trong xử lý cảnh báo. Rule file quy định các điều kiện để sinh ra một cảnh báo từ thông tin metric đầu vào. Ví dụ đặt rule RAM của Node > 80% thì đặt cảnh báo cao tải RAM.
- **scrape_configs:** Đây là phần cấu hình liên quan tới kết nối đến các target để lấy metric. Ví dụ ta cần lấy performance của các K8s node, và lấy thêm metric của database đang được cài trên K8s chẳng hạn thì cần cài exporter cho 2 target trên, và cấu hình scrape_configs để lấy thông tin từ exporter đó export ra.

## Giới thiệu về Grafana

Grafana là phần mềm open source dùng để phân tích và hiển thị trực quan dữ liệu. Giúp việc xử lý dữ liệu trên các dashboard với khả năng tùy biến cao, hỗ trợ rất lớn cho việc theo dõi phân tích dữ liệu theo thời gian. Nó lấy nguồn dữ liệu từ nguồn như Prometheus, Graphite hoặc ElasticSearch...

### Các tính năng chính của Grafana

**Dashboard:** Đây là tính năng chính của Grafana với rất nhiều tùy biến cũng như hệ thống template cực kỳ đa dạng giúp việc hiển thị dữ liệu trở nên sinh động, trực quan.

**Alerts:** Việc đặt ngưỡng cảnh báo có thể được thực hiện ở Grafana (tương tự cấu hình rule ở Alert Manager)

**Native Support:** Được hỗ trợ native từ rất nhiều database phổ biến như MySQL, Postgres,...

**Built-in Support:** Hỗ trợ sẵn các datasource đối với Prometheus, Influx DB, CloudWatch, Graphite, ElasticSearch.

## Cài đặt Prometheus và Grafana trên K8s bằng Helm

Khai báo repo của Helm và download helm-chart của Prometheus về:

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add stable https://charts.helm.sh/stable
helm repo update
helm search repo prometheus |egrep "stack|CHART"
helm pull prometheus-community/kube-prometheus-stack --version 45.29.0
tar -xzf kube-prometheus-stack-45.29.0.tgz
cp kube-prometheus-stack/values.yaml values-prometheus.yaml
```

Mở file values mặc định của bộ helm-chart này sẽ thấy nó đã cấu hình Rule cho các thành phần của K8s như etcd, kube-api,..., hay Alert Manager cũng được cài mặc định trong bộ này luôn.

```sh
defaultRules:
  create: true
  rules:
    alertmanager: true
    etcd: true
    configReloaders: true
    general: true
    k8s: true
    kubeApiserverAvailability: true
    kubeApiserverBurnrate: true
    kubeApiserverHistogram: true
    kubeApiserverSlos: true
    kubeControllerManager: true
    kubelet: true
    kubeProxy: true
    kubePrometheusGeneral: true
    kubePrometheusNodeRecording: true
    kubernetesApps: true
    kubernetesResources: true
    kubernetesStorage: true
    kubernetesSystem: true
    kubeSchedulerAlerting: true
    kubeSchedulerRecording: true
    kubeStateMetrics: true
    network: true
    node: true
    nodeExporterAlerting: true
    nodeExporterRecording: true
    prometheus: true
    prometheusOperator: true
```

```sh
alertmanager:

  ## Deploy alertmanager
  ##
  enabled: true

  ## Annotations for Alertmanager
  ##
  annotations: {}

  ## Api that prometheus will use to communicate with alertmanager. Possible values are v1, v2
  ##
  apiVersion: v2
```

Cấu hình tạo ingress cho Alert Manager để kết nối từ bên ngoài vào bằng hostname là alertmanager.monitor.viettq.com

```sh
  ingress:
    enabled: true

    # For Kubernetes >= 1.18 you should specify the ingress-controller via the field ingressClassName
    # See https://kubernetes.io/blog/2020/04/02/improvements-to-the-ingress-api-in-kubernetes-1.18/#specifying-the-class-of-an-ingress
    # ingressClassName: nginx

    annotations: {}

    labels: {}

    ## Redirect ingress to an additional defined port on the service
    # servicePort: 8081

    ## Hosts must be provided if Ingress is enabled.
    ##
    hosts:
      - alertmanager.monitor.baotrung.xyz

    ## Paths to use for ingress rules - one path should match the alertmanagerSpec.routePrefix
    ##
    paths:
      - /
```

Đổi password mặc định khi login vào web Grafana

```sh
adminPassword: gfbsojrebgoj
```

Cấu hình ingress cho Grafana để kết nối từ ngoài vào với hostname grafana.monitor.baotrung.xyz

```sh
  ingress:
    ## If true, Grafana Ingress will be created
    ##
    enabled: true

    ## IngressClassName for Grafana Ingress.
    ## Should be provided if Ingress is enable.
    ##
    # ingressClassName: nginx

    ## Annotations for Grafana Ingress
    ##
    annotations: {}
      # kubernetes.io/ingress.class: nginx
      # kubernetes.io/tls-acme: "true"

    ## Labels to be added to the Ingress
    ##
    labels: {}

    ## Hostnames.
    ## Must be provided if Ingress is enable.
    ##
    hosts:
      - grafana.monitor.baotrung.xyz
    #hosts: []

    ## Path for grafana ingress
    path: /
```

Cấu hình ingress cho Prometheus để kết nối từ ngoài vào qua hostname prometheus.monitor.viettq.com

```sh
   ingress:
     enabled: true

     # For Kubernetes >= 1.18 you should specify the ingress-controller via the field ingressClassName
     # See https://kubernetes.io/blog/2020/04/02/improvements-to-the-ingress-api-in-kubernetes-1.18/#specifying-the-class-of-an-ingress
     # ingressClassName: nginx

     annotations: {}
     labels: {}

     ## Redirect ingress to an additional defined port on the service
     # servicePort: 8081

     ## Hostnames.
     ## Must be provided if Ingress is enabled.
     ##
     hosts:
       - prometheus.monitor.baotrung.xyz
     #hosts: []

     ## Paths to use for ingress rules - one path should match the prometheusSpec.routePrefix
     ##
     paths:
       - /
```

Thêm cấu hình dashboard vào sau thông số .grafana

```sh
grafana:
  # Provision grafana-dashboards-kubernetes
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'grafana-dashboards-kubernetes'
        orgId: 1
        folder: 'Kubernetes'
        type: file
        disableDeletion: true
        editable: true
        options:
          path: /var/lib/grafana/dashboards/grafana-dashboards-kubernetes
  dashboards:
    grafana-dashboards-kubernetes:
      k8s-system-api-server:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-system-api-server.json
        token: ''
      k8s-system-coredns:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-system-coredns.json
        token: ''
      k8s-views-global:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-views-global.json
        token: ''
      k8s-views-namespaces:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-views-namespaces.json
        token: ''
      k8s-views-nodes:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-views-nodes.json
        token: ''
      k8s-views-pods:
        url: https://raw.githubusercontent.com/dotdc/grafana-dashboards-kubernetes/master/dashboards/k8s-views-pods.json
        token: ''
```

Thực hiện cài đặt:

```sh
kubectl create ns monitor
helm -n monitor install prometheus-grafana-stack -f values-prometheus.yaml kube-prometheus-stack
```

![](./images/K8s_Monitor_2.png)

Kiểm tra

```sh
kubectl -n monitor get all
```

![](./images/K8s_Monitor_3.png)

Như trên là helm đã cài đặt xong.

### Cài đặt Nginx-Ingress

Cài đặt NGINX Ingress controller (đã giới thiệu ở bài về Ingress)

Tạo ingress để kết nối vào Service vừa cài bên trên từ domain là **alertmanager.monitor.baotrung.xyz**, **grafana.monitor.baotrung.xyz**, **prometheus.monitor.baotrung.xyz**

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitor-virtual-host-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: alertmanager.monitor.baotrung.xyz
    http:
      paths:
      - backend:
          service:
            name: prometheus-grafana-stack-k-alertmanager
            port:
              number: 9093
        path: /
        pathType: Prefix
  - host: grafana.monitor.baotrung.xyz
    http:
      paths:
      - backend:
          service:
            name: prometheus-grafana-stack
            port:
              number: 80
        path: /
        pathType: Prefix
  - host: prometheus.monitor.baotrung.xyz
    http:
      paths:
      - backend:
          service:
            name: prometheus-grafana-stack-k-prometheus
            port:
              number: 9090
        path: /
        pathType: Prefix
```

Apply

```sh
kubectl -n monitor apply -f app.ingress.yaml
```

Trỏ host về IP trong cluster

```sh
103.159.51.184 grafana.monitor.baotrung.xyz
103.159.51.184 alertmanager.monitor.baotrung.xyz
103.159.51.184 prometheus.monitor.baotrung.xyz
```

Truy cập vào service, lưu ý port ở đây là NodePort của Nginx Ingress Controller

![](./images/K8s_Monitor_4.png)

Lúc này ta đã cài đặt xong bộ công cụ Prometheus + AlertManager + Grafana. Giờ là lúc dùng các thông tin metric lấy được từ Prometheus để hiển thị lên Grafana.

![](./images/K8s_Monitor_10.png)

## Giám sát service trên K8s bằng Prometheus và Grafana

Sau khi cài tới đây thì cơ bản lấy được thông tin của K8s và hiển thị lên Grafana được rồi

Vậy khi cài một ứng dụng khác lên K8s thì việc cài đặt để lấy dữ liệu của nó và hiển thị lên dashboard sẽ như nào? Hãy cùng lab với MinIO.

Ý tưởng là cài MinIO lên K8s, sau đó cấu hình để expose metric của nó, vì có khá nhiều opensource hỗ trợ sẵn metric mà Prometheus có thể hiểu được. Sau đó cấu hình scrape-config của Prometheus để chọc vào MinIO lấy metric. Cuối cùng là lên mạng tìm 1 dashboard template của MinIO import vào Grafana là xong.

### Cài đặt MinIO

Trong bài này sẽ cài MinIO bằng helmchart

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo minio
helm pull bitnami/minio --version=12.6.0
tar -xzf minio-12.6.0.tgz
cp minio/values.yaml values-minio.yaml
```

Giờ thì sửa vài tham số cơ bản của file values-minio.yaml để chạy nó lên gồm enable ingress, gán pvc dung lượng 1Gi và khai báo storageclass

```sh
rootPassword: "gbsjrekbngraj"
ingress:
  enabled: true
  apiVersion: "networking.k8s.io/v1"
  ingressClassName: "nginx"
  hostname: minio.monitor.baotrung.xyz
  annotations:
    prometheus.io/scrape: 'true'
persistence:
  storageClass: "longhorn"
  size: 1Gi
```

Tạo namespace và cài đặt với helm

```sh
kubectl create ns minio-ns
helm -n minio-ns install minio -f values-minio.yaml minio
```

Trỏ host sau đó truy cập

![](./images/K8s_Monitor_11.png)

Đăng nhập vào bằng thông tin đã khai báo trước đó, và tạo thêm 1 vài bucket để giám sát trên Grafana

![](./images/K8s_Monitor_12.png)

Trong file values của minio có tham số ```path: /minio/v2/metrics/cluster``` thì đó là địa chỉ minio expose metrics của nó, ta sẽ dùng thông tin này để cấu hình cho Prometheus

### Cấu hình Prometheus lấy dữ liệu từ Minio

Để lấy được metrics từ MinIO, ta sẽ cần thông tin TOKEN để xác thực kết nối tới MinIO API. Đầu tiên truy cập vào MinIO pod

```sh
k exec minio-586df48495-htqmx -n minio-ns -it -- /bin/bash
```

Đặt Alias cho MinIO API instance (IP ở đây là IP của MinIO service)

```sh
mc alias set mycloud http://10.99.161.246:9000
```

Generate config

```sh
mc admin prometheus generate mycloud
```

Quay lại thư mục cài đặt Prometheus ban đầu, ta sẽ sửa lại file values của prometheus stack để update thêm phần scrape-config cho minio với cấu hình y hệt như ta vừa gen:

```sh
additionalScrapeConfigs:
- job_name: minio-job
  metrics_path: /minio/v2/metrics/cluster
  bearer_token: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJwcm9tZXRoZXVzIiwic3ViIjoiNU1ReTcxYTlrVGxGdHpyaCIsImV4cCI6NDgzODU0MTA0Mn0.lN6QZPxXyagYs0QC8oLVy2RGBHntucsLTw50aG5urg4PRASUfkyVTrZ_pVtlMboQJ97daWBW1MiegVDFRPPe5Q
  scheme: http
  static_configs:
  - targets: ['minio.minio-ns.svc.cluster.local:9000']
```

Trong đó:
- **metric_path:** là đường dẫn được cấu hình ở minio để expose metrics
- **targets:** hiểu đơn giản là khai báo IP/Port để kết nối tới địa chỉ expose metrics. Ở đây ta điền service name của Minio và port của nó. Do Prometheus và MinIO được cài đặt ở 2 namespace khác nhau nên phải đặt service name full format ```<service-name>.<namespace>.svc.<cluster-name>``` trong đó cluster name đang set là ```cluster.local```

Tiếp theo ta update lại Prometheus với helm

```sh
helm -n monitor upgrade prometheus-grafana-stack -f values-prometheus.yaml kube-prometheus-stack
```

Chờ chút để update rồi vào lại web prometheus kiểm tra trong phần target xem đã có MinIO hay chưa:

![](./images/K8s_Monitor_13.png)

![](./images/K8s_Monitor_14.png)

### Cấu hình dashboard hiển thị metrics của MinIO lên Grafana

Ở đây ta sẽ sử dụng dashboard template có ID là **13502**. Import lên Grafana và xem thành quả:

![](./images/K8s_Monitor_15.png)

## Cấu hình cảnh báo qua Alert Manager

Ta tạo thêm cấu hình rule alert cho MinIO với tham số đơn giản là số lượng file của 1 bucket nếu lớn hơn 1 thì sẽ có cảnh báo

Sửa file value của Prometheus như sau:

```sh
# additionalPrometheusRules: []
additionalPrometheusRules:
  - name: minio-rule-file
    groups:
    - name: minio-rule
      rules:
      - alert: MinioBucketUsage
        expr: minio_bucket_usage_object_total{bucket="test-bucket1", instance="10.99.161.246:9000", job="minio-job"} > 1
        for: 10s
        labels:
          severity: page
        annotations:
          summary: High bucket usage
```

Sau khi upgrade helm thì vào prometheus kiểm tra xem

![](./images/K8s_Monitor_16.png)

Tạo 1 vài file trong bucket, sau đó vào alertmanager kiểm tra

![](./images/K8s_Monitor_17.png)