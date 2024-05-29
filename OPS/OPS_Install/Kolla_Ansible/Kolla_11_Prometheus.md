# Prometheus - Monitoring System & Time Series Database

Kolla có thể triển khai 1 Prometheus hoàn chỉnh và hoạt động trong cả hệ thống ```all-in-one``` hoặc ```multinode```

## Preparation and Deployment

Để enable Prometheus, chỉnh sửa file cấu hình ```/etc/kolla/globals.yml``` và thay đổi như sau:

```sh
enable_prometheus: "yes"
```

Lưu ý: Bằng việc thiết lập này, Promethus 2.x sẽ được triển khai. Bất kỳ sự hiện diện nào của Prometheus 1.x trong hệ thống sẽ gây mâu thuẫn. Do đó, các triển khai trước đó của Promethus nên được xóa đi thủ công. Để loại bỏ các volume chứa dữ liệu cũ của Prometheus 1.x, hãy thực thi lệnh sau trên host mà đã deploy prometheus:

```sh
docker volume rm prometheus
```

## Basic Auth

Prometheus được bảo vệ với basic HTTP authentication. Kolla-ansible sẽ tạo các user sau: ```admin```, ```grafana``` (nếu grafana được bật), ```skyline``` (nếu skyline được bật). Grafana username có thể được tùy chỉnh thông qua biến ```prometheus_grafana_user```, còn skyline username thì qua ```prometheus_skyline_user```. Password của chúng thì định nghĩa trong biến ```prometheus_password```, ```prometheus_grafana_password```, và ```prometheus_skyline_password``` trong ```passwords.yml```. Danh sách basic auth user có thể được mở rộng thêm bằng biến sau:

```sh
prometheus_basic_auth_users_extra:
   - username: user
     password: hello
     enabled: true
```

## Extending the default command line options

Ta có thể mở rộng các tùy chọn command line mặc định bằng cách sử dụng biến tùy chỉnh. Ví dụ, thiết lập query timeout thành 1 phút và data retention size thành 30GB:

```sh
prometheus_cmdline_extras: "--query.timeout=1m --storage.tsdb.retention.size=30GB"
```

## Configuration options

|Option|Default|Description|
|:-|:-|:-|
|prometheus_scrape_interval|60s|Default scrape interval for all jobs|

## Extending prometheus.cfg

Nếu bạn muốn thêm extra targets vào scrap, bạn có thể mở rộng file cấu hình mặc định ```prometheus.yml``` bằng cách thêm config vào ```{{ node_custom_config }}/prometheus/prometheus.yml.d```. Những file cấu hình thêm này nên có cùng định dạng với ```prometheus.yml```. Những file này mddeefud dược merged vì vậy bất kỳ list items nào đều được mở rộng. VD, nếu sử dụng giá trị mặc định cho ```node_custom_config```, bạn có thể thêm targets vào scrape bằng cách định nghĩa ```/etc/kolla/config/prometheus/prometheus.yml.d/10-custom.yml``` như sau:

```sh
scrape_configs:
  - job_name: custom
    static_configs:
      - targets:
        - '10.0.0.111:1234'
  - job_name: custom-template
    static_configs:
      - targets:
{% for host in groups['prometheus'] %}
        - '{{ hostvars[host]['ansible_' + hostvars[host]['api_interface']]['ipv4']['address'] }}:{{ 3456 }}'
{% endfor %}
```

2 jobs ```custom``` và ```custom_template``` cần được thêm vào danh sách mặc định của ```scrape_configs``` trong ```prometheus.yml```. Để customize trên từng host, ta sẽ cần đặt file ở ```{{ node_custom_config }}/prometheus/<inventory_hostname>/prometheus.yml.d```, vì vậy để ghi đè 1 danh sách giá trị thay vì mở rộng nó, ta sẽ cần đảm bảo ko có file nào ở ```{{ node_custom_config }}/prometheus/prometheus.yml.d``` thiết lập 1 key với 1 hierarchical path tương ứng.

## Extra files

Đôi khi ta sẽ cần tham chiếu thêm file từ trong ```prometheus.yml```. Ví dụ, khi định nghĩa file service discovery configuration. Để cho phép ta làm điều này, kolla-ansible sẽ recursively discover bất kỳ files nào trong ```{{ node_custom_config }}/prometheus/extras``` và template chúng. Đầu ra đã được template sau đó sẽ được copy vào ```/etc/prometheus/extras``` bên trong container khi khởi động. Ví dụ để cấu hình ```impi exporter```, sử dụng giá trị mặc định cho ```node_custom_config```, ta có thể tạo 2 file sau: 

- ```/etc/kolla/config/prometheus/prometheus.yml.d/ipmi-exporter.yml```

```sh
---
scrape_configs:
- job_name: ipmi
  params:
    module: ["default"]
    scrape_interval: 1m
    scrape_timeout: 30s
    metrics_path: /ipmi
    scheme: http
    file_sd_configs:
      - files:
          - /etc/prometheus/extras/file_sd/ipmi-exporter-targets.yml
    refresh_interval: 5m
    relabel_configs:
      - source_labels: [__address__]
        separator: ;
        regex: (.*)
        target_label: __param_target
        replacement: ${1}
        action: replace
      - source_labels: [__param_target]
        separator: ;
        regex: (.*)
        target_label: instance
        replacement: ${1}
        action: replace
      - separator: ;
        regex: .*
        target_label: __address__
        replacement: "{{ ipmi_exporter_listen_address }}:9290"
        action: replace
```

Trong đó ```ipmi_exporter_listen_address``` là 1 biến chứa địa chỉ IP của node, nơi mà exporter đang chạy

- ```/etc/kolla/config/prometheus/extras/file_sd/ipmi-exporter-targets.yml```

```sh
---
- targets:
  - 192.168.1.1
labels:
    job: ipmi_exporter
```

## Metric Instance labels

Trước đó, Prometheus metrics đã đánh nhãn instance dựa trên địa chỉ IP của chúng. Hành vi này có thể được thay đổi như việc đánh nhãn chúng dựa trên inventory hostname. Địa chỉ IP vẫn là target address, theo đó, ngay cả khi hostname có thể phân giải được, nó không gây ra vấn đề gì cả.

Hành vi mặc định vẫn đánh nhãn instance với địa chỉ IP của chúng. Tuy nhiên, điều này có thể thay đổi bằng cách chỉnh sửa biến ```prometheus_instance_label``` trong ```globals.yml```. Biến này chấp nhận các giá trị sau:

- ```None```: Instace labels sẽ là địa chỉ IP (mặc định)
- ```{{ ansible_facts.hostname }}```: Instance labels sẽ là hostnames
- ```{{ ansible_facts.nodename }}```: Instance labels sẽ là FQDNs

Lưu ý là sau khi thay đổi biến này sẽ khiến Prometheus scrape metrics với tên mới trong 1 khoảng thời gian ngắn. Điều này sẽ dẫn đến duplicate metrics cho đến khi tất cả metrics đã được thay thế với labels mới.

Tính năng đánh nhãn metrics này sẽ trở thành cài đặt mặc định trong các bản phát hành tiếp theo. Do đó, nếu bạn muốn giữ cấu hình mặc định hiện tại (gán nhãn bằng địa chỉ IP), bạn sẽ phải đặt biến ```prometheus_instance_label``` thành ```None```.