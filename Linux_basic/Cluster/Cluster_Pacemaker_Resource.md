# Tổng quan về Resource trong Pacemaker

## Định nghĩa

Resource hay tài nguyên là dịch vụ được pacemaker bảo đảm sự sẵn sàng. Resource có nhiều loại, bao gồm các dịch vụ cơ bản (http, ssh,...) tới những dịch vụ phức tạp như các group resource, clone resource.

Tất cả dịch vụ cơ bản như SSH,... đều sở hữu ```resource agent```, nó là module mở rộng, trừu tượng hóa dịch vụ cung cấp thành đối tượng cho phép cluster pacemaker có thể quản trị. Các hoạt động quản trị cơ bản bao gồm: ```start```, ```stop```, ```monitor```

## Các loại Resource cơ bản

Pacemaker hỗ trợ nhiều loại resource khác nhau

### OCF (Open Cluster Framework)

Tiêu chuẩn quy ước của Linux Standard Base cho các script. Quy chuẩn các đối số đầu vào (gọi là **support parameters**), các tham số tự định nghĩa (**self-describing**), khả năng tùy biến, mở rộng (extensible). Các quy ước của OCF tập trung vào các ```exit code``` trả lại bởi các thao tác start, stop, monitor,.... Các đối số của OCF được truyền vào thông qua môi trường thực thi với khóa ```OCF_RESKEY```

### LSB (Linux Standard Base)

Tiêu chuẩn được cung cấp, hỗ trợ trong nhiều bản phân phối Linux, các tài nguyên thường được tìm thấy trong ```/etc/init.d```

### Systemd

Tiêu chuẩn mới trong các bản phân phối Linux, thay thế thôi ```SysV```. Pacemaker có thể quản trị tất cả dịch vụ ```Systemd``` nếu chúng tồn tại. ```Systemd``` quản trị dịch vụ thông qua ```unit files```

**Lưu ý:** nếu sử dụng Pacemaker quản trị tiến trình ```systemd``` thì không được để dịch vụ tự khởi động cùng hệ thống (hay enable dịch vụ)

### Upstart

Tiêu chuẩn mới trong các bản phân phối Linux, thay thế cho ```SysV```. Pacemaker có thể quản trị tất cả dịch vụ ```Upstart``` nếu chúng tồn tại. ```Upstart``` quản trị dịch vụ thông qua ```jobs```

### Service

Vì hệ thống có nhiều loại tiến trình quản trị dịch vụ (systemd, upstart, LSB). Pacemaker hỗ trợ kiểu ```service```, cho phép tự động phát hiện kiểu dữ liệu của dịch vụ (systemd, upstart, lsb) để quản trị dễ dàng hơn

### STONITH

STONITH / Fencing: là kỹ thuật dành cho Fencing, đã nói ở các bài trước

### Nagios Plugins

Giám sát tài nguyên từ xa thông qua ```Nagios Plugins``` trong trường hợp các dịch vụ là các máy ảo, các dịch vụ bên trong máy ảo

## Tham số cơ bản trên Resource

Các tham số cơ bản:
- ID: Tên resource 
- Class Kiểu scripts (OCF, service, upstart, systemd, LSB, STONITH)
- Type: Tên dịch vụ quản trị được quản trị (Apache, SSH,...)

```sh
[root@node1 ~]# crm_resource --resource Web_Cluster-clone --query-xml
 Clone Set: Web_Cluster-clone [Web_Cluster] (unique)
     Web_Cluster:0	(ocf::heartbeat:apache):	Started node3
     Web_Cluster:1	(ocf::heartbeat:apache):	Started node2
     Web_Cluster:2	(ocf::heartbeat:apache):	Started node1
xml:
<clone id="Web_Cluster-clone">
  <primitive class="ocf" id="Web_Cluster" provider="heartbeat" type="apache">
    <instance_attributes id="Web_Cluster-instance_attributes">
      <nvpair id="Web_Cluster-instance_attributes-configfile" name="configfile" value="/etc/httpd/conf/httpd.conf"/>
    </instance_attributes>
    <operations>
      <op id="Web_Cluster-monitor-interval-20s" interval="20s" name="monitor"/>
      <op id="Web_Cluster-start-interval-0s" interval="0s" name="start" timeout="40s"/>
      <op id="Web_Cluster-stop-interval-0s" interval="0s" name="stop" timeout="60s"/>
    </operations>
  </primitive>
  <meta_attributes id="Web_Cluster-clone-meta_attributes">
    <nvpair id="Web_Cluster-clone-meta_attributes-globally-unique" name="globally-unique" value="true"/>
  </meta_attributes>
</clone>
```

