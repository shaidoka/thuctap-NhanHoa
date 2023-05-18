# Tìm hiểu về cấu trúc của Pod

## I. Pod's tatus

Pod status là một trường bên trong manifest của Pod mà chứa các thông tin về Pod sau khi nó được tạo ra, trường Pod status này là một object mà chứa các thông tin sau:
- Địa chỉ IP của Pod và worker node Pod deploy tới
- Thời gian Pod đã được chạy
- Pod's QoS class
- Pod's phase
- Pod's conditions
- Trạng thái của từng container trong Pod

### Pod's phase

Đây là thông tin ta cần quan tâm trong trường status của Pod, trường này sẽ thể hiện cho ta biết Pod đang ở giai đoạn nào trong một life cycle, khi một Pod được tạo ra cho tới khi nó bị xóa đi thì trạng thái của nó sẽ nằm ở 1 trong các giai đoạn sau đây:

![](./images/K8s_Pod_1.png)

- Pending phase: Pod sẽ ở trạng thái Pending cho tới khi nó được schedule tới một worker node và started
- Running phase: Pod sẽ ở trạng thái này khi 1 container trong Pod được running thành công và vẫn duy trì running
- Succeeded phase: Pod sẽ ở trạng thái này khi tất cả container của Pod kết thúc quá trình chạy thành công hoặc/và bị terminate
- Failed phase: Chỉ cần 1 container chạy thất bại thì Pod sẽ ở trạng thái này
- Unknown phase: đây là trạng thái khi mà kubelet ở một worker node không thể gửi report của Pod về cho K8s master

### Pod's conditions

Đây là thuộc tính của Pod mà báo cho ta biết Pod đã đạt đến trạng thái mong muốn hay chưa. Thuộc tính này là một array chứa các conditión của Pod. Có 4 condition như sau:
- PodScheduled: Pod đã được scheduled tới node hay chưa
- Initialized: tất cả các container đã được khởi tạo thành công chưa
- ContainersReady: tất cả các container trong Pod đã chạy xong hết chưa
- Ready: tất cả container Pod đã chạy xcng và có thể nhận request chưa

Từng condition sẽ là một object trong mảng array Pod conditions, với các thuộc tính quan trọng sau:
- Type: tên của condition
- Status: True, False, hoặc Unknown
- Reason: machine readable text chỉ định lý do tại sao condition này pass hoặc không pass
- Message: human readable message chỉ định định lý do chi tiết tại sao condition này pass hoặc không pass

Từng condition này sẽ có message riêng, mà ta sẽ thường xuyên xem trường message này để biết được lý do tại sao một Pod của chúng ta không thể chạy được thành công, rất hữu ích khi ta debug.

Ta có thể list condition của Pod bằng câu lệnh sau:

```sh
kubectl describe po <pod-name> | grep Conditions: -A 5
```

Hiện condition chi tiết:

```sh
kubectl get pods <pod-name> -o json | jq .status.conditions
```

