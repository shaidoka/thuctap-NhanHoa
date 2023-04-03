# Taint và Toleration

**Node affinity** là một thuộc tính của Pod để thu hút chúng vào một tập hợp các node (có thể là tùy chọn hoặc yêu cầu cứng). **Taints** thì ngược lại - chúng cho phép một node từ chối một tập hợp các pod nào đó.

**Toleration** được áp dụng cho các pod và cho phép (nhưng không bắt buộc) các pod được lập lịch trên các node khớp với taint.

Taints và Toleration phối hợp với nhau để đảm bảo rằng các pod không được lập lịch trên các node không phù hợp. Một hoặc nhiều taints được áp dụng cho một node; việc đánh dấu taint này có nghĩa là node không được chấp nhận bất kỳ pod nào không **tolerate** (chấp nhận/chịu đựng) được các **taint** (lỗi/hư hỏng).

## Khái niệm

Ta thêm taint vào một node bằng cách sử dụng lệnh ```kubectl taint```. Ví dụ:

```sh
kubectl taint nodes node1 key=value:NoSchedule
```

Lệnh trên sẽ đưa taint vào node ```node1``` (nghĩa là đánh dấu node 1 là bị lỗi/hư hỏng). Taint có key tên là ```key```, giá trị là ```value``` và hiệu ứng (effect) taint là ```NoSchedule```. Điều này có nghĩa là không có pod nào có thể lập lịch trên ```node1``` trừ khi nó có toleration (mức độ chịu đựng/chấp nhận) phù hợp.

Để loại bỏ taint đã được thêm bởi lệnh trên, ta có thể chạy lệnh:

```sh
kubectl taint nodes node1 key:NoSchedule-
```

Ta chỉ định toleration cho một pod trong PodSpec. Cả 2 toleration sau đều "khớp" với taint được tạo ra bởi lệnh ```kubectl taint``` ở trên, và do đó một pod có bất kỳ toleration nào bên dưới sẽ có thể lập lịch trên ```node1```

```sh
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

```sh
tolerations:
- key: "key"
  operator: "Exists"
  effect: "NoSchedule"
```

Ví dụ 1 pod sử dụng toleration như sau:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  tolerations:
  - key: "example-key"
    operator: "Exists"
    effect: "NoSchedule"
```

Giá trị mặc định cho ```operator``` là ```Equal```.

Một toleration "khớp" với taint nếu các **key** là giống nhau và các hiệu ứng (**effect**) cũng giống nhau, và:
- ```operator``` là ```Exists``` (trong trường hợp đó không nên chỉ định ```value```), hoặc
- ```operator``` là ```Equal``` và các ```value``` là bằng nhau

Ví dụ trên sử dụng ```effect``` là ```NoSchedule```. Ngoài ra, ta có thể sử dụng hiệu ứng (effect) ```PreferNoSchedule```. Đây là phiên bản "ưu tiên" hoặc bản "mềm" của ```NoSchedule``` - hệ thống sẽ cố gắng tránh đặt pod để nó không phải tolerate taint trên node, nhưng nó không bắt buộc. Loại ```effect``` thứ 3 là ```NoExecute```, loại này sẽ được đề cập sau.

Ta có thể đặt nhiều taint trên cùng một node và nhiều toleration trên cùng 1 pod. Cách K8s xử lý nhiều taint và toleration giống như một bộ lọc: *bắt đầu với tất cả các taint của một node, sau đó bỏ qua những taint mà pod có toleration phù hợp (khớp); đối với các taint còn lại không bị bỏ qua (un-ignored - nghĩa là không nằm trong danh sách toleration của pod), nó sẽ xem xét các hiệu ứng (effect) được chỉ định trên pod*. Cụ thể:
- Nếu có ít nhát một taint chưa bị bỏ qua (un-ignored) với effect là ```NoSchedule``` thì K8s sẽ không lập lịch pod trên node đó
- Nếu không có taint chưa bị bỏ qua (un-ignored) nào với effect ```NoSchedule``` nhưng có ít nhất một taint chưa bị bỏ qua (un-ignored) với hiệu ứng (effect) ```PreferNoSchedule``` thì K8s sẽ cố gắng không lập lịch pod trên node
- Nếu có ít nhất một taint chưa bị bỏ qua với effect là ```NoExecute``` thì pod sẽ bị thu hồi/trục xuất khỏi node (nếu nó đã chạy trên node) và sẽ không được lập lịch vào node (nếu nó chưa chạy trên node)

Ví dụ, ta đánh dấu taint của 1 node như sau:

```sh
kubectl taint nodes node1 key1=value1:NoSchedule
kubectl taint nodes node1 key2=value1:NoExecute
kubectl taint nodes node1 key2=value2:NoSchedule
```

Và có 1 pod với 2 toleration như sau:

```sh
tolerations:
- key: "key1"
  operator: "Equal"
  value: "value1"
  effect: "NoSchedule"
- key: "key2"
  operator: "Equal"
  value: "value1"
  effect: "NoExecute"
```

Trong trường hợp này, pod sẽ không thể lập lịch trên node, vì không có toleration nào khớp với taint thứ 3. Nhưng nó sẽ tiếp tục chạy nếu nó đã chạy trên node tại thời điểm taint được thêm vào, bởi vì taint thứ 3 là taint duy nhất trong 3 taint không được tolerate bởi pod.

Thông thường, nếu một taint có hiệu ứng (effect) ```NoExecute``` được thêm vào một node thì bất kỳ pod nào không tolerate được taint đó sẽ bị trục xuất ngay lập tức và pod tolerate được taint sẽ không bao giờ bị trục xuất. Tuy nhiên, 1 toleration với effect ```NoExecute``` có thể chỉ định một trường ```tolerationSeconds``` tùy chọn quy định thời gian pod vẫn sẽ giữ liên kết (bound) với node sau khi taint được thêm vào. Ví dụ:

```sh
tolerations:
- key: "key1"
  operator: "Equal"
  value: "value1"
  effect: "NoExecute"
  tolerationSeconds: 3600
```

Có nghĩa là nếu pod này đang chạy với một taint khớp được thêm vào node thì pod vẫn sẽ bound với node trong 3600s trước khi bị trục xuất. Nếu taint bị loại bỏ trước thời điểm đó thì pod vẫn sẽ ở lại node.

## Use Case

Taints và toleration là một cách linh hoạt để điều khiển các pod tránh xa các node hoặc thu hồi các pod không nên chạy ở node nào đó. Một số trường hợp sử dụng có thể là:
- **Các node chuyên dụng:** nếu ta muốn dành riêng một tập hợp các node cho một nhóm người dùng cụ thể sử dụng, ta có thể thêm một taint cho các node đó (giả sử ```kubectl taint nodes nodename dedicated=groupName:NoSchedule```) và sau đó thêm toleration tương ứng vào pod của chúng (điều này sẽ được thực hiện dễ dàng nhất bằng cách viết một [admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/) tùy biến). Các pod có toleration sau đó sẽ được phép sử dụng các node bị đánh dấu taint ```dedicated``` cũng như bất kỳ node nào khác trong cluster. Nếu ta muốn dành riêng các node cho chúng và đảm bảo chúng chỉ sử dụng các node được dành riêng đó thì ta nên thêm một label tương tự như taint vào cùng một tập hợp các node (ví dụ: ```dedicated=groupName```) và admission controller nên thêm bổ sung một node affinity để yêu cầu các pod chỉ có thể lập lịch trên các node được gắn label ```dedicated=groupName```.
- **Các node có phần cứng đặc biệt:** Trong một cluster có một tập hợp nhỏ các node với phần cứng chuyên dụng (ví dụ: GPU) thì ta nên đảm bảo giữ các pod không cần sử dụng phần cứng chuyên dụng khỏi các node đó, để dành chỗ cho các pod đến sau cần phần cứng chuyên dụng. Điều này có thể được thực hiện bằng cách thêm taint vào các node có phần cứng chuyên dụng (ví dụ: ```kubectl taint nodes nodename special=true:NoSchedule``` hoặc ```kubectl taint nodes nodename special=true:PreferNoSchedule```) và thêm toleration tương ứng vào các pod sử dụng phần cứng đặc biệt. Như trong trường hợp sử dụng các node chuyên dụng ở trên, có lẽ sẽ dễ dàng nhất để áp dụng toleration bằng cách sử dụng admission controller tùy biến. Ví dụ: ta nên sử dụng ```Tài nguyên mở rộng``` để đại diện (biểu diễn) cho phần cứng đặc biệt, thêm taint vào các node có phần cứng đặc biệt của ta bằng tên của tài nguyên mở rộng và chạy ```ExtendedResourceToleration``` admission controller. Bây giờ, vì các node đã bị đánh dấu taint nên không có pod nào với toleration phù hợp sẽ được lập lịch trên chúng. Nhưng khi ta gửi/tạo (submit) một pod có yêu cầu tài nguyên mở rộng thì ```ExtendedResourceToleration``` sẽ tự động thêm toleration chính xác vào pod và pod đó sẽ lập lịch trên các node có phần cứng đặc biệt. Điều này đảm bảo rằng các node có phần cứng đặc biệt được dành riêng cho các pod yêu cầu phần cứng như vậy và ta không phải thêm toleration cho pod của mình theo cách thủ công.
- **Thu hồi/trục xuất dựa trên taint**: Hành vi thu hồi có thể cấu hình được theo từng pod khi có sự cố trên node sẽ được mô tả trong phần sau.

## Thu hồi/trục xuất dựa trên Taint (từ bản 1.18 trở đi)

Hiệu ứng (effect) ```NoExecute``` của taint như được đề cập ở trên sẽ ảnh hưởng đến các pod đã chạy trên node như sau:
- Các pod không tolerate được taint sẽ bị thu hồi ngay lập tức
- Các pod có thể tolerate được taint mà không chỉ định ```tolerationSeconds``` trong spec toleration của chúng sẽ giữ liên kết mãi mãi, ngược lại nếu có ```tolerationSeconds``` thì sẽ chỉ bound trong khoảng thời gian chỉ định

Node controller sẽ tự động đánh dấu 1 node khi các điều kiện nhất định là đúng. Các taint sau được tích hợp sẵn:
- ```node.kubernetes.io/not-ready```: Node chưa sẵn sàng. Điều này tương ứng với NodeCondition ```Ready``` là ```False```
- ```node.kubernetes.io/unreachable```: Không thể truy cập node từ Node controller. Điều này tương ứng với NodeCondition ```Ready``` là ```Unknown```
- ```node.kubernetes.io/out-of-disk```: Node bị hết dung lượng lưu trữ trên đĩa
- ```node.kubernetes.io/memory-pressure```: Node sắp hết bộ nhớ
- ```node.kubernetes.io/network-unavailable```: Mạng của Node không khả dụng
- ```node.kuberentes.io/unschedulable```: Node không thể lập lịch được
- ```node.cloudprovider.kubernetes.io/uninitialized```: Khi kubelet được khởi động với nhà cung cấp đám mây "bên ngoài", taint này được thiết lập trên một node để đánh dấu nó là không sử dụng được. Sau khi controller từ cloud-controller-manager khởi tạo node này thì kubelet sẽ loại bỏ taint này.

Trong trường hợp một node bị thu hồi thì node controller hoặc kubelet sẽ thêm các taint phù hợp với effect ```NoExecute```. Nếu tình trạng lỗi trở lại bình thường thì node controller hoặc kubelet có thể loại bỏ (các) taint có liên quan đó.

Ta có thể chỉ định ```tolerationSeconds``` cho một Pod để xác định thời gian Pod đó vẫn giữ liên kết với một Node bị lỗi hoặc không phản hồi.

Ví dụ: ta có thể muốn giữ một ứng dụng có nhiều trạng thái cục bộ luôn liên kết (bound) với node trong thời gian dài trong trường hợp mạng bị phân vùng (bị lỗi) với hy vọng rằng lỗi mạng sẽ phục hồi và do đó có thể tránh được việc thu hồi/trục xuất pod. Toleration mà ta thiết lập cho Pod đó có thể giống như sau:

```sh
tolerations:
- key: "node.kubernetes.io/unreachable"
  operator: "Exists"
  effect: "NoExecute"
  tolerationSeconds: 6000
```

*Lưu ý là khi gặp sự cố về mạng thì kubernetes sẽ tự động thêm 2 toleration là ```node.kubernetes.io/not-ready``` và ```node.kubnernetes.io/unreachable``` với ```tolerationSeconds=300``` vào các pod trừ khi ta thiết lập toleration đó một cách tường minh*

Các **DaemonSet** pods được tạo ra với ```NoExecute``` toleration cho các taint sau mà không có ```tolerationSeconds```:
- ```node.kubernetes.io/unreachable```
- ```node.kubernetes.io/not-ready```

Điều này đảm bảo rằng các DaemonSet pod không bao giờ bị thu hồi do những vấn đề này.

## Đánh dấu Taint cho Node theo Condition

Node lifecycle controller (Bộ điều khiển vòng đời của node) sẽ tự động tạo ra các taint tương ứng với condition của node với effect ```NoSchedule```. Tương tự như vậy, Scheduler không kiểm tra các tình trạng (condition) của Node; thay vào đó scheduler sẽ kiểm tra Taints. Điều này đảm bảo rằng các tình trạng của Node không ảnh hưởng đến những gì sẽ được lập lịch trên Node. Người dùng có thể chọn bỏ qua một số vấn đề của Node (được biểu thị dưới dạng tình trạng của Node) bằng cách thêm toleration phù hợp cho Pod.

DaemonSet controller sẽ tự động thêm các toleration ```NoSchedule``` sau vào tất cả các daemon để ngăn DaemonSets khỏi bị phá vỡ
- ```node.kubernetes.io/memory-pressure```
- ```node.kubernetes.io/disk-pressure```
- ```node.kubernetes.io/out-of-disk``` (chỉ cho các pod quan trọng)
- ```node.kubernetes.io/unschedulable``` (1.10 trở lên)
- ```node.kubernetes.io/network-unavailable``` (chỉ cho host network)

Việc thêm các toleration này sẽ đảm bảo tính tương thích ngược. Ta cũng có thể thêm toleration tùy ý vào DaemonSets.