## Tham số tùy chọn trên Resource

Sử dụng tùy chọn mở rộng cho phép định nghĩa cách cluster quản lý các resource. Bổ sung tham số thông qua tùy chọn ```--meta``` thuộc ```crm_resource``` 

Các tham số cần chú ý:
- ```priority``` (default = 0): Nếu tất cả resource không thể sẵn sàng, cluster sẽ ngừng các resource có độ ưu tiên thấp, bảo đảm resource có độ ưu tiên cao sẵn sàng
- ```target-role``` (default = started): trạng thái mong muốn, cluster sẽ cố gắng giữ trạng thái này trên resource
  - ```Stopped```: Buộc tài nguyên dừng hoạt động
  - ```Started```: Cho phép tài nguyên hoạt động (Trong trường hợp cấu hình multistate dạng Active - Passive)
  - ```Master```: Cho phép tài nguyên hoạt động nếu trong trạng thái thích hợp
- ```is-managed``` (default = TRUE): Cluster cố gắng start hoặc stop dịch vụ (mặc định tự start)
- ```resource-stickiness``` (default = 0): Ràng buộc vị trí tài nguyên
- ```migration-threshold``` (default = INFNITY): Nếu quá nhiều lỗi xảy ra trên 1 node, tài nguyên sẽ di chuyển sang node khác
- ```multiple-active``` (default = stop_start): Phản ứng khi phát nhiều một resource tương ứng đang chạy trên node khác
  - ```block```: Quy định resource không được quản lý. Sẽ tạm dừng hoạt động resource và đưa ra cảnh báo
  - ```stop_only```: Dừng tất cả các trường hợp hoạt động
  - ```stop_start```: Dừng tất cả các trường hợp hoạt động và thử khởi động lại

## Tham số vận hành Resource

Các tham số cần lưu ý trong quá trình vận hành Resource:
- ```id```: Định danh resource
- ```name```: Hành động thực hiện (```monitor```, ```start```, ```stop```)
- ```interval```: Tần số thực hiện hành động (mặc định = 0)
- ```timeout```: Thời gian chờ tối đa nếu xảy ra sự cố
- ```on-fail```: Thao tác nếu phát hiện sự cố
  - ```ignore```: Không phản ứng, bỏ qua lỗi
  - ```block```: Không thực hiện thêm bất kỳ hoạt động nào khác trên resource
  - ```stop```: Dừng hoạt động resource, không khởi động resource trên bất kỳ node nào khác
  - ```restart```: Khởi động lại resource
  - ```fence```: STONITH trên node mà resource đó bị lỗi
  - ```standby```: Di chuyển tất cả các resource ra khỏi node xảy ra sự cố
- ```enable```: Nếu thiết lập ```false``` thì giám sát tài nguyên sẽ được bỏ qua

Cấu trúc:

```sh
pcs resource create <Tên resource> <Tham số 1> <Tham số 2 ..> op <tham số vận hành>
```

VD:

```sh
pcs resource create Virtual_IP IPaddr2 ip=10.10.10.89 cidr_netmask=24 op monitor interval=30s

# Mô tả
[root@node1 ~]# pcs resource show Web_Cluster-clone
 Clone: Web_Cluster-clone
  Meta Attrs: globally-unique=true # Metadata
  Resource: Web_Cluster (class=ocf provider=heartbeat type=apache)
   Attributes: configfile=/etc/httpd/conf/httpd.conf # Tham số tài nguyên
   Operations: monitor interval=20s (Web_Cluster-monitor-interval-20s) # Tham số vận hành
               start interval=0s timeout=40s (Web_Cluster-start-interval-0s)
               stop interval=0s timeout=60s (Web_Cluster-stop-interval-0s)
```

