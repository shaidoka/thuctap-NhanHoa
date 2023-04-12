# Service Topology

Service Topology cho phép một service route traffic (định tuyến lưu lượng) dựa trên Node topology của cluster. Ví dụ: 1 service có thể chỉ định rằng traffic được ưu tiên route đến các endpoint nằm trên cùng một Node với client hoặc trong cùng vùng khả dụng (availability zone).

## Giới thiệu

Mặc định, traffic được gửi đến ```ClusterIP``` service hoặc ```NodePort``` service có thể được route đến bất kỳ địa chỉ backend nào của Service. Kể từ K8s 1.7, ta có thể route các traffic "bên ngoài" đến các Pod chạy trên Node, nhưng điều này không được hỗ trợ cho các ```ClusterIP``` service và các topology phức tạp hơn - như routing dựa trên zone - là không thể thực hiện được. Tính năng Service Topology giải quyết vấn đề này bằng cách cho phép người tạo ra Service xác định chính sách để route traffic dựa vào label của Node cho các Node gốc và Node đích.

Bằng cách khớp (match) label của Node giữa nguồn và đích, toán tử có thể chỉ định nhóm các Node "gần" và "xa" nhau hơn, sử dụng bất kỳ số liệu (metric) nào có ý nghĩa đối với các yêu cầu của toán tử đó. Ví dụ, đối với nhiều người quản trị (operator) trong public cloud, có 1 sự ưu tiên là giữ traffic của service trong cùng 1 zone (vùng, khu vực), bởi vì traffic giữa các zone có chi phí liên quan trong khi traffic nội bộ thì không. Các nhu cầu phổ biến khác bao gồm có thể route traffic đến 1 Pod cục bộ (local) được quản lý bởi DaemonSet hoặc giữ traffic truy cập đến các Node được kết nối với cùng Switch trong tủ rack để có độ trễ thấp nhất.

## Sử dụng Service Topology

Nếu cluster của ta đã kích hoạt hỗ trợ Service Topology, ta có thể kiểm soát việc route traffic của Service bằng cách chỉ định trường ```topologyKeys``` trong đặc tả của Service. Trường này là 1 danh sách thứ tự ưu tiên chứa label của các Node sẽ được sử dụng để sắp xếp các endpoint khi truy cập Service này.

Traffic truy cập sẽ được chuyển đến Node với label có giá trị khớp label đầu tiên của ```topologyKeys```. Nếu không có backend Pod nào của Service chạy trên Node sẽ được lựa chọn đó (node có label khớp), thì label thứ 2 trong danh sách của ```topologyKeys``` sẽ được xem xét và quá trình trên sẽ lặp lại cho đến khi không còn label nào.

Nếu không Node nào khớp với toàn bộ danh sách của ```topologyKeys``` thì traffic sẽ bị từ chối, điều này là giống như trường hợp không có backend Pod nào cho Service cả. Nghĩa là các endpoint được lựa chọn dựa trên topology key đầu tiên khớp với các backend pod có sẵn. Nếu trường này được chỉ định và tất cả các mục (các label trong danh sách) đều không có backend khớp với topology của client thì nghĩa là Service không có backend nào cho client đó và kết nối không thành công.

Giá trị đặc biệt ```"*"``` có thể được sử dụng, nó có nghĩa là "bất kỳ topology nào". Giá trị ```*``` này, nếu được sử dụng, thì nên đặt nó là giá trị cuối cùng trong danh sách của ```topologyKeys```.

Nếu ```topologyKeys``` không được chỉ định hoặc để trống thì sẽ không áp dụng các ràng buộc topology.

Hãy xem xét một cluster với các Node được gắn label là hostname, zone name và region name của chúng. Sau đó, ta có thể thiết lập giá trị cho trường ```topologyKeys``` của Service để chuyển hướng traffic như sau:
- Chỉ chuyển traffic đến các endpoint trên cùng 1 node, nó sẽ thất bại nếu không endpoint nào tồn tại trên node đó: ```["kubernetes.io/hostname"]```
- Ưu tiên chuyển đến endpoint trên cùng 1 node, nếu không có thì chuyển cho các endpoint trong cùng 1 zone, nếu vẫn không có thì chuyển cho các endpoint trong cùng region, cuối cùng nếu vẫn không có thì xem như thất bại: ```["kubernetes.io/hostname", "topology.kubernetes.io/zone", "topology.kubernetes.io/region"]```. Điều này có thể hữu ích, ví dụ trong trường hợp lưu dữ liệu cục bộ là quan trọng.
- Ưu tiên chuyển đến các endpoint trong cùng 1 zone, nếu không có sẽ chuyển cho bất kỳ endpoint khả dụng nào: ```["topology.kubernetes.io/zone", "*"]```

## Hạn chế

- Service topology không tương thích với ```externalTrafficPolicy=Local``` và do đó, 1 service không thể sử dụng cả 2 tính năng này. Ta có thể sử dụng cả 2 tính năng trong cùng 1 cluster trên các Service khác nhau chứ không phải trên cùng 1 Service.
- Các topology key hợp lệ hiện bị giới hạn trong các giá trị ```kubernetes.io/hostname```, ```topology.kubernetes.io/zone``` và ```topology.kubernetes.io/region``` nhưng sẽ được khái quát cho các node label khác trong tương lai.
- Topology key phải là label key hợp lệ và ta chỉ có thể chỉ định tối đa 16 key.
- Giá trị bất kỳ (catch-all), ```"*"```, phải là giá trị cuối cùng trong danh sách các topology key, nếu nó được sử dụng.

## Ví dụ

Sau đây là những ví dụ phổ biến về việc sử dụng tính năng Service Topology

### 1. Chỉ chuyển đến Endpoint cục bộ trên Node

Một Service chỉ route traffic đến các endpoint cục bộ của Node. Nếu không có endpoint nào tồn tại trên node thì traffic sẽ bị hủy:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  topologyKeys:
    - "kubernetes.io/hostname"
```

### 2. Ưu tiên chuyển đến Endpoint cục bộ trên Node

Service ưu tiên các endpoint cục bộ của Node nhưng nếu Node đó không có endpoint nào thì chuyển đến các endpoint trên toàn phạm vi cluster

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  topologyKeys:
    - "kubernetes.io/hostname"
    - "*"
```

### 3. Chỉ chuyển cho các Endpoint của Zone hoặc Region

Service ưu tiên các endpoint trong zone, sau đó đến trong region. Nếu không có endpoint nào tồn tại trong cả 2 thì traffic sẽ bị hủy:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  topologyKeys:
    - "topology.kuberntes.io/zone"
    - "topology.kuberntes.io/region"
```

### 4. Ưu tiên chuyển cho các Endpoint trên Local, sau đó đến Zone và Region

Service ưu tiên các endpoint trên node cục bộ, sau đó đến zone, region và cuối cùng là chuyển cho các endpoint trên phạm vi cluster:

```sh
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  topologyKeys:
    - "kubernetes.io/hostname"
    - "topology.kubernetes.io/zone"
    - "topology.kubernetes.io/region"
    - "*"
```