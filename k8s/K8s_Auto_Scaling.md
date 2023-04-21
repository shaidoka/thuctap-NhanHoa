# Automatic scaling

Có 2 phương pháp scaling (pod/cluster) là **horizontal scaling** và **vertical scaling**:
- **Horizontal scaling** là cách scale mà ta sẽ tăng số lượng worker (application) đang xử lý công việc hiện tại ra nhiều hơn. Ví dụ ta đang có 2 pod để xử lý tích điểm cho client khi client tạo deal thành công, khi số lượng client tăng đột biến, 2 pod không thể xử lý kịp, ta sẽ scale số lượng pod lên thành 4 chẳng hạn.
- **Vertical scaling** là cách scale thay vì tăng số lượng worker, ta sẽ tăng lượng tài nguyên của ứng dụng đó lên, như là tăng số CPU và RAM của ứng dụng đó. Ví dụ ta có một model để train AI, việc train này không thể tách ra 1 model khác để tăng tốc độ train được, mà ta chỉ có thể ăng CPU và memory cho model đó.

Trong K8s, ta horizontal scale bằng cách tăng số lượng ở thuộc tính replicas của ReplicationController như ReplicaSet/Deployment. Vertical scale bằng cách tăng resource requests và limits của Pod. Ta có thể làm việc này thủ công, nhưng sẽ rất bất tiện, do không thể ngồi cả ngày để kiểm tra lúc nào ứng dụng có nhiều client thì ta scale được.

K8s cung cấp cho ta cách autoscaling dựa vào việc phát hiện CPU và Memory ta chỉ định đạt tới ngưỡng scale. Nếu ta xài cloud, nó còn có thể tự động tạo thêm worker node khi phát hiện không còn đủ node để deploy pod

## Horizontal pod autoscaling

Horizontal pod autoscaling là cách ta tăng giá trị replicas ở trong các scalable resource (Deployment, ReplicaSet, ReplicationController, hay StatefulSet) để scale số lượng Pod. Công việc này được thực hiện bởi Horizontal controller khi ta tạo 1 HorizontalPodAutoscaler (HPA) resource. Horizontal controller sẽ thường xuyên kiểm tra metric của pod, tính toán số lượng pod replicas phù hợp dựa vào metric kiểm tra của pod hiện tại với giá trị metric mà ta đã chỉ định ở trong HPA resource, sau đó sẽ thay đổi trường replicas của các scalable resource (Deployment, ReplicaSet, ReplicationController, or StatefulSet) nếu nó thấy cần thiết.

Ví dụ 1 file config HPA sẽ như sau:

```sh
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: micro-services-autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservice-user-products
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

Với config trên, ta chỉ định scalable resource bằng thuộc tính scaleTargetRef, ta chọn resource ta muốn scale là Deployment và tên của Deployment đó, ta chỉ định số lượng min và max replicas bằng 2 thuộc tính minReplicas, maxReplicas. Metric mà ta muốn thu thập là memory, với giá trị ngưỡng là 70%. Khi metric thu thập được từ Pod vượt qua giá trị này, quá trình autoScaling sẽ được thực thi.

### 1. Quá trình Autscaling 

Quá trình autoscaling được chia thành 3 giai đoạn như sau:
- Thu thập metrics của tất cả các pod được quản lý bởi scalable resource mà ta chỉ định trong HPA
- Tính toán số lượng Pod cần thiết dựa vào metrics thu thập được
- Cập nhật lại trường replicas của scalable resource

### 2. Thu thập metrics

Horizontal controller sẽ không trực tiếp thu thập metrics của Pod, mà nó sẽ lấy thông qua một đối tượng khác, được gọi là metrics server. Ở trên từng worker node, sẽ có 1 đối tượng được gọi là **cAdvisor**, đây là một component của kubelet, có nhiệm vụ thu thập metric của Pod và node, sau đó những metric này sẽ được tổng hợp ở metrics server, và horizontal controller sẽ lấy metric từ metrics server ra.

![](./images/K8s_Auto_Scaling_1.png)

Ta cần lưu ý một điều ở đây là metrics server này là một add-ons, chứ nó không có sẵn trong K8s cluster của ta, nếu ta muốn sử dụng được tính năng autoscaling, ta cần phải cài metrics server này vào. Tài liệu gốc ở [đây](https://github.com/kubernetes-sigs/metrics-server). Nhìn chung là ta chạy lệnh sau để install bản mới nhất (support K8s v1.21+)

```sh
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Kubelet certificate cần phải được ký bởi cluster CA, hoặc tắt nó đi bằng cách

