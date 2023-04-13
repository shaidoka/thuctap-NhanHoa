# EndpointSlices

EndpointSlices cung cấp một cách đơn giản để theo dõi các endpoint trong K8s cluster. Chúng cung cấp một giải pháp thay thế linh hoạt và có khả năng mở rộng so với Endpoints.

EndpointSlices cung cấp một cách đơn giản để theo dõi các endpoint trong K8s cluster. Chúng cung cấp một giải pháp thay thế linh hoạt và có khả năng mở rộng hơn so với Endpoint 

## Động lực

Endpoint API đã cung cấp 1 cách đơn giản và rõ ràng trong việc theo dõi các network endpoint trong K8s. Tuy nhiên, khi K8s cluster và Service trở nên lớn hơn thì các giới hạn của API đó càng trở nên rõ ràng hơn. Đáng chú ý nhất là nó bao gồm các thách thức trong việc mở rộng (scale) lên một số lượng lớn các network endpoint.

Vì tất cả các network endpoint cho Service được lưu trong 1 tài nguyên Endpoint duy nhất nên tài nguyên đó có thể rất lớn. Điều này gây ảnh hưởng đến hiệu năng của các thành phần K8s (đáng chú ý là master control plane) và kết quả là 1 lượng lớn network traffic cần được xử lý khi endpoint bị thay đổi. Endpoint Slices giúp ta giảm bớt các vấn đề như vậy cũng như cung cấp 1 nền tảng có thể mở rộng thêm các tính năng bổ sung như là **topology routing**.

## Tài nguyên EndpointSlice

Trong K8s, 1 EndpointSlices chứa các tham chiếu đến 1 tập các network endpoint. EndpointSlice Controller sẽ tự động tạo ra các EndpointSlices cho 1 K8s Service khi 1 selector được chỉ định. Các EndpointSlice này sẽ bao gồm các tham chiếu đến bất kỳ pod nào khớp với selector của Service. EndpointSlice nhóm các network endpoint lại với nhau bằng 1 tổ hợp Service và Port duy nhất.

Ví dụ bên dưới là tài nguyên EndpointSlice cho K8s service có tên là ```example```:

```sh
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: example-abc
  labels:
    kubernetes.io/service-name: example
addressType: IPv4
ports:
  - name: http
    protocol: TCP
    port: 80
endpoints:
  - addresses:
    - "10.1.2.3"
    conditions:
      ready: true
    nodeName: node-1
    zone: us-west2-a
```

Mặc định, các EndpointSlice sẽ được quản lý bởi EndpointSlice Controller và sẽ không có nhiều hơn 100 endpoint. Dưới tỉ lệ này, EndpointSlice cần được ánh xạ 1:1 với Endpoint và Service và có hiệu năng tương tự.

EndpointSlices có thể hoạt động như là 1 nguồn tin cậy cho kube-proxy khi nó cần route traffic nội bộ. Khi được bật, chúng nên cung cấp 1 sự cải thiện về hiệu năng cho các Service về số lượng endpoint lớn.

### 1. Address Type

EndpointSlices hỗ trợ 3 loại Address
- IPv4
- IPv6
- FQDN (Fully Qualified Domain Name)

### 2. Topology

Mỗi endpoint trong EndpointSlice có thể chứa thông tin liên quan đến topology. Thông tin này được sử dụng để chỉ ra endpoint ở đâu, thông tin về Node, zone và region tương ứng. Khi các giá trị là khả dụng, các Topology label sau sẽ được thiết lập bởi EndpointSlice Controller
- ```kubernetes.io/hostname``` - Tên của Node mà endpoint này đang nằm
- ```topology.kubernetes.io/zone``` - Zone mà endpoint này thuộc về
- ```topology.kubernetes.io/region``` - Region mà endpoint này thuộc về

Các giá trị của các label này được lấy từ các tài nguyên được liên kết với mỗi endpoint trong một slice. Label ```hostname``` đại diện cho giá trị của trường ```NodeName``` trên Pod tương ứng. Các label ```zone``` và ```region``` biểu thị giá trị của các label có cùng tên trên Node tương ứng.

### 3. Quản lý

Mặc định, EndpointSlices được tạo ra và quản lý bởi EndpointSlice Controller. Có nhiều trường hợp sử dụng khác cho EndpointSlices, chẳng hạn như khi triển khai service mesh có thể dẫn đến các thực thể hoặc controller khác sẽ quản lý các EndpointSlices bổ sung. Để đảm bảo rằng nhiều thực thể có thể quản lý EndpointSlice mà không can thiệp lẫn nhau, label ```endpointslice.kubernetes.io/managed-by``` được sử dụng để chỉ ra thực thể sẽ quản lý EndpointSlice. EndpointSlice controller thiết lập ```endpointslice-control.l8s.io``` làm giá trị cho label này trên tất cả EndpointSlices mà nó quản lý. Các thực thể khác quản lý EndpointSlices cũng nên thiết lập một giá trị duy nhất cho label này.

### 4. Quyền sở hữu

Trong hầu hết các trường hợp, EndpointSlices sẽ được sở hữu bởi Service mà nó theo dõi các endpoint. Điều này được biểu thị bằng tham chiếu chủ sở hữu trên mỗi EndpointSlice cũng như label ```kubernetes.io/service-name``` cho phép ta tra cứu đơn giản tất cả các EndpointSlices thuộc về 1 Service

## EndpointSlice Controller

EndpointSlice Controller giám sát các Service và Pods để đảm bảo EndpointSlices tương ứng được cập nhật. Controller sẽ quản lý EndpointSlices cho mọi Service có Selector được chỉ định. Chúng sẽ đại diện cho địa chỉ IP của Pod khớp với Selector của Service.

### 1. Kích thước của EndpointSlices

Mặc định, EndpointSlices được giới hạn ở 100 endpoint. Ta có thể cấu hình cờ ```--max-endpoint-perslice``` (cho kube-controller-manager) lên đến tối đa 1000.

### 2. Phân Phối EndpointSlices

Mỗi EndpointSlice có một tập hợp các port áp dụng cho tất cả các endpoint trong tài nguyên. Khi sử dụng các port được đặt tên (named port) cho Service, các pod có thể có các target port number khác nhau cho cùng một named port, dẫn đến cần các EndpointSlices khác nhau. Điều này tương tự như logic đằng sau cách các tập hợp con được nhóm với Endpoint.

Controller sẽ cố gắng điền vào EndpointSlices nhiều nhất có thể, nhưng không chủ động cân bằng lại chúng. Logic của Controller khá đơn giản:
