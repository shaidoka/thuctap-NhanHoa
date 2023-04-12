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

### 2. EndpointSlices

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

### 3. Chế độ ```iptables``` proxy

Trong chế độ này, kube-proxy sẽ giám sát K8s control plane trong việc thêm hoặc xóa **Service** và **Endpoint object**. Đối với mỗi Service, nó sẽ cài đặt các **iptables rule** có nhiệm vụ capture traffic đi đến địa chỉ ```clusterIP``` và ```port``` của Service và chuyển hướng traffic đó đến 1 trong các backend pod của Service. Đối với mỗi Endpoint object, nó sẽ cài đặt các **iptables rule** để lựa chọn 1 backend pod.

Mặc định thì kube-proxy trong iptables mode sẽ lựa chọn 1 backend ngẫu nhiên

Việc sử dụng iptables để quản lý traffic sẽ có chi phí overhead hệ thống thấp hơn vì traffic sẽ được xử lý bởi **Linux netfilter** mà không cần chuyển qua lại giữa userspace và kernel space. Cách tiếp cận này thường là đáng tin cậy hơn.

Nếu kube-proxy đang chạy trong iptables mode và pod đầu tiên được lựa chọn không phản hồi sẽ dẫn đến kết nối thất bại (fail). Đặc điểm này khác với userspace mode trong đó kube-proxy sẽ phát hiện việc kết nối đến pod đầu tiên fail để tự động retry đến 1 backend pod khác.

Ta có thể sử dụng tính năng **readiness probes** (sẽ được đề cập trong bài viết chi tiết về Pod) của Pod để kiểm tra backend pod có đang hoạt động hay không để đảm bảo kube-proxy trong iptables mode chỉ thấy được các backend đã được kiểm tra là vẫn đang hoạt động. Làm như vậy thì ta sẽ tránh được việc traffic gửi qua kube-proxy đến 1 pod không còn hoạt động

![](./images/K8s_Service_2.svg)

### 4. Chế độ IPVS proxy

Trong ```ipvs``` mode, kube-proxy sẽ giám sát K8s **Service** và **Endpoint**, gọi giao diện ```netlink``` để tạo ra các **IPVS rule** tương ứng và đồng bộ IPVS rule với các Service và Endpoint theo định kỳ. Vòng lặp điều khiển (Control loop) này đảm bảo trạng thái của IPVS match với trạng thái mong muốn. Khi truy cập 1 Service, IPVS điều hướng traffic đến 1 trong các backend pod

IPVS proxy mode dựa trên chức năng **hook** của **netfilter** tương tự như iptables mode, nhưng sử dụng **hash table** như là cấu trúc dữ liệu bên dưới và hoạt động trong **kernel space**. Điều này có nghĩa là kube-proxy trong IPVS mode chuyển hướng traffic với độ trễ thấp hơn so với kube-proxy trong iptable mode nên sẽ có hiệu năng tốt hơn nhiều khi đồng bộ các proxy rule. So với các proxy mode khác thì IPVS mode cũng hỗ trợ network traffic với throughput cao hơn.

IPVS cung cấp nhiều tùy chọn hơn trong việc cân bằng traffic đến backend pod:
- ```rr```: round-robin
- ```lc```: least connection
- ```dh```: destination hashing
- ```sh```: source hashing
- ```sed```: shortest expected delay
- ```nq```: never queue

**Lưu ý:** để chạy kube-proxy ở IPVS mode, ta phải cài đặt IPVS trên node trước khi khởi động kube-proxy. Khi kube-proxy khởi động ở iPVS proxy mode, nó sẽ xác minh xem các module kernel của IPVS có khả dụng hay không. Nếu các module kernel của IPVS không được tìm thấy thì kube-proxy sẽ quay trở lại chạy trong iptables proxy mode.

![](./images/K8s_Service_3.svg)

Trong các mô hình proxy này, traffic gắn với địa chỉ ```ip:port``` của Service sẽ được proxy đến backend phù hợp mà không cần cho client biết bất cứ điều gì về K8s hoặc Service hay Pod.