```sh
kubectl edit deployment metrics-server -n kube-system
```
Sau đó tìm đến ```.spec.template.spec.container[].args[]``` và thêm tham số sau vào ```--kubelet-insecure-tls```

Kiểm tra đã cài đặt thành công chưa bằng lệnh

```sh
kubectl top node
```

![](./images/K8s_Auto_Scaling_2.png)

### 3. Tính toán số lượng pod cần thiết

Sau khi horizontal controller thu thập được metric, nó sẽ tiến hành giai đoạn tiếp theo là tính toán số lượng Pod dựa theo metric thu thập được với số metric ta chỉ định trong HPA, nó sẽ tính toán theo công thức có sẵn với đầu vào là pod metrics và đầu ra là số replicas. Công thức đơn giản hóa như sau:

```sh
desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]
```

#### Ví dụ 1: Với 1 metric

Khi 1 HPA cấu hình chỉ có 1 metric (chỉ có CPU hoặc memory) thì việc tính toán số lượng pod chỉ có một bước là sử dụng công thức trên. Ví dụ ta có giá trị current metric hiện tại là 200m, giá trị desired là 100m, current replicas là 2, ta sẽ có:

```sh
currentMetricValue / desiredMetricValue = 200m / 100m = 2

desiredReplicas = ceil[2 * 2] = 4
```

Số lượng replicas của ta bây giờ sẽ được scale từ 2 lên 4. Một ví dụ khác là ta có giá trị curent metric là 50m, giá trị desired là 100m, ta sẽ có:

```sh
currentMetricValue / desiredMetricValue = 50m / 100m = 0.5

disiredReplicas = ceil[2 * 0.5] = 1
```

#### Ví dụ 2: Với nhiều metric

Khi HPA của ta cấu hình mà có nhiều metric, ví dụ có cả cpu và queries-per-second (QPS), thì việc tính toán cũng không khác là mấy, horizontal controller sẽ tính ra giá trị replicas của từng metric riêng lẻ, sau đó lấy giá trị replicas lớn nhất

Ví dụ ta có replicas sau khi tính ra của CPU là 4, QPS là 3, thì max(4,3) = 4, số lượng replica sẽ được scale lên 4

![](./images/K8s_Auto_Scaling_3.png)

### 4. Cập nhật trường Replicas

Đây là bước cuối cùng của quá trình autoscaling, horizontal controller sẽ cập nhật lại giá trị replicas của resource ta chỉ định trong HPA, và để resource đó tự động thực hiện việc tăng số lượng Pod. Hiện tại thì autoscaling chỉ hỗ trợ các resource sau đây:
- Deployments:
- ReplicaSets
- ReplicationController
- StatefulSets

## Thực hành Scale Horizontal

### 1. Scale theo CPU

Giờ ta sẽ tạo 1 deployment và 1 HPA, lưu ý là deploy buộc phải có .resources.requests

```sh
cat << EOF > deploy-scaling-horizontal.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubia
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kubia
  template:
    metadata:
      labels:
        app: kubia
    spec:
      containers:
      - image: luksa/kubia:v1
        name: nodejs
        resources:
          requests:
            cpu: 100m
EOF
```

Ở file config trên, ta tạo Deployment với số lượng replicas là 3, và cpu requests là 100m. Giờ ta sẽ tạo HPA, tạo 1 file tên là ```hpa.yaml``` với config như sau:

```sh
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kubia
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kubia
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 30
```

Tạo và kiểm thử

```sh
kubectl apply -f deploy-scaling-horizontal.yaml
kubectl apply -f hpa.yaml
kubectl get hpa
```

![](./images/K8s_Auto_Scaling_4.png)

Do CPU đang sử dụng ~0%, vài phút sau ta get lại sẽ thấy replica scale xuống 1

![](./images/K8s_Auto_Scaling_5.png)

Hoặc ta có thể dùng lệnh sau để theo dõi trực quan hơn quá trình scaling

```sh
watch -n 1 kubectl get hpa,deployment
```

Để trigger scalup, đầu tiên ta cần expose deployment

```sh
kubectl expose deployment kubia --port=80 --target-port=8080
kubectl run -it --rm --restart=Never loadgenerator --image=busybox -- sh -c "while true; do wget -O - -q http://kubia; done"
```

**Chú ý:** AutoScaling có 1 thông số gọi là Maximum rate of scaling, thông số này giới hạn số replica có thể scale trong 1 lần, mặc định là **gấp 2 lần số lượng replicas hiện tại**, nếu số lượng relicas hiện tại là 1 hoặc 2 thì tối đa replicas được scale là 4.

### 2. Scale theo memory

Việc config scale memory không khác gì so với CPU. Tuy nhiên ta cần phải lưu ý rằng việc release và sử dụng memory sẽ phụ thuộc vào ứng dụng bên trong container. Khi ta scale up số lượng Pod lên dựa vào memory, system không thể chắc chắn rằng số lượng sử dụng memory của từng ứng dụng sẽ giảm đi, vì điều này phụ thuộc vào cách ta viết ứng dụng, nếu sau khi ta scale up Pod, ứng dụng vẫn sử dụng memory nhiều như trước hoặc thậm chí nhiều hơn, quá trình scale sẽ lặp lại và đạt tới ngưỡng maximum Pod của worker node và có thể dẫn tới die worker node. Vì vậy khi scale Pod dựa vào memory thì ta phải xem xét nhiều yếu tố hơn chứ không phải chỉ config HPA là xong.

### 3. Scale theo metric khác

Ngoài CPU và memory, K8s cũng có hỗ trợ 1 số metric khác mà ta cũng hay xài, ở trên ta đã sử dụng ```type: Resource``` với CPU và memory, còn 2 ```type``` khác là ```Pods``` và ```Object```

Ví dụ: với type Pods, ta có thể theo dõi Queries-Per-Second và number of messages trong queue, chẳng hạn như:

```sh
metrics:
- type: Pods
  resource:
    metricName: qps
    targetAverageValue: 100
```

Object metric là những metric mà không liên quan trực tiếp tới Pod, mà sẽ liên quan tới những resource khác của cluster. Ví dụ như ingress:

```sh
metrics:
- type: Object
  object:
    metric:
      name: requests-per-second
    describedObject:
      apiVersion: networking.k8s.io/v1
      kind: Ingress
      name: main-route
    target:
      type: Value
      value: 2k
```

## Vertical pod AutoScaling

Ta đã thấy horizontal scaling giúp ta giải quyết được nhiều vấn đề performance của ứng dụng, nhưng không phải ứng dụng nào ta cũng có thể scale theo kiểu horizontal được, như việc train AI mà ta đã đề cập ở đầu bài viết. Vì vậy ta cần phải scale để tăng tài nguyên của Pod lên (hoặc giảm)

Ta cần lưu ý hiện tại K8s không hỗ trợ resource Vertical có sẵn mà phải cài thêm add-ons như hướng dẫn ở [đây](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)

Ví dụ 1 file cấu hình VerticalPodAutoscaler như sau:

```sh
apiVersion: autoscaling.k8s.io
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
```

Với ```targetRef``` ta sẽ chọn resource ta thu thập để scale, và ```updatePolicy.updateMode``` có 3 chế độ là ```Off```, ```Initial``` và ```Auto```

