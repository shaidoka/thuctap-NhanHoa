# Ceilometer - Data collection

Trách nhiệm chính của Telemetry trong OpenStack là thu thập thông tin về hệ thống mà có thể được sử dụng bởi billing system hoặc analytic tool

Ceilometer data có thể được lưu trữ trong định dạng mẫu (samples) hoặc sự kiện (events) trong các database được hỗ trợ (khuyến khích là Gnocchi)

Các phương thức thu thập dữ liệu bao gồm:

- **Notifications**: Xử lý các cảnh báo từ các dịch vụ OpenStack khác, bằng cách lấy messages từ hệ thống message queue đã cấu hình
- **Polling**: Thu thập thông tin trực tiếp từ hypervisor hoặc bởi APIs của các dịch vụ OpenStack khác

## Notifications

Tất cả các dịch vụ OpenStack đều gửi notifications về các hành động đã thực thi hoặc trạng thái hệ thống của chúng. Một vài notifications mang thông tin mà có thể đo lường được. Ví dụ, CPU time của 1 VM instance được tạo bởi OpenStack Compute service.

Notification agent chịu trách nhiệm cho việc thu thập các notification này. Thành phần này sử dụng message từ message bus và chuyển hóa notification thành events và tính toán/đo lường mẫu (samples).

Mặc định, notification agent được cấu hình để xây dựng cả events và samples. Để enable selective data models, hãy thiết lập pipelines yêu cầu sử dụng tùy chọn *pipelines* bên dưới *[notification]* section.

Thêm vào đó, notification agent chịu trách nhiệm gửi đến bất kỳ publisher target được hỗ trợ như gnocchi hoặc panko. Những service này giữ dữ liệu trong databases đã cấu hình.

Các OpenStack service khác nhau đưa ra một vài notifications về nhiều loại events mà có thể xảy ra trong hệ thống khi hoạt động trong trạng thái bình thường. Không phải tất cả những notifications này đều được sử dụng bởi Telemetry service, vì mục tiêu là chỉ capture các events có thể tính tiền (billable events) và notications mà có thể sử dụng cho mục đích monitoring hoặc profiling. Notifications handled nằm dưới namespace ```ceilometer.sample.endpoint```.

### Meter definitions

Telemetry service thu thập 1 tập các dữ liệu đo lường bằng cách lọc các notifications đưa ra bởi các dịch vụ OpenStack khác. Ta có thể tìm kiếm các định nghĩa dữ liệu đo lường (meter definitions) trong 1 file cấu hình riêng biệt, gọi là ```ceilometer/data/meter.d/meters.yaml```. Điều này cho phép người quản trị/vận hành có thể thêm các meter mới vào Telemetry project bằng cách cập nhật ```meters.yaml``` mà không phải thay đổi bất kỳ dòng code nào.

Nó cũng hỗ trợ tải nhiều meter definition files và cho phép người dùng thêm các meter definitions của họ vào các files với nhiều loại metrics khác nhau vào ```/etc/ceilometer/meters.d```

1 meter definition tiêu chuẩn sẽ có dạng như sau:

```sh
---
metric:
  - name: 'meter name'
    event_type: 'event name'
    type: 'type of meter eg: gauge, cumulative or delta'
    unit: 'name of unit eg: MB'
    volume: 'path to a measurable value eg: $.payload.size'
    resource_id: 'path to resource id eg: $.payload.id'
    project_id: 'path to project id eg: $.payload.owner'
    metadata: 'additional key-value data describing resource'
```

Định nghĩa bên trên cho thấy 1 meter definition đơn giản với 1 vài trường, trong đó ```name```, ```event_type```, ```type```, ```unit```, và ```volume``` là bắt buộc. Nếu có 1 metric khớp với loại event trên, samples sẽ được sinh ra cho meter.

