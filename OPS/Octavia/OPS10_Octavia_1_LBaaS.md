# Load Balancer as a Service (LBaaS)

Networking service cung cấp 1 tính năng load balancer gọi là **LBaaS v2** thông qua plugin ```neutron-lbaas```.

LBaaS v2 thêm vào ý tưởng về các listeners so với LBaaS v1. LBaaS v2 cho phép ta cấu hình nhiều listener ports trên 1 địa chỉ IP load balancer.

Có 2 cách triển khai LBaaS v2. Thứ nhất là 1 triển khai dựa trên agent với HAProxy. Các Agent sẽ xử lý cấu hình HAProxy và quản lý HAProxy daemon. Cách thứ 2 là sử dụng **Octavia**, thành phần này có 1 API và worker processes riêng biệt giúp xây dựng Load Balancer bên trong VMs trên hypervisors mà được quản lý bởi Compute service. Và rõ ràng là bạn sẽ không cần 1 agent cho Octavia.

**Lưu ý:** LBaaS v1 đã được loại bỏ từ bản phát hành Newton

## LBaaS v2 Concepts

LBaaS v2 có 1 vài ý tưởng mà chúng ta nên nắm được như sau:

![](./images/Octavia_1.png)

- **Load Balancer:** Load Balancer sử dụng 1 neutron network port và có 1 địa chỉ IP từ 1 subnet
- **Listener:** Load Balancer có thể lắng nghe từ requests trên nhiều ports. Mỗi port lại được chỉ định bởi 1 listener
- **Pool:** 1 pool giữ 1 danh sách thành viên mà phục vụ nội dung thông qua LB
- **Member:** Các thành viên là những máy chủ mà phục vụ traffic đằng sau 1 LB. Mỗi member được chỉ định bởi 1 IP address và port nó sử dụng để phục vụ traffic
- **Health monitor:** Các thành viên có thể không khả dụng vào 1 thời điểm bất kỳ, health monitors có trách nhiệm theo dõi điều này và định hướng traffic tránh khỏi các thành viên đó. Heath monitors cũng được tổ chức chung với các pool

LBaaS v2 có nhiều triển khai thông qua nhiều service plugins khác nhau. Tuy vậy 2 cách triển khai phổ biến nhất là sử dụng agent hoặc Octavia. Cả 2 cách này đều sử dụng LBaaS v2 API.

## Configurations

### Configuring LBaaS v2 with an agent

1. Thêm LBaaS v2 service plugin vào ```service_plugins``` của ```/etc/neutron/neutron.conf```. Các plugin trong danh sách được liệt kê cách nhau bởi dấu phẩy:

```sh
service_plugins = [existing service plugins],neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2
```

2. Thêm LBaaS v2 service provider vào phần ```[service_providers]``` của ```/etc/neutron/neutron_lbaas.conf```

```sh
service_provider = LOADBALANCERV2:Haproxy:neutron_lbaas.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default
```

Nếu bạn có service provider nào đã tồn tại cho các networking service plugins khác, như VPNaaS hay FWaaS, bạn chỉ cần đơn giản thêm 1 dòng ```service_provider``` khác bên trong ```[service_providers]```

3. Chọn driver mà quản lý virtual interfaces trong ```/etc/neutron/lbaas_agent.ini```

```sh
[DEFAULT]
interface_driver = INTERFACE_DRIVER
```
Thay thế ```INTERFACE_DRIVER``` với interface driver mà layer-2 agent bạn đang sử dụng. Ví dụ như ```openvswitch``` cho Open vSwitch hay ```linuxbridge``` cho Linux Bridge.

4. Chạy ```neutron-lbaas``` database migration

```sh
neutron-db-manage --subproject neutron-lbaas upgrade head
```

5. Nếu bạn đã triển khai LBaaS v1, hãy dừng LBaaS v1 agent vì 2 phiên bản này không thể cùng hoạt động 1 lúc được

6. Khởi động LBaaS v2 agent

