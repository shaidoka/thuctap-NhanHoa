# Chuẩn bị volume động

Dynamic Volume Provisioning cho phép storage volume có được tạo tự động. Nếu không có dynamic provisioning, người quản trị cluster phải thực hiện các lệnh gọi thủ công đến cloud hay storage provider để tạo những storage volume mới, và sau đó tạo ```PersistentVolume objects``` để sử dụng chúng trong K8s. Tính năng dynamic provisioning loại bỏ nhu cầu về pre-provision storage. Thay vào đó, nó tự động cung cấp storage khi được yêu cầu bởi người dùng.

## Background

Sự cải thiện của dynamic volume provisioning dựa trên đối tượng API ```StorageClass``` từ API group ```storage.k8s.io```. 1 cluster administrator có thể định nghĩa nhiều ```StorageClass``` objects tùy ý, mỗi chúng lại chỉ định 1 volume plugin (hay provisioner) mà provision 1 volume và 1 tập các tham số cần đưa vào provisioner đó khi provisioning, 1 cluster administrator có thể định nghĩa và expose multiple flavors của storage (từ cùng hoặc khác storage system) bên trong 1 cluster, mỗi trong số chúng có 1 tập tham số tùy chỉnh. Thiết kế này cũng đảm bảo rằng người dùng cuối không phải bận tâm về sự phức tạp và cách thức mà storage được provisione, nhưng vẫn có khả năng lựa chọn từ nhiều tùy chọn storage.

## Enabling Dynamic Provisioning

Để kích hoạt dynamic provisioning, 1 cluster administrator cần pre-create 1 hay nhiều StorageClass objects cho người dùng. StorageClass objects định nghĩa provisioner nào nên được sử dụng và tham số gì nên được đưa vào provisioner đó khi thực hiện dynamic provisioning. Tên của 1 StorageClass phải là 1 DNS subdomain name.

Phần cấu hình sau tạo 1 SC tên "slow" mà cung cấp standard persistent disk

```sh
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: slow
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-standard
```

Phần cấu hình sau tạo 1 storage class tên "fast" mà cung cấp SSD persistent disk

```sh
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
```

## Sử dụng Dynamic Provisioning

Người dùng yêu cầu dynamically provisioned storage bằng cách thêm 1 SC trong ```PersistentVolumeClaim``` của họ. Trước phiên bản K8s 1.6, điều này được làm thông qua ```volume.beta.kubernetes.io/storage-class``` annotation. Tuy vậy, annotation này đã không còn sử dụng từ 1.9. Người dùng giờ có thể và nên thay thế nó bằng trường ```storageClassName``` của đối tượng ```PersistentVolumeClaim```. Giá trị của trường này phải khớp với tên của ```StorageClass``` được cấu hình bởi administrator.

Để lựa chọn ```fast``` storageClass, ví dụ:

```sh
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claim1
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast
  resources:
    requests:
      storage: 30Gi
```

## Hành vi mặc định

Dynamic provisioning có thể được kích hoạt trên 1 cluster mà tất cả claim được cấp động nếu không storage class nào được chỉ định. Người quản trị có thể làm điều này bằng cách:
- Đánh dấu 1 SC là ```default```
- Đảm bảo ```DefaultStorageClass admission controller``` được kích hoạt trên API server

1 administrator có thể đánh dấu 1 SC cụ thể là mặc định bằng cách thêm annotation ```storageclass.kubernetes.io/is-default-class``` vào nó. Khi StorageClass mặc định tồn tại trong 1 cluster và user tạo ra ```PersistentVolumeClaim``` với trường ```storageClassName``` không được chỉ định, ```DefaultStorageClass``` admission controller sẽ tự động thêm trường ```StorageClassName``` trỏ vào storage class mặc định.

Lưu ý rằng chỉ có thể có tối đa 1 loại sc mặc định trên 1 cluster. Nếu có nhiều hơn thì PVC mà không có trường ```storageClassName``` rõ ràng sẽ không được tạo ra

## Nhận diện topology

Trong cluster nhiều zone, Pod có thể được trải rộng trên các zone trong 1 Region. Các hệ thống lưu trữ một zone nên được provision trong Zone nơi Pod được lập lịch. Điều này có thể được thực hiện bằng cách thiết lập [Volume Binding Mode](https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode)