# Phân phối tài nguyên động

Dynamic resource allocation là 1 API mới cho việc yêu cầu và chia sẻ tài nguyên giữa các pod và các container trong nội tại 1 pod. Nó là 1 sự tổng quát hóa của persistent volumes API cho các tài nguyên chung. Trình điều khiển tài nguyên của bên thứ 3 sẽ chịu trách nhiệm cho việc theo dõi và phân phối tài nguyên. Các loại tài nguyên khác nhau lại hỗ trợ các kiểu tham số tùy chọn cho việc xác định yêu cầu và khởi tạo khác nhau.

## Trước khi bắt đầu

K8s v1.27 bao gồm API cấp cụm hỗ trợ cho việc phân phối tài nguyên động, nhưng nó cần phải được kích hoạt rõ ràng. Ta cũng phải cài đặt 1 tài nguyên driver cho tài nguyên cụ thể mà ta dự định sẽ quản lý với API này.

## API

API group ```resource.k8s.io/v1alpha2``` cung cấp 4 loại mới:
- **ResourceClass:** Định nghĩa resource driver sẽ xử lý 1 loại resource nào và cung cấp các tham số chung cho nó. ResourceClasses được tạo bởi người quản trị cluster khi cài đặt 1 resource driver.
- **ResourceClaim:** Định nghĩa 1 resource cụ thể mà cần thiết bởi 1 workload. Được tạo bởi 1 user (vòng đời được quản lý thủ công, có thể được chia sẻ giữa các Pod khác nhau) hoặc cho pods riêng lẻ bởi control plane dựa trên 1 ResourceClaimTemplate (vòng đời tự động, thường được sử dụng bởi chỉ 1 pod).
- **ResourceClaimTemplate:** Định nghĩa trường ```spec``` và 1 vài ```metadata``` cho việc tạo lập ResourceClaim. Được tạo bởi 1 người dùng khi deploy 1 workload.
- **PodSchedulingContext:** Sử dụng nội bộ bởi control plane và resource drivers để định vị pod scheduling khi ResourceClaim cần phải phân phối 1 pod.

Các tham số cho ResourceClass và ResourceClaim được lưu trữ trong các object riêng biệt, thường là sử dụng loại được định nghĩa bởi 1 CRD mà được tạo khi cài đặt 1 resource driver.

PodSpec ```core/v1``` định nghĩa ResourceClaims mà cần thiết cho 1 Pod trong 1 trường ```resourceClaims``` mới. Các danh mục trong danh sách đó tham chiếu đến cả ResourceClaim hoặc ResourceClaimTemplate. Khi tham chiếu 1 ResourceClaim, tất cả pod sử dụng PodSpec này (ví dụ, trong 1 deployment hay StatefulSet) chia sẻ cùng 1 ResourceClaim. Khi tham chiếu 1 ResourceClaimTemplate, mỗi Pod sẽ lấy instance của nó.

Danh sách ```resources.claims``` cho container resource định nghĩa khi nào 1 container truy nhập vào những resource instance này, thứ khiến nó có thể chia sẻ tài nguyên giữa 1 hoặc nhiều container.

Dưới đây là 1 ví dụ cho 1 resource driver giả định. 2 ResourceClaim object sẽ được tạo cho mỗi Pod và container sẽ truy nhập vào 1 trong số chúng.

```sh
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClass
name: resource.example.com
driverName: resource-driver.example.com
---
apiVersion: cats.resource.example.com/v1
kind: ClaimParameters
name: large-black-cat-claim-parameters
spec:
  color: black
  size: large
---
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClaimTemplate
metadata:
  name: large-black-cat-claim-template
spec:
  spec:
    resourceClassName: resource.example.com
    parametersRef:
      apiGroup: cats.resource.example.com
      kind: ClaimParameters
      name: large-black-cat-claim-parameters
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-cats
spec: 
  containers:
  - name: container0
    image: ubuntu:20.04
    command: ["sleep", "9999"]
    resources:
      claims:
      - name: cat-0
  - name: container1
    image: ubuntu:20.04
    command: ["sleep","9999"]
    resources:
      claims:
      - name: cat-1
  resourceClaims:
  - name: cat-0
    source: 
      resourceClaimTemplateName: large-black-cat-claim-template
  - name: cat-1
    source:
      resourceClaimTemplateName: large-black-cat-claim-template
```