```sh
neutron-lbaasv2-agent \
  --config-file /etc/neutron/neutron.conf \
  --config-file /etc/neutron/lbaas_agent.ini
```

7. Khởi động lại network service để kích hoạt cấu hình mới. Giờ bạn đã sẵn sàng để tạo LB với LBaaS v2 agent.

```sh
systemctl restart neutron-server neutron-linuxbridge-agent neutron-l3-agent
```


### Configuring LBaaS v2 with Octavia

Octavia cung cấp thêm các tính năng cho Load Balancers, bao gồm sử dụng 1 compute driver để build instances mà vận hành như 1 Load Balancer.

Cách cài đặt Octavia sẽ được đề cập ở bài viết khác. Nếu bạn đã có Octavia cài đặt và cấu hình bên trong môi trường của mình, bạn có thể cấu hình Network service để sử dụng Octavia

1. Thêm LBaaS v2 service plugin vào ```service-plugins``` trong ```/etc/neutron/neutron.conf```. Lưu ý các plugin cách nhau bởi dấu phẩy:

```sh
service_plugins = [existing service plugins],neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2
```

2. Thêm Octavia service provider vào cấu hình ```service_provider``` bên trong ```[service_providers]``` của ```/etc/neutron/neutron_lbaas.conf```:

```sh
service_provider = LOADBALANCERV2:Octavia:neutron_lbaas.drivers.octavia.driver.OctaviaDriver:default
```

Hãy chắc chắn là LBaaS v1 và v2 service provider đã được loại bỏ khỏi phần ```[service_providers]``` do chúng không thể sử dụng cùng với Octavia.

3. Khởi động lại Network service để kích hoạt cấu hình mới:

```sh
systemctl restart neutron-server neutron-linuxbridge-agent neutron-l3-agent
```

### Thêm LBaaS panels lên Dashboard

Dashboard panels sử dụng để quản lý LBaaS v2 có thể cài đặt từ bản phát hành Mikata:

1. Clone [neutron-lbaas-dashboard repository](https://git.openstack.org/cgit/openstack/neutron-lbaas-dashboard/) và check out release branch mà khớp với phiên bản Dashboard được cài đặt:

```sh
git clone https://git.openstack.org/openstack/neutron-lbaas-dashboard
cd neutron-lbaas-dashboard
git checkout OPENSTACK_RELEASE
```

2. Cài đặt Dashboard panel plugin

```sh
python setup.py install
```

3. Copy tệp ```_1481_project_ng_loadbalancersv2_panel.py``` từ đường dẫn ```neutron-lbaas-dashboard/enabled``` vào trong đường dẫn Dashboard ```openstack_dashboard/local/enabled```

4. Kích hoạt plugin trong Dashboard bằng cách chỉnh sửa tệp ```local_settings.py``` và cài đặt ```enable_lb``` thành ```True``` trong ```OPENSTACK_NEUTRON_NETWORK``` dictionary

5. Nếu Dashboard được cấu hình để nén static files cho hiệu suất tốt hơn (thông thường đặt qua ```COMPRESS_OFFLINE``` trong ```local_settings.py```), tối ưu hiệu suất static files một lần nữa:

```sh
./manage.py collectstatic
./manage.py compress
```

6. Restart Apache để kích hoạt panel mới:

```sh
systemctl restart apache2 
```

Sau khi đăng nhập vào Dashboard, hãy chọn ```Project``` => ```Network``` => ```Load Balancers```

## LBaaS v2 operations

LBaaS v2 sử dụng lệnh neutron để thao tác.

### Building an LBaaS v2 load balancer

1. Bắt đầu bằng việc tạo 1 load balancer trên 1 network. Ở ví dụ này, ```private``` network là 1 network cô lập với 2 web server instances:

```sh
neutron lbaas-loadbalancer-create --name test-lb private-subnet
```

2. Ta có thể kiểm tra loadbalancer status và IP address với lệnh

```sh
neutron lbaas-loadbalancer-show <LB-name>
```

```sh
neutron lbaas-loadbalancer-show test-lb
+---------------------+------------------------------------------------+
| Field               | Value                                          |
+---------------------+------------------------------------------------+
| admin_state_up      | True                                           |
| description         |                                                |
| id                  | 7780f9dd-e5dd-43a9-af81-0d2d1bd9c386           |
| listeners           | {"id": "23442d6a-4d82-40ee-8d08-243750dbc191"} |
|                     | {"id": "7e0d084d-6d67-47e6-9f77-0115e6cf9ba8"} |
| name                | test-lb                                        |
| operating_status    | ONLINE                                         |
| provider            | haproxy                                        |
| provisioning_status | ACTIVE                                         |
| tenant_id           | fbfce4cb346c4f9097a977c54904cafd               |
| vip_address         | 192.0.2.22                                     |
| vip_port_id         | 9f8f8a75-a731-4a34-b622-864907e1d556           |
| vip_subnet_id       | f1e7827d-1bfe-40b6-b8f0-2d9fd946f59b           |
+---------------------+------------------------------------------------+
```

3. Update security group để cho phép traffic tới được load balancer mới này. Tạo 1 security group mới với ingress rules để cho phép traffic vào LB mới. Neutron port cho LB được thể hiện ở ```vip_port_id``` bên trên.

Tạo 1 security group và rules cho phép TCP port 80, TCP port 443, và tất cả ICMP traffic:

```sh
neutron security-group-create lbaas
neutron security-group-rule-create \
  --direction ingress \
  --protocol tcp \
  --port-range-min 80 \
  --port-range-max 80 \
  --remote-ip-prefix 0.0.0.0/0 \
  lbaas
neutron security-group-rule-create \
  --direction ingress \
  --protocol tcp \
  --port-range-min 443 \
  --port-range-max 443 \
  --remote-ip-prefix 0.0.0.0/0 \
  lbaas
neutron security-group-rule-create \
  --direction ingress \
  --protocol icmp \
  lbaas
```

Áp security group vào LB's network port sử dụng ```vip_port_id``` bằng lệnh:

```sh
neutron port-update \
  --security-group lbaas \
  9f8f8a75-a731-4a34-b622-864907e1d556
```

### Adding an HTTP listener

1. Với load balancer, ta có thể thêm 1 listener cho plaintext tại port 80:

```sh
neutron lbaas-listener-create \
  --name test-lb-http \
  --loadbalancer test-lb \
  --protocol HTTP \
  --protocol-port 80
```

2. Đảm bảo là LB có thể ping được trước khi thực hiện thao tác tiếp theo:

3. Ta có thể bắt đầu build 1 pool và thêm thành viên vào pool để phục vụ HTTP content trên port 80. Trong VD này, web server là ```192.0.2.16``` và ```192.0.2.17```:

```sh
neutron lbaas-pool-create \
  --name test-lb-pool-http \
  --lb-algorithm ROUND_ROBIN \
  --listener test-lb-http \
  --protocol HTTP
neutron lbaas-member-create \
  --name test-lb-http-member-1 \
  --subnet private-subnet \
  --address 192.0.2.16 \
  --protocol-port 80 \
  test-lb-pool-http
neutron lbaas-member-create \
  --name test-lb-http-member-2 \
  --subnet private-subnet \
  --address 192.0.2.17 \
  --protocol-port 80 \
  test-lb-pool-http
```

4. Ta có thể ```curl``` vào LB's IP address để kiểm tra kết nối, ví dụ:

```sh
$ curl 192.0.2.22
web2
$ curl 192.0.2.22
web1
$ curl 192.0.2.22
web2
$ curl 192.0.2.22
web1
```

Trong ví dụ này, LB sử dụng thuật toán round robin và do đó traffic thay đổi tuần tự giữa 2 backend

5. Ta có thể thêm 1 health monitor để giúp traffic sẽ không được điều phối tới server mà có trạng thái không tốt

```sh
neutron lbaas-healthmonitor-create \
  --name test-lb-http-monitor \
  --delay 5 \
  --max-retries 2 \
  --timeout 10 \
  --type HTTP \
  --pool test-lb-pool-http
```

Trong ví dụ này, health monitor loại bỏ server khỏi pool nếu nó fail health check 2 lần (mỗi lần cách nhau 5s). Khi server phục hồi trở lại và bắt đầu phản hồi health check, nó sẽ tự động được thêm vào pool.

### Adding an HTTPS listener

Ta có thể thêm listener khác trên port 443 cho HTTPS traffic. LBaaS v2 cung cấp giả mã SSL/TLS ở load balancer, nhưng ví dụ này thực hiện 1 cách tiếp cận đơn giản hơn và cho phép các kết nối mã hóa được giải mã ở server thành viên.

1. Bắt đầu bằng việc tạo 1 listener, gắn 1 pool, và thêm vào các thành viên:

```sh
neutron lbaas-listener-create \
  --name test-lb-https \
  --loadbalancer test-lb \
  --protocol HTTPS \
  --protocol-port 443
neutron lbaas-pool-create \
  --name test-lb-pool-https \
  --lb-algorithm LEAST_CONNECTIONS \
  --listener test-lb-https \
  --protocol HTTPS
neutron lbaas-member-create \
  --name test-lb-https-member-1 \
  --subnet private-subnet \
  --address 192.0.2.16 \
  --protocol-port 443 \
  test-lb-pool-https
neutron lbaas-member-create \
  --name test-lb-https-member-2 \
  --subnet private-subnet \
  --address 192.0.2.17 \
  --protocol-port 443 \
  test-lb-pool-https
```

2. Thêm vào 1 health monitor:

```sh
neutron lbaas-healthmonitor-create \
  --name test-lb-https-monitor \
  --delay 5 \
  --max-retries 2 \
  --timeout 10 \
  --type HTTPS \
  --pool test-lb-pool-https
```

### Associating a floating IP address

Load balancers được triển khai với 1 public hoặc provider network mà truy cập được từ internet thì không cần 1 floating IP. Các client bên ngoài có thể trực tiếp truy cập Virtual IP (VIP) của những load balancers đó.

Mặc dù vậy, load balancers được triển khai trên private hoặc isolated network cần 1 floating IP nếu chúng muốn cho phép client bên ngoài truy cập vào được. Để làm vậy, ta phải có 1 router ở giữa private và public network và 1 IP khả dụng.

Ta có thể sử dụng ```neutron lbaas-loadbalancer-show``` command để xác định ```vip_port_id```. ```vip_port_id``` là ID của network port mà được cấp cho Load balancer. Ta có thể cấp 1 floating trống đến LB này sử dụng ```neutron floatingip-associate```

```sh
neutron floatingip-associate <FLOATINGIP_ID> <LOAD_BALANCER_PORT_ID>
```

### Setting quotas for LBaaS v2

Quotas có thể được áp xuống để giới hạn số lượng ```Load balancer``` và ```Load balancer pool```. Mặc định thì cả 2 tham số trên sẽ là ```10```.

Bạn có thể thay đổi quotas sử dụng lệnh ```neutron quota-update```

```sh
neutron quota-update --tenant-id <TENANT_UUID> --loadbalancer 25
neutron quota-update --tenant-id <TENANT_UUID> --pool 50
```

**Lưu ý:** Thiết lập ```-1``` sẽ tắt quota cho tenant

### Kiểm tra thông số Load Balancer

LBaaS v2 agent tổng hợp 4 loại thông số với mỗi LB mỗi 6s. Người dùng có thể truy vấn thông số này bằng lệnh sau:

```sh
neutron lbaas-loadbalancer-stats test-lb
+--------------------+----------+
| Field              | Value    |
+--------------------+----------+
| active_connections | 0        |
| bytes_in           | 40264557 |
| bytes_out          | 71701666 |
| total_connections  | 384601   |
+--------------------+----------+
```

Con số ```active_connections``` là tổng số kết nối đang có ở thời điểm lệnh được sử dụng. 3 thông số còn lại là tổng số kể từ lần khởi động Load Balancer gần nhất.