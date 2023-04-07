# Service

Một cách trừu tượng, ta có thể expose 1 ứng dụng đang chạy trên các pod như là 1 network Service.

Với K8s, ta không cần phải chỉnh sửa ứng dụng để sử dụng với các cơ chế khám phá dịch vụ (service discovery) phức tạp. K8s gán địa chỉ IP cho các pod và 1 tên DNS duy nhất cho 1 nhóm các pod để thực hiện cân bằng tải (load balancing) giữa chúng.

## Motivation

Các pod trong K8s có lifetime cụ thể, chúng được tạo ra và khi mất đi, chúng sẽ không được recycle. Nếu ta sử dụng Deployment để chạy ứng dụng, ta có thể tạo và hủy pod 1 cách tự động.

Mỗi pod có địa chỉ IP của nó, tuy nhiên, trong 1 Deployment, tập các pod đang chạy tại 1 thời điểm có thể khác với tập các pod chạy tại 1 thời điểm khác sau đó (lý do vì có thể đã có sự thay đổi các pod ví dụ khi có sự thay đổi node hoặc pod bị lỗi,... nên Deployment sẽ tự động tạo pod mới thay thế).

Điều này dẫn đến 1 vấn đề: Nếu 1 tập các pod nào đó (giả sử gọi là backend) cung cấp chức năng cho các pod khác (giả sử là frontend) trong cluster thì làm cách nào frontend tìm ra và theo dõi địa chỉ IP nào để kết nối đến các backend? Service sẽ giúp ta giải quyết vấn đề này.

## Tài nguyên Service

Trong K8s, Service là 1 khái niệm trừu tượng định nghĩa logic 1 tập các pod và 1 chính sách (**policy**) để truy cập đến chúng (đôi khi khuôn mẫu này được gọi là **micro-service**). Tập các pod mục tiêu của 1 service thường được quyết định bởi *selector*.

Ví dụ xem xét trường hợp 1 ứng dụng xử lý hình ảnh phi trạng thái (**stateless**) ở backend đang chạy với 3 bản sao (**replica**). Các bản sao đó có thể thay thế được vào frontend không cần quan tâm pod nào ở backend mà nó đang sử dụng. Mặc dù pod thật sự cấu thành nên backend có thể bị thay đổi, frontend client không cần phải biết điều đó cũng như không cần theo dõi trạng thái của các backend này.

=> Khái niệm Service cho phép sự tách rời này

Nếu ta sử dụng K8s API để khám phá dịch vụ (service discovery) trong ứng dụng, ta có thể truy vấn các endpoint của API server để được cập nhật mỗi khi các pod trong service bị thay đổi.

Đối với các ứng dụng không phải là cloud-native, K8s cung cấp để đặt **network port** hoặc **load balancer** ở giữa ứng dụng và các backend pod

## Định nghĩa service

Service trong K8s là 1 REST object tương tự như Pod. Giống như các REST object khác, ta có thể POST định nghĩa của Service lên cho API server để tạo 1 instance mới.

Ví dụ ta có 1 tập các pod, mỗi pod listen port TCP 9376 và có label là ```app=MyApp```

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
```

Đặc tả trên sẽ tạo 1 Service object mới có tên là ```my-service``` nhắm mục tiêu là bất kỳ Pod nào đang lắng nghe trên TCP port ```9376``` và có label là ```app=MyApp```

Kubernetes sẽ gán cho Service này 1 địa chỉ IP (đôi lúc được gọi là **Cluster IP**) được sử dụng bởi **Service Proxy** (Service Proxy sẽ được đề cập sau).

Controller của Service selector sẽ liên tục quét các pod match với selector của nó rồi sau đó POST bất kỳ sự thay đổi nào đến **Endpoint object** cũng có tên là ```my-service```

**Lưu ý:** Service có thể ánh xạ bất kỳ ```port``` nào tới ```targetPort```, do đó để thuận tiện thì ta thường để 2 trường này tương tự nhau

Phần định nghĩa về Port trong đặc tả của Pod sẽ có tên và ta có thể tham chiếu đến tên này trong thuộc tính ```targetPort``` của Service (nghĩa là giá trị của ```targetPort``` trong đặc tả Service sẽ giống với giá trị của ```port``` trong đặc tả của Pod để chúng liên kết với nhau)

Cách này (sử dụng tên để tham chiếu đến port) vẫn hoạt động ngay cả khi có sự trộn lẫn các Pod trong Service bằng cách sử dụng 1 tên duy nhất với cùng network protocol trên các port khác nhau (nghĩa là trong đặc tả của các pod ở backend, ta cấu hình mỗi pod sẽ lắng nghe trên 1 port number khác nhau nhưng sử dụng cùng 1 tên rồi tham chiếu đến tên này trong đặc tả của Service). Cách này rất linh hoạt khi triển khai và phát triển các Service. Ví dụ ta có thể thay đổi port number mà pod sẽ expose ra trong phiên bản tiếp theo của phần mềm backend mà không làm các client bị mất kết nối.

Protocol mặc định cho Service là TCP, ta cũng có thể sử dụng các protocol được hỗ trợ khác nếu muốn.

Khi các Service cần expose ra nhiều hơn 1 port, K8s hỗ trợ nhiều phần định nghĩa port trong 1 Service object. Mỗi định nghĩa port có thể có cùng hoặc khác protocol.

### 1. Service không có Selector

Service là 1 khái niệm phổ biến để truy cập đến cá cpod nhưng chúng cũng có thể trừu tượng hóa các loại backend khác. Ví dụ:
- Ta muốn sử dụng Database cluster bên ngoài trong môi trường *production* nhưng trong môi trường *test* ta lại sử dụng database riêng.
- Ta muốn trỏ Service của ta đến 1 Service trong Namespace khác hoặc trên 1 cluster khác.
- Ta đang di chuyển (migrate) 1 workload lên K8s, trong khi đánh giá cách tiếp cận này, ta chỉ chạy 1 phần của backend trên K8s

Trong bất kỳ trường hợp nào bên trên, ta có thể định nghĩa 1 service mà không có pod selector. Ví dụ:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
```

Bởi vì Service này không có selector nên **Endpoint object** tương ứng sẽ không tự động được sinh ra. Ta có thể ánh xạ thủ công Service đến địa chỉ network và port nơi ứng dụng đang chạy bằng cách thêm **Endpoint object** thủ công như sau:

```sh
apiVersion: v1
kind: Endpoints
metadata:
  name: my-service
subsets:
  - addresses:
    - ip: 192.0.2.42
    ports:
      - port: 9376
```

**Lưu ý:** IP của Endpoint không được là **loopback** hoặc **link-local** (169.254.0.0/16). Ip của của Endpoint cũng không thể là Cluster IP của các K8s Service khác vì kube-proxy không hỗ trợ virtual IP làm đích.

Việc truy cập đến các Service không có selector cũng tương tự như truy cập đến Service có selector. Trong ví dụ ở trên, traffic được route đến 1 endpoint duy nhất có địa chỉ IP được định nghĩa trong file yaml là ```192.0.2.42:9376``` (TCP)

```ExternalName``` Service là 1 trường hợp đặc biệt của Service không có selector mà sử dụng tên DNS thay thế. Chi tiết sẽ được đề cập sau.

### 2. EndpintSlices

```EndpointSlice``` là 1 tài nguyên API có thể cung cấp 1 sự thay thế có thể mở rộng được cho ```Endpoint```. Mặc dù về mặt khái niệm là khá giống với ```Endpoint```, song ```EndpointSlice``` cho phép phân tán các network endpoint trên nhiều tài nguyên khác nhau. Mặc định, 1 ```EndpointSlice``` được xem như là "full" khi nó đạt tới 100 endpoint. Lúc đó, nếu có thêm endpoint mới thì 1 ```EndpointSlice``` mới sẽ được tạo ra để lưu trữ các endpoint mới này

```EndpointSlice``` cung cấp các thuộc tính và chức năng bổ sung, chi tiết sẽ được đề cập ở các bài viết sau.

## Virtual IP và Service Proxies

Mọi node trong K8s cluster đều chạy kube-proxy, nó chịu trách nhiệm cho việc cài đặt một hình thức VirtualIP cho các loại Services không phải là ExternalName

### 1. Tại sao không sử dụng round-robin DNS?

Một câu hỏi được đặt ra là tại sao K8s lại dựa trên proxy để chuyển inbound traffic đến backend. Các cách tiếp cận khác thì sao, ví dụ liệu ta có thể cấu hình DNS Record với nhiều A record để hoạt động dựa trên phân giải tên theo kiểu round-robin?

Có nhiều lý do để sử dụng Proxy cho Service:
- Đã có nhiều vấn đề xảy ra khi triển khai DNS khiến nó không tôn trọng TTL và vẫn giữ lại bản cache kết quả của việc truy vấn tên thậm chí sau khi chúng đã hết hạn (nghĩa là dù đã hết thời gian TTL nhưng cache vẫn không bị xóa dẫn đến không hoạt động đúng theo nguyên tắc round-robin)
- Một số ứng dụng thực hiện truy vấn DNS chỉ 1 lần rồi cache kết quả vô thời hạn
- Thậm chí nếu các ứng dụng và thư viện thực hiện phân giải lại tên miền thì với giá trị TTL thấp hoặc bằng 0 trên DNS record sẽ gây ra vấn đề tải cao (high load) trên DNS nên sẽ khó quản lý.

### 2. Chế độ User space proxy

Trong chế độ (mode) này, kube-proxy sẽ giám sát K8s master trong việc thêm và xóa **Service** cũng như **Endpoint object**. Đối với mỗi Service, nó sẽ mở 1 port (ngẫu nhiên, port này được gọi là **proxy port**), trên **local node** (local node là node mà kube-proxy đó đang chạy). Bất kỳ kết nối nào đến **proxy port** này sẽ được proxy đến một trong các pod backend của Service (đã được khai báo thông qua Endpoint). kube-proxy có tính đến thiết lập ```SessionAffinity``` của Service khi quyết định backend pod nào sẽ được sử dụng.

Cuối cùng, user-space proxy sẽ cài đặt các **iptables rules** để capture các traffic đi đến địa chỉ ```clusterIP``` (là địa chỉ virtual) và ```port``` của Service. Các rule này sẽ chuyển hướng traffic đó đến proxy port để được proxies đến backend pod.

Mặc định, kube-proxy trong userspace mode sẽ chọn 1 backend bằng thuật toán round-robin

![](./images/K8s_Service_1.svg)