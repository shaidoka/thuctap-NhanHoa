# Logging trong K8s - Phần 3

Trong bài này sẽ giới thiệu về cách cài đặt hệ thống Middle-ware Logging ELK trong K8s

## Cài đặt Elastic search cluster

Tải chart của Elastic search

```sh
helm repo add elastic https://helm.elastic.co
helm search repo elastic/elasticsearch
helm pull elastic/elasticsearch --version 8.5.1
tar -xzf elasticsearch-8.5.1.tgz
cp elasticsearch/values.yaml value-elasticsearch.yaml
```

Chỉnh sửa file value của elastic:

Tài nguyên cấp phát thì tùy vào môi trường mà điều chỉnh cho phù hợp

```sh
resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "1000m"
    memory: "2Gi"
```

AntiAffinity thì mặc định là ```hard```, điều này sẽ khiến các pod elastic search không chạy cùng 1 node, còn ```soft``` thì được phép, do đó tùy vào cluster mà điều chỉnh ```hard``` hay ```soft``` cho phù hợp

```sh
# Changing this to a region would allow you to spread pods across regions
antiAffinityTopologyKey: "kubernetes.io/hostname"

# Hard means that by default pods will only be scheduled if there are enough nodes for them
# and that they will never end up on the same node. Setting this to soft will do this "best effort"
antiAffinity: "soft"

# This is the node affinity settings as defined in
# https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#node-affinity-beta-feature
nodeAffinity: {}
```

Cấu hình Ingress. Phần này không hẳn là cần thiết vì cả bộ ELK cài trên K8s thì về cơ bản đã kết nối in-cluster với nhau rồi.

```sh
ingress:
  enabled: true
  annotations: {}
  # kubernetes.io/ingress.class: nginx
  # kubernetes.io/tls-acme: "true"
  className: "nginx"
  pathtype: Prefix
  hosts:
    - host: elasticsearch.baotrung.xyz
      paths:
        - path: /
  tls: []
```

Cấu hình cho Persistence Volume. Nếu muốn lưu dữ liệu ra bên ngoài thì enable persistence lên. Một lưu ý quan trọng của elastic search là nó không có cấu hình chọn storage class, mà nó dùng storage class mặc định. Do đó nếu muốn dùng storage class nào thì đưa SC đó lên thành default.

```sh
persistence:
  enabled: true
  labels:
    # Add default labels for the volumeClaimTemplate of the StatefulSet
    enabled: false
  annotations: {}

volumeClaimTemplate:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 3Gi
```

Giờ cài đặt elastic search thôi:

```sh
helm install elasticsearch -f value-elasticsearch.yaml elastic/elasticsearch
```

## Cài đặt Kibana

Tải chart của Kibana

```sh
helm search repo elastic/kibana
helm pull elastic/kibana --version 8.5.1
tar -xzf kibana-8.5.1.tgz
cp kibana/values.yaml value-kibana.yaml
```

Cấu hình file value:

```sh
resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "1000m"
    memory: "2Gi"
```

Ingress, do Kibana là công cụ biểu diễn đồ họa nên việc truy cập nó từ môi trường internet bên ngoài là cần thiết

```sh
ingress:
  enabled: true
  className: "nginx"
  pathtype: ImplementationSpecific
  annotations: {}
  # kubernetes.io/ingress.class: nginx
  # kubernetes.io/tls-acme: "true"
  hosts:
    - host: kibana.baotrung.xyz
      paths:
        - path: /
```

Cài đặt Kibana:

```sh
helm install kibana -f value-kibana.yaml elastic/kibana
```

## Cài đặt Logstash

Tải chart của logstash

```sh
helm search repo elastic/logstash
helm pull elastic/logstash --version 8.5.1
tar -xzf logstash-8.5.1.tgz
cp logstash/values.yaml value-logstash.yaml
```

Cấu hình value của logstash chart:

Ta sẽ cấu hình để phân loại log (input) theo tag để lưu vào các index tương ứng trên elastic search.

Cụ thể, với log của opensource (xác định bởi tag "myopensource") sẽ được logstash đẩy vào index có tên logstash-myopensource-{YYYY-MM-dd} => Nhờ đó mỗi ngày sẽ ghi vào 1 index. Tương tự cho log của "myservice" cũng vậy.

Việc này phục vụ cho việc cấu hình thời gian lưu log khác nhau cho các loại log khác nhau. Sau đó sử dụng Elastic Curator để tự động xóa các index cũ theo thời gian tạo. Ý tưởng là xóa các index có tên "logstash-myopensource" quá 7 ngày, và xóa các index có tên "logstash-myservice" quá 30 ngày.

Cấu hình logstash pipeline:

```sh
  logstashPipeline:
    logstash.conf: |
      input {
          beats {
              port => "5044"
        }
      }
      filter {
          grok {
              add_field => [ "received_at", "%{@timestamp}" ]
          }
      }
      output {
        if "myopensource" in [tags] {
           elasticsearch {
             hosts => [ "elasticsearch-master:9200" ]
             index => "logstash_myopensource_%{+YYYY.MM.dd}"
            }
        }
        else if "myservice" in [tags] {
           elasticsearch {
             hosts => [ "elasticsearch-master:9200" ]
             index => "logstash_myservice_%{+YYYY.MM.dd}"
            }
        }
        else {
           elasticsearch {
             hosts => [ "elasticsearch-master:9200" ]
             index => "logstash_default_%{+YYYY.MM.dd}"
            }
        }
      }
```

Cấu hình pipeline của Logstash gồm 3 phần chính là Input, Filter và Output. Trong đó Filter của Logstash có một số loại chính và phổ biến như grok, mutate... và hỗ trợ rất nhiều plugs.

Quay trở lại về bài toán đặt ra ban đầu. Nhiệm vụ của Filebeat là lấy log của các opensource (vernemq, kafka, zookeeper) và service (myservice tự deploy) và gửi về Logstash. Như vậy pipeline của Logstash cần thực hiện như sau:
- **Input:** Lấy input từ Filebeat gửi tới port 5044
- **Filter:** Bước này không bắt buộc (bài toán không yêu cầu parse log). Ở đây chúng ta sử dụng 1 filter đơn giản là add thêm trường "received_at" vào log lấy từ tham số timestamp
- **Output:**
   - Với các đầu vào có chứa keyword "myopensource" trong tags thì gửi tới index "logstash_myopensurce_%{+YYYY.MM.dd}" của elastic search có thông tin kết nối là elasticsearch-master:9200
   - Với các đầu vào có chứa keyword "myservice" trong tags thì gửi tới index "logstash_myservice_%{+YYYY.MM.dd}" của elastic search có thông tin kết nối là elasticsearch-master:9200
   - Trường hợp đầu vào không thỏa mãn cả 2 điều kiện thì lưu vào index "logstash_default_%{+YYYY.MM.dd}" của elastic search có thông tin kết nối là elasticsearch-master:9200

Sau này khi bổ sung thêm các filter để parse log (nhằm lấy dữ liệu log có ích và tối ưu dung lượng lưu trữ) thì chỉ cần bổ sung vào phần filter của cấu hình logstash mà không phải thay đổi gì kiến trúc hệ thống cả.

Ngoài ra các thành phần cấu hình khác như sau:

```sh
logstashJavaOpts: "-Xmx1g -Xms1g"

resources:
  requests:
    cpu: "100m"
    memory: "1024Mi"
  limits:
    cpu: "1000m"
    memory: "2048Mi"

volumeClaimTemplate:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
```

Service

```sh
service:
  # annotations: {}
  type: ClusterIP
  # loadBalancerIP: ""
  ports:
  - name: beats
    port: 5044
    protocol: TCP
    targetPort: 5044
  - name: http
    port: 8080
    protocol: TCP
    targetPort: 8080
```

Ingress

```sh
ingress:
  enabled: true
  annotations:
    {}
    # kubernetes.io/tls-acme: "true"
  className: "nginx"
  pathtype: ImplementationSpecific
  hosts:
    - host: logstash.baotrung.xyz
      paths:
        - path: /beats
          servicePort: 5044
        - path: /http
          servicePort: 8080
```

Cài đặt

```sh
helm install logstash -f value-logstash.yaml elastic/logstash
```

