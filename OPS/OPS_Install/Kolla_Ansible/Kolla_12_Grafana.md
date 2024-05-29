# Grafana

Grafana là 1 nền tảng giám và biểu diễn dữ liệu đồ họa mã nguồn mở. Biểu diễn metrics, logs, và traces từ nhiều nguồn như Prometheus, Loki, Elasticsearch, InfluxDB, Postgres và nhiều hơn nữa.

## Preparation and deployment

Để enable Grafana, chỉnh sửa file cấu hình ```globals.yml``` như sau:

```sh
enable_grafana: "yes"
```

Nếu bạn muốn thiết lập Prometheus thành data source, hãy thiết lập thêm:

```sh
enable_prometheus: "yes"
```

## Custom dashboards provisioning

Kolla Ansible thiết lập custom dashboards provisioning sử dụng [Dashboard provider](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

Dashboard JSON files nên được đặt ở thư mục ```{{ node_custom_config }}/grafana/dashboards/```. Việc sử dụng thư mục con cũng được hỗ trợ khi dùng 1 custom ```provisioning.yml``` file. Dashboards sẽ được import vào Grafana Dashboards ở folder 'General' theo mặc định

Grafana provisioner config có thể được thay đổi bằng cách đặt ```provisioning.yml``` thành ```{{ node_custom_config }}/grafana```

Để biết thêm thông tin chi tiết, hãy xem thêm về Dashboards provider ở link bên trên.