Nếu ta muốn đảm bảo rằng kết nối từ 1 client nào đó được chuyển đến cùng 1 pod (so với kết nối trước đó) thì ta có thể lựa chọn **session affinity** dựa trên địa chỉ IP của client bằng cách thiết lập giá trị cho trường ```service.spec.sessionAffinity``` thành ```ClientIP``` (mặc định là node). Ta cũng có thể thiết lập thời gian tối đa của 1 session bằng tham số ```service.spec.sessionAffinityConfig.clientIP.timeoutSeconds``` phù hợp (mặc định là 10800 tức là 3h)

## Service Multi-Port

Đối với một số Service cần expose ra nhiều hơn 1 port. K8s cho phép ta cấu hình nhiều port trên 1 Service object. Khi sử dụng nhiều port cho 1 service ta phải chỉ định tên của port để tránh bị nhầm lẫn. Ví dụ:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  slector:
    app: MyApp
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 9376
  - name: https
    protocol: TCP
    port: 443
    targetPort: 9377
```

## Lựa chọn địa chỉ IP

Ta có thể chỉ định địa chỉ clusterIP mong muốn khi tạo Service bằng cách sử dụng trường ```.spec.clusterIP```. Ví dụ nếu ta có 1 mục DNS mà muốn sử dụng lại hoặc 1 hệ thống cũ (legacy) đã được cấu hình với 1 địa chỉ IP cụ thể rất khó cấu hình lại.

Địa chỉ IP mà ta lựa chọn phải là IPv4 hoặc IPv6 nằm trong dãy CIDR ```service-cluster-ip-range``` đã được cấu hình trên API server. Nếu ta cố gắng tạo 1 service với địa chỉ IP không hợp lệ thì API server sẽ trả lại mã trạng thái 422 HTTP để báo hiệu có vấn đề.

## Service Discovery

Kubernetes hỗ trợ 2 phương thức chính trong việc tìm kiếm service: **biến môi trường** và **DNS**.

### 1. Biến môi trường

Khi 1 pod chạy trong 1 node thì kubelet sẽ thêm một tập các biến môi trường cho mỗi Service đang hoạt động (active). Nó hỗ trợ các biến môi trường tương thích với Docker Link và các biến đơn giản hơn như ```{SVCNAME}_SERVICE_HOST``` và ```{SVCNAME}_SERVICE_PORT```, trong đó Service là chữ in hoa và dấu gạch ngang được chuyển thành dấu gạch dưới.

Ví dụ Service ```redis-master``` expose TCP port 6379 và đã được gán IP là ```10.0.0.11``` sinh ra các biến môi trường sau:

```sh
REDIS_MASTER_SERVICE_HOST=10.0.0.11
REDIS_MASTER_SERVICE_PORT=6379
REDIS_MASTER_PORT=tcp://10.0.0.11:6379
REDIS_MASTER_PORT_6379_TCP=tcp://10.0.0.11:6379
REDIS_MASTER_PORT_6379_TCP_PROTO=tcp
REDIS_MASTER_PORT_6379_TCP_PORT=6379
REDIS_MASTER_PORT_6379_TCP_ADDR=10.0.0.11
```

**Lưu ý:** khi ta có client Pod cần truy cập đến 1 Service và ta đang sử dụng phương thức **biến môi trường** để công khai Port và clusterIP cho client Pods thì ta phải tạo Service trước khi client Pods xuất hiện. Nếu không thì các client Pods sẽ không nhận được các biến môi trường của chúng (do kubelet thêm vào). Nếu ta chỉ sử dụng DNS để khám phá clusterIP cho một Service, ta không cần lo lắng về vấn đề thứ tự này.

### 2. DNS

Ta có thể thiết lập 1 DNS Service cho cluster của ta bằng cách sử dụng các [addon](https://kubernetes.io/docs/concepts/cluster-administration/addons/)

Một DNS server hỗ trợ cluster như CoreDNS sẽ giám sát K8s API khi có Service mới và tạo 1 tập các DNS record cho mỗi Service. Nếu ta đã bật DNS trong cluster thì tất cả các pod sẽ tự động có thể phân giải Service bằng tên DNS của Service.

Ví dụ, nếu ta có Service tên ```my-service``` trong K8s namespace ```my-ns``` thì Control Plane và DNS Services phối hợp với nhau để tạo ra 1 DNS record là ```my-service.my-ns```. Các pod trong ```my-ns``` namespace có thể tìm thấy Service đơn giản bằng cách thực hiện truy vấn tên ```my-service``` (hoặc cũng có thể tìm kiếm ```my-service.my-ns```).

Các pod trong namespace khác phải sử dụng tên ```my-service.my-ns``` để giao tiếp. Các tên này sẽ được phân giải thành ```ClusterIP``` đã được gán cho Service.

Kubernetes cũng hỗ trợ DNS SRV (Service) records cho các port đã được đặt tên. Nếu ```my-service.my-ns``` Service có 1 port là ```http``` và protocol là ```TCP``` thì ta có thể thực hiện truy vấn DNS SRV cho ```_http._tcp.my-service.my-ns``` để biết được số port cũng như địa chỉ IP của ```http```.

Kubernetes DNS Server là cách duy nhất để truy cập đến ```ExternalName``` Service.

**DNS cho Services và Pods sẽ được đề cập trong 1 bài viết sau**

## Headless Services

Đôi lúc ta không cần cân bằng tải và địa chỉ IP cho Service. Trong trường hợp này, ta có thể tạo ra cái gọi là **Headless Service** bằng cách gán giá trị ```None``` cho clusterIP (```.spec.clusterIP```).

Ta có thể sử dụng 1 Headless Service để giao tiếp với các cơ chế khám phá Service khác mà không bị ràng buộc với những cái có sẵn của K8s.

Headless Services sẽ không gán ClusterIP, kube-proxy sẽ không quản lý các Service này và sẽ không có cân bằng tải hay proxy nào được thực hiện cho chúng. Cách DNS tự động cấu hình tùy thuộc vào việc Service có định nghĩa Selector hay không:

**Có Selector**

Với Headless Services có định nghĩa Selector thì Endpoint Controller sẽ tạo ra các ```Endpoints``` record trong API và chỉnh sửa cấu hình DNS để trả về các record (chứa địa chỉ) trỏ trực tiếp đến các ```Pod``` của ```Service```

**Không có Selector**

Với Headless Services không định nghĩa Selector thì Endpoint Controller sẽ không tạo ra các ```Endpoints``` record. Tuy nhiên, hệ thống DNS sẽ tìm kiếm và cấu hình:
- CNAME record đối với loại **ExternalName** Services 
- A record đối cho bất kỳ ```Endpoints``` nào có cùng tên với Services đối với các loại Services khác

## Công khai Services (ServiceTypes)

Với một số phần của ứng dụng (như frontend) ta có thể muốn expose 1 Services ra 1 địa chỉ IP bên ngoài cluster.

Trường ```ServiceTypes``` cho phép ta chỉ định kiểu Services mong muốn. Giá trị mặc định là ```ClusterIP``` hoặc các giá trị sau:
- ```ClusterIP```: expose Services ra địa chỉ IP nội bộ của cluster nghĩa là Service chỉ có thể kết nối được từ bên trong cluster. Đây là giá trị mặc định.
- ```NodePort```: expose Services ra địa chỉ IP của mỗi Node tại 1 port tĩnh (được gọi là ```NodePort```). Một service loại ```ClusterIP``` (nơi mà ```NodePort``` Services sẽ route về) sẽ tự động được tạo ra. Ta có thể giao tiếp với ```NodePort``` Services từ bên ngoài Cluster thông qua địa chỉ ```<NodeIP>:<NodePort>```
- ```LoadBalancer```: expose Services ra bên ngoài sử dụng bộ cân bằng tải (Load Balancer) của nhà cung cấp đám mây. ```NodePort``` và ```ClusterIP``` Services nơi mà bộ cân bằng tải bên ngoài route về sẽ được tự động tạo ra.
- ```ExternalName```: ánh xạ Services với nội dung của trường ```externalName``` (ví dụ ```foo.bar.example.com```) bằng cách trả lại giá trị của ```CNAME``` record, không cần cài đặt hay proxy gì thêm.

Ta cũng có thể sử dụng **Ingress** để expose Services. Ingress không phải là 1 loại Services nhưng nó hoạt động như là 1 entrypoint cho cluster. Nó cho phép ta tổng hợp các routing rule (quy tắc định tuyến) vào trong 1 tài nguyên duy nhất vì nó có thể expose nhiều Services trên cùng 1 địa chỉ IP. Sẽ có 1 bài riêng về **Ingress** sau, giờ ta lần lượt tìm hiểu về:

### 1. NodePort

Nếu ta thiết lập trường ```type``` thành ```NodePort```, thì K8s Control Plane sẽ phân bổ 1 port trong dãy được chỉ định bởi cờ ```--service-node-port-range``` (mặc định: 30000 - 32767). Mỗi node sẽ proxy port đó (cùng port number trên mọi Node) vào trong Services. Các Services sẽ báo cáo port đã được gán cho nó thông qua trường ```.spec.port[*].nodePort```.

Nếu ta muốn chỉ định 1 địa chỉ IP cụ thể để proxy Port thì ta có thể thiết lập cờ ```nodeport-addresses``` trong kube-proxy thành các dãy IP mong muốn. Cơ chế này được hỗ trợ từ K8s 1.10. Cờ này sử dụng dấu phẩy "," để tách biệt giữa các dãy IP (VD: ```10.0.0.0/8,192.0.2.0/25```) mà kube-proxy nên xem xét là cục bộ (local) để sử dụng trên node này.

Ví dụ nếu ta khởi động kube-proxy với cờ ```--nodeport-addresses=127.0.0.0/8``` thì kube-proxy chỉ lựa chọn các loopback interface cho NodePort Services. Giá trị mặc định cho ```--nodeport-addresses``` là danh sách trống. Có nghĩa là kube-proxy nên xem xét tất cả các network interface hiện có cho NodePort. (Điều này cũng tương thích với các bản phát hành K8s trước đó).

Nếu ta muốn sử dụng 1 port cụ thể, ta có thể chỉ định 1 giá trị cho trường ```nodePort```. Control Plane sẽ phân bổ port đó hoặc sẽ báo cáo là giao dịch API bị lỗi (```API transaction failed```). Có nghĩa là ta cần phải quản lý thủ công sự xung đột về Port. Ta cũng phải sử dụng 1 port hợp lệ nằm trong dãy đã được cấu hình để sử dụng cho ```NodePort```.

Việc sử dụng ```NodePort``` cho phép ta tự do thiết lập các giải pháp cân bằng tải (Load Balancing) riêng của ta để cấu hình các môi trường không được hỗ trợ đầy đủ bởi K8s hoặc thậm chí chỉ expose trực tiếp 1 hoặc vài node IP.

Lưu ý rằng Service nodePort này được nhìn thấy thông qua ```<NodeIP>:spec.ports[*].nodePort``` và ```.spec.clusterIP:spec.ports[*].port``` (Nếu cờ ```--nodeport-addresses``` trong kube-proxy được thiết lập thì nó sẽ lọc các NodeIP)

Ví dụ:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: MyApp
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30007
```

### 2. Loại LoadBalancer

Trên các nhà cung cấp đám mây có hỗ trợ **external load balancer**, việc thiết lập trường ```type``` thành ```LoadBalancer``` sẽ cần chuẩn bị (provision) trước 1 bộ cân bằng tải cho Service của ta. Quá trình tạo bộ cân bằng tải thật sự diễn ra bất đồng bộ và thông tin về bộ cân bằng tải đã được chuẩn bị trước đó sẽ được công bố (published) trong trường ```.status.loadBalancer```. Ví dụ:

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
  cluserIP: 10.0.171.239
  type: LoadBalancer
status:
  loadBalancer:
    ingress:
    - ip: 192.0.2.127
```

Traffic từ bộ cân bằng tải bên ngoài sẽ được chuyển hướng đến các pod ở backend. Nhà cung cấp đám mây sẽ quyết định cách nó sẽ được cân bằng tải.

Đối với loại Service ```LoadBalancer```, khi có nhiều hơn một port được định nghĩa, tất cả các port phải có cùng giao thức (protocol) và giao thức phải là một trong ```TCP```, ```UDP``` hoặc ```SCTP```.

Một số nhà cung cấp đám mây cho phép ta chỉ định giá trị cho ```loadBalancerIP```. Trong trường đó, bộ cân bằng tải được tạo ra với địa chỉ IP cụ thể do ta thiết lập trong trường ```loadBalancerIP```. Nếu trường ```loadBalancerIP``` không được thiết lập thì bộ cân bằng tải sẽ được thiết lập 1 địa chỉ IP tạm thời (ephemeral). Nếu ta chỉ định trường ```loadBalancerIP``` nhưng nhà cung cấp đám mây không hỗ trợ tính năng này thì giá trị đã thiết lập cho trường ```loadBalancerIP``` sẽ bị bỏ qua.

**Internal Load Balancer**

Trong một môi trường hỗn hợp, đôi lúc ta cần phải route traffic từ các Services vào bên trong cùng 1 dãy địa chỉ network (virtual)

Trong môi trường split-horizon DNS, ta sẽ cần 2 Services để có thể route cả traffic bên trong và bên ngoài đến các endpoint.

Ta có thể đạt được điều này bằng cách thêm 1 trong các annotation sau vào Services. Loại Annotations nào cần đưa vào tùy thuộc vào nhà cung cấp đám mây ta đang sử dụng:

GCP:

```sh
[...]
metadata:
  name: my-service
  annotation:
    cloud.google.com/load-balancer-type: "Internal"
[...]
```

AWS:

```sh
[...]
metadata:
  name: my-service
  annotations:
    cloud.google.com/load-balancer-type: "Internal"
[...]
```

Azure:

```sh
[...]
metadata:
  name: my-service
    annotations:
      service.beta.kubernetes.io/azure-load-balancer-internal: "true"
[...]
```

OpenStack:

```sh
[...]
metadata:
    name: my-service
    annotations:
        service.beta.kubernetes.io/openstack-internal-load-balancer: "true"
[...]
```

### 3. Loại ExternalName

Các Services thuộc loại ```ExternalName``` sẽ ánh xạ 1 Services đến 1 tên DNS chứ không phải là đến 1 selector thông thường như ```my-service``` hay ```casssandra```. Ta chỉ định các Services này thông qua tham số ```spec.externalName```

Ví dụ định nghĩa Services có tên ```my-service``` trong namespace ```prod``` để ánh xạ đến ```my.database.example.com```:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: prod
spec:
  type: ExternalName
  externalName: my.database.example.com
```

Khi tìm kiếm host có tên ```my-service.prod.svc.cluster.local```, thì DNS service của cluster sẽ trả lại 1 CNAME record với giá trị ```my.database.example.com```. Việc truy cập vào ```my-service``` sẽ hoạt động theo cách tương tự như với các Services khác nhưng có 1 sự khác biệt quan trọng là việc chuyển hướng sẽ diễn ra ở cấp DNS thay vì thông qua proxy hay forwarding. Nếu sau này ta muốn chuyển Database vào trong cluster, ta có thể khởi động các pod của nó, đưa thêm vào các selector hoặc endpoint phù hợp và thay đổi trường ```type``` của Services