## Lập lịch

Trong tương phản với những tài nguyên động (CPU, RAM) và tài nguyên mở rộng (được quản lý bởi 1 device plugin, quảng bá bởi kubelet), trình lập lịch sẽ không biết tài nguyên động nào là khả dụng trong 1 cluster và cách chúng có thể được chia ra để thỏa mãn yêu cầu của ResourceClaim cụ thể. Resource driver chịu trách nhiệm cho điều đó. Chúng đánh dấu ResourceClaim là "allocated" mỗi khi resource cho nó được phân phối. Điều này cũng nói cho trình lập lịch biết nơi mà ResourceClaim khả dụng trong 1 cluster.

ResourceClaims có thể được phân bổ ngay khi chúng được tạo ra mà không cần quan tâm Pod nào sẽ sử dụng chúng. Theo mặc định thì sự phân phối sẽ được trì hoãn cho tới khi 1 Pod được lập lịch mà cần đến ResourceClaim (ví dụ: "wait for first consumer").

Trong chế độ đó, trình lập lịch kiểm tra tất cả ResourceClaim cần bởi 1 Pod và tạo 1 PodScheduling object nơi mà nó thông báo với resource driver chịu trách nhiệm cho những ResourceClaim đó về các node mà trình lập lịch cho rằng phù hợp với Pod. Resource driver phản hồi bằng việc loại trừ những node mà không còn đủ tài nguyên của driver. Một khi trình lập lịch có được thông tin đó, nó chọn 1 node và lưu trữ lựa chọn trong 1 PodScheduling object. Resource driver sau đó phân phối ResourceClaim của chúng, nhờ đó mà resource sẽ được khả dụng ở trên node. Khi đã hoàn thành công đoạn này, Pod sẽ được lập lịch.

Như một phần của tiến trình này, ResourceClaim cũng được dành riêng cho Pod. Hiện tại ResourceClaim có thể được sử dụng độc quyền bởi 1 pod hoặc bao nhiêu pod đều được.

1 tính năng quan trọng là Pod sẽ không được lập lịch đến 1 node nếu tất cả resource của chúng không được allocate và reserve. Điều này giúp tránh viễn cảnh khi 1 Pod được lập lịch trên 1 node và sau đó không thể chạy được ở đó, điều này rất tệ vì 1 pending Pod cũng chặn tất cả resource khác như RAM và CPU mà được thiết lập bên cạnh đó.

## Monitoring resource

Kubelet cung cấp 1 gRPC service để kích hoạt tìm kiếm dynamic resource của các Pod đang chạy. Chi tiết về gRPC endpoint được nhắc đến ở [resource allocation reporting](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/#monitoring-device-plugin-resources)

## Hạn chế

Scheduler plugin bắt buộc phải tham gia vào quá trình lập lịch Pod mà sử dụng ResourceClaim. Bỏ qua trình lập lịch bởi cấu hình trong trường ```nodeName``` sẽ dẫn đến pod đó từ chối khởi động vì rõ ràng ResourceClaim không được dành riêng/phân bổ.

## Kích hoạt dynamic resource allocation

Dynamic resource allocation là 1 tính năng alpha và chỉ được kích hoạt khi ```DynamicresourceAllocation``` feature gate và ```resource.k8s.io/v1alpha2``` API group được kích hoạt.

Một cách kiểm tra nhanh xem 1 K8s cluster có hỗ trợ tính năng này không là liệt kê resourceClass object bằng lệnh

```sh
kubectl get resourceclasses
```

Nếu cluster hỗ trợ dynamic resource allocation thì kết quả trả về sẽ là 

```sh
No resources found
```

Ngược lại, nếu không hỗ trợ sẽ là

```sh
error: the server doesn't have a resource type "resourceclasses"
```

Cấu hình mặc định của kube-scheduler đã kích hoạt plugin "DynamicResources" nếu và chỉ nếu feature gate được kích hoạt và khi sử dụng v1 configuration API. Các cấu hình custom có thể cần được modify để bao gồm nó.

Thêm vào đó để kích hoạt tính năng này trong cluster, 1 resource driver cũng phải được cài đặt.