File ```meters.yaml``` chứa các định nghĩa sample cho tất cả các meters mà Telemetry đang thu thập từ notifications. Giá trị của mỗi trường được chỉ định bằng cách sử dụng JSON path để tìm kiếm trường giá trị chính xác mà bạn cần để biết được dạng của notification. Các giá trị mà cần để được tìm kiếm trong notification message được thiết lập với 1 JSON path bắt đầu với ```$```. Ví dụ, nếu bạn cần thông tin ```size``` từ payload, bạn có thể định nghĩa nó như này ```$.playload.size```

1 notification message có thể chứa nhiều meters. Bạn có thể sử dụng ```*``` trong meter definition để capture tất cả meters và khởi tạo samples tương ứng. Bạn có thể sử dụng wildcards như ví dụ dưới đây:

```sh
---
metric:
  - name: $.payload.measurements.[*].metric.[*].name
    event_type: 'event_name.*'
    type: 'delta'
    unit: $.payload.measurements.[*].metric.[*].unit
    volume: payload.measurements.[*].result
    resource_id: $.payload.target
    user_id: $.payload.initiator.id
    project_id: $.payload.initiator.project_id
```

Trong ví dụ trên, trường ```name``` là 1 JSON path khớp với 1 danh sách các meter names đã định nghĩa trong notification message.

Ta có thể sử dụng complex operation trên JSON paths. Trong ví dụ sau đây, ```volume``` và ```resource_id``` thực hiện 1 phép toán và 1 phép nối chuỗi ký tự:

```sh
metric:
- name: 'compute.node.cpu.idle.percent'
  event_type: 'compute.metrics.update'
  type: 'gauge'
  unit: 'percent'
  volume: payload.metrics[?(@.name='cpu.idle.percent')].value * 100
  resource_id: $.payload.host + "_" + $.payload.nodename
```

Ta có thể dùng plugin ```timedelta``` để tính toán khoảng cách (tính bằng giây) giữa 2 trường ```datetime``` từ 1 notification

```sh
---
metric:
- name: 'compute.instance.booting.time'
  event_type: 'compute.instance.create.end'
 type: 'gauge'
 unit: 'sec'
 volume:
   fields: [$.payload.created_at, $.payload.launched_at]
   plugin: 'timedelta'
 project_id: $.payload.tenant_id
 resource_id: $.payload.instance_id
```

## Polling

Dịch vụ Telemetry hướng đến việc lưu trữ 1 bức tranh toàn cảnh về cơ sở hạ tầng. Mục tiêu này cần nhiều thông tin hơn những gì được cung cấp bởi events và notifications của mỗi service. Một vài thông tin không được đưa ra trực tiếp, như tài nguyên sử dụng của VM instances.

Do đó, Telmetry sử dụng 1 phương thức khác để thu thập các dữ liệu này bằng cách polling cơ sở hạ tầng bao gồm APIs của nhiều dịch vụ khác nhau của OpenStack và nhiều assets khác, như hypervisor chẳng hạn. Để giải quyết vấn đề này, Telemetry sử dụng 1 kiến trúc dựa trên agent cho việc thu thập dữ liệu.

### Configuration

Polling rules được định nghĩa bởi tệp ```polling.yaml```. Nó định nghĩa pollsters để enable và khoảng cách giữa các lần poll.

Mỗi cấu hình nguồn đóng gói meter name sao cho khớp với entry point của pollster. Nó cũng bao gồm: polling interval, resource enumeration hoặc discovery (optional)

Tất cả samples tạo ra bởi polling đều đặt trên hàng đợi để được xử lý bởi cấu hình pipeline đã tải trong notification agent

Định nghĩa polling có thể giống như sau:

```sh
---
sources:
  - name: 'source name'
    interval: 'how often the samples should be generated'
    meters:
      - 'meter filter'
    resources:
      - 'list of resource URLs'
    discovery:
      - 'list of discoverers'
```

Polling plugins được gọi theo mỗi ```source```, thứ mà có tham số ```meters``` khớp với tên của meter plugin. Matching logic function của nó tương đồng với pipeline filtering.

Tham số ```resources``` là tùy chọn, nó bao gồm 1 danh sách các URLs tài nguyên tĩnh. 1 danh sách tổng hợp của tất cả các tài nguyên tĩnh đã định nghĩa được chuyển qua pollster riêng biệt cho polling.

Một tham số tùy chọn khác là ```discovery```, nó bao gồm 1 danh sách các *discoverers*. Những discoverers này có thể được sử dụng để linh hoạt phát hiện các tài nguyên có thể được poll bởi pollster.

Nếu cả ```resources``` và ```discovery``` được thiết lập, danh sách tài nguyên cuối cùng được chuyển cho pollster sẽ là tổng hợp của cả 2 loại này.

### Agents

Có 3 loại agents hỗ trợ phương thức polling: ```compute agent```, ```central agent```, và ```IPMI agent```. Dù vậy, tất cả loại polling agents đều là ```ceilometer-polling``` agent, trừ việc chúng tải các loại plugin khác nhau (hay gọi là pollster) từ nhiều namespace khác nhau để thu thập dữ liệu. Phần dưới đây đưa thêm thông tin liên quan đến kiến trúc và chi tiết cấu hình của những thành phần này.

Chạy ```ceilometer-agent-compute``` cũng tương đồng với:

```sh
ceilometer-polling --polling-namespaces compute
```

Chạy ```ceilometer-agent-central``` cũng tương đồng với:

```sh
ceilometer-polling --polling-namespaces central
```

Chạy ```ceilometer-agent-ipmi``` cũng tương đồng với:

```sh
ceilometer-polling --polling-namespaces ipmi
```

#### Compute agent

Agent chịu trách nhiệm cho việc thu thập dữ liệu resource usage của VM instances trên từng compute node riêng. Phương thức này cần 1 tương tác gần hơn với hypervisor, do đó 1 loại agent riêng biệt được đặt tại host machine để thu thập các dữ liệu liên quan là cần thiết.

1 compute agent instance phải được cài đặt trên mỗi và mọi compute node, hướng dẫn cài đặt có thể được tìm kiếm ở đây: [Install and Configure Compute Services](https://docs.openstack.org/ceilometer/latest/install/install-compute.html#install-compute)

Compute agent sử dụng API của hypervisor đã cài đặt trên compute hosts. Do đó, các meters được hỗ trợ có thể khác trên các virtualization backend khác nhau.

Danh sách các meters được hỗ trợ có thể xem tại đây: [OpenStack Compute](https://docs.openstack.org/ceilometer/latest/admin/telemetry-measurements.html#telemetry-compute-meters).

#### Central agent

Agent này chịu trách nhiệm polling public REST APIs để thu thập thêm thông tin về OpenStack resource mà không đưa lên trên notification.

Một vài service mà được poll với agent này là: Networking, Object Storage, Block Storage.

Để cài đặt và cấu hình service này, hãy xem thêm tại [đây](https://docs.openstack.org/ceilometer/latest/install/install-base-rdo.html#install-rdo).

Ngoài ra, Ceilometer cũng có 1 tập các polling agent mặc định, người quản trị có thể thêm pollster mới vào thông qua dynamic pollster subsystem [Introduction to dynamic pollster subsystem](https://docs.openstack.org/ceilometer/latest/admin/telemetry-dynamic-pollster.html#telemetry-dynamic-pollster)

#### IPMI agent

Agent này chịu trách nhiệm thu thập IPMI sensor data từ Intel Node Manager data trên từng compute nodes. Agent này cần 1 IPMI node thích hợp với công cụ ipmitool được cài đặt.

1 IPMI agent instance có thể được cài đặt trên mỗi và mọi node với IPMI support, trừ khi node đó được quản lý bởi Baremetal service và ```conductor.send_sensor_data``` option đặt thành ```true``` trong dịch vụ Baremetal. 