**Lưu ý:** Ta có thể gặp khó khăn khi sử dụng ExternalName cho một số giao thức phổ biến, như HTTP và HTPPS. Nếu ta sử dụng ExternalName thì Hostname được sử dụng bởi các client bên trong cluster của ta sẽ khác với tên mà ExternalName tham chiếu. Đối với các giao thức sử dụng hostname, sự khác biệt này có thể dẫn đến lỗi hoặc phản hồi không mong muốn. Các yêu cầu HTTP sẽ có một ```Host:header``` mà server gốc không nhận ra. TLS Server sẽ không thể cung cấp certificate khớp với hostname mà client kết nối đến.

### 4. External IP

Nếu có các địa chỉ IP bên ngoài route đến 1 hoặc nhiều cluster node thì các Service của K8s có thể được expose ra trên các ```externalIPs``` đó. Các traffic đi vào (ingress) trong cluster với externalIP (như là destination IP) trên Service Port, sẽ được route đến 1 trong những endpoint của Services. ```externalIPs``` không được quản lý bởi kubernetes mà là trách nhiệm của cluster admin.

Trong đặc tả của Services, ```externalIPs``` có thể được ghi cùng với bất kỳ ```ServiceTypes``` nào. Trong ví dụ bên dưới, ```my-service``` có thể được truy cập bởi các client tại ```80.11.12.10:80``` (externalIP:port)

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 9376
  externalIPs:
  - 80.11.12.10
```

## Các thiếu sót 

Việc sử dụng userspace proxy cho VIP (virtual IP) hoạt động ở phạm vi nhỏ và vừa nhưng không thể mở rộng thành cluster lớn đến rất lớn tầm hàng ngàn Services. 

Việc sử dụng userspace proxy sẽ che khuất địa chỉ IP nguồn của 1 gói tin truy cập đến Services. Điều này làm cho một số cơ chế network filtering (như firewall) là không khả thi. Chế độ iptables proxy sẽ không che khuất địa chỉ IP nguồn (bên trong cluster) nhưng nó vẫn ảnh hưởng đến các client đến từ load balancer hoặc node port.

Trường ```Type``` được thiết kế như là 1 chức năng được lồng vào, mỗi cấp (level) được thêm vào cho cấp trước. Đây không phải là yêu cầu bắt buộc đối với tất cả các nhà cung cấp đám mây (ví dụ GCP không cần phải phân bổ 1 ```NodePort``` để cho ```LoadBalancer``` hoạt động nhưng AWS thì có) nhưng API hiện tại yêu cầu nó.

## Cài đặt Virtual IP

Những gì mô tả trong phần trước là tương đối đủ cho việc sử dụng Services. Tuy nhiên có nhiều thành phần khác nên nắm rõ.

### 1. Tránh xung đột

Một trong những nguyên tắc chính của K8s là không để ta bị rơi vào tình huống có thể khiến các hành động của ta bị thất bại mặc dù không phải do lỗi của ta. Với thiết kế của tài nguyên Services, điều này có nghĩa là không bắt ta phải tự đưa ra quyết định lựa chọn port number nếu lựa chọn đó xung đột với lựa chọn của một người khác. Đó chính là sự cô lập các lỗi.

Để cho phép ta chọn 1 port number cho Services, ta phải đảm bảo rằng khong có 2 Services nào bị xung đột. K8s thực hiện bằng cách phân bổ cho mỗi Services 1 địa chỉ IP riêng.

Để đảm bảo mỗi Services nhận được 1 địa chỉ IP duy nhất, 1 bộ cấp phát nội bộ (**internal allocator**) sẽ tự động cập nhật bản đồ cấp phát toàn cục (**global**) trong cơ sở dữ liệu etcd trước khi tạo Services. Object bản đồ (map object) phải tồn tại trong registry cho Services để có thể nhận được 1 địa chỉ IP, nếu không việc tạo Services sẽ bị thất bại với 1 thông điệp cho biết địa chỉ IP không thể được phân bổ.

Trong Control Plane, 1 **background Controller** sẽ chịu trách nhiệm cho việc tạo bản đồ (map) đó (cần thiết để hỗ trợ di chuyển từ các phiên bản cũ hơn của Kubernetes sử dụng **in-memory locking**). K8s cũng sử dụng các **Controller** để kiểm tra việc cấp phát không đúng (ví dụ bởi vì admin can thiệp) và để xóa các địa chỉ IP đã được cấp phát mà không còn được sử dụng bởi bất kỳ Services nào.

### 2. Địa chỉ IP của Service

Không giống như các địa chỉ IP của Pod, được thật sự route đến 1 đích cố định. Địa chỉ IP của Services không thật sự được trả lời bởi 1 host cụ thể nào. Thay vào đó kube-proxy sử dụng **iptables** để định nghĩa địa chỉ IP Virtual sẽ được chuyển hướng khi cần. Khi các client kết nối đến Virtual IP (VIP), traffic của chúng sẽ được tự động chuyển đến 1 endpoint phù hợp. Các **biến môi trường** và **DNS** cho Services sẽ thật sự được điền theo địa chỉ VIP (và Port) của Service (nghĩa là biến môi trường của mỗi Pod và DNS của Service sẽ sử dụng VIP của Service).

kube-proxy hỗ trợ 3 chế độ proxy là ```userspace```, ```iptables```, ```ipvs``` mỗi chế độ lại hoạt động hơi khác nhau.

**Userspace**

Ví dụ xem xét ứng dụng xử lý ảnh được mô tả trong phần trước. Khi backend Services được tạo ra thì K8s master sẽ phân bổ 1 VIP, ví dụ ```10.0.0.1```. Giả sử Services port là ```1234```, Service này sẽ được quan sát bởi tất cả kube-proxy instance trong toàn cluster.

Khi proxy thấy có 1 Services mới, nó sẽ mở 1 port ngẫu nhiên mới, thiết lập iptables rule để chuyển hướng traffic từ VIP đến port mới này và bắt đầu chấp nhận kết nối đến nó.

Khi 1 client kết nối đến VIP của Service thì các iptables rule sẽ được sử dụng và chuyển hướng các gói tin đến port của proxy. "Service proxy" sẽ lựa chọn 1 backend (theo thuật toán **round-robin**) và bắt đầu proxy traffic từ client đến backend đó.

Điều này có nghĩa là Service owners có thể lựa chọn bất kỳ port nào họ muốn mà không gặp rủi ro về sự xung đột. Các client đơn giản chỉ kết nối đến IP và Port mà không cần quan tâm đến Pod nào nó đang truy cập đến.

**Iptables**

Một lần nữa, hãy xem xét ứng dụng xử lý ảnh được mô tả trong phần trước. Khi backend Services được tạo ra thì K8s master sẽ phân bổ 1 VIP, ví dụ ```10.0.0.1```. Giả sử Service port là ```1234```, Services này sẽ được quan sát bởi tất cả kube-proxy instance trong toàn cluster

Khi proxy thấy có 1 Services mới, nó sẽ cài đặt các iptables rules để chuyển hướng traffic từ VIP đến các rule cho từng Services. Các rule cho từng Services liên kết với các rule cho từng Endpoint để chuyển hướng traffic (sử dụng destination NAT) đến các backend.

Khi 1 client kết nối với VIP của Services thì các iptables rule sẽ được kích hoạt. Một backend Pod được lựa chọn (có thể dựa trên **session affinity** hoặc **ngẫu nhiên**) và các gói tin sẽ được chuyển hướng đến các backend đó. Không giống như userspace proxy, các gói tin sẽ không bao giờ được copy vào userspace, kube-proxy không cần phải chạy để cho VIP hoạt động được và các node sẽ thấy traffic đến từ địa chỉ IP không thay đổi của client.

Quy trình cơ bản này cũng sẽ được thực thi khi traffic đến thông qua nodeport hoặc qua 1 load balancer mặc dù trong những trường hợp đó, địa chỉ IP của client sẽ bị thay đổi.

**IPVS**

Hoạt động của iptables sẽ bị chậm đáng kể trong cluster kích thước lớn với hàng chục nghìn Services. IPVS được thiết kế để cân bằng tải và dựa trên hash table bên trong kernel. Vì vậy ta có thể đạt được hiệu năng ổn định khi có nhiều Service từ kube-proxy dựa trên IPVS. Có nghĩa là kube-proxy dựa trên IPVS có thuật toán cân bằng tải phức tạp hơn (least conns, locality, weighted, persistence)

## API Object

Service là 1 top-level resource trong Kubernetes REST API. Chi tiết ở [Kubernetes Service API](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#service-v1-core)

## Các giao thức được hỗ trợ

### 1. TCP

Ta có thể sử dụng TCP cho bất kỳ loại Service nào vì nó là giao thức mạng mặc định

### 2. UDP

Ta có thể sử dụng UDP cho hầu hết các Service. Đối với Service có ```type=LoadBalancer```, việc hỗ trợ UDP phụ thuộc vào nhà cung cấp đám may có cung cấp tính năng này không.

### 3. HTTP

Nếu nhà cung cấp đám mây của ta hỗ trợ giao thức này, ta có thể sử dụng Service ở chế độ LoadBalancer để thiết lập reverse proxy HTTP/HTTPS bên ngoài, được forward đến Endpoint của Service.

### 4. Giao thứ Proxy

Nếu nhà cung cấp cloud hỗ trợ giao thức này, ta có thể sử dụng Service ở chế độ LoadBalaner để cấu hình bộ cân bằng tải bên ngoài K8s, nó sẽ forward các kết nối đã được gắn tiền tố (prefix) với giao thức proxy

Bộ cân bằng tải sẽ gửi 1 loạt các octet ban đầu mô tả kết nối đến, tương tự như ví dụ sau:

```sh
PROXY TCP4 192.0.2.202 10.0.42.7 12345 7\r\n
```

theo sau đó là dữ liệu từ client

### 5. SCTP

K8s hỗ trợ SCTP làm giá trị cho trường ```protocol``` trong đặc tả Service, Endpoint, NetworkPolicy và Pod dưới dạng tính năng alpha. Để kích hoạt tính năng này, cluster admin cần bật ```SCTPSupport``` feature gate trên apiserver, ví dụ ```--feature-gate=SCTPSupport=true```

