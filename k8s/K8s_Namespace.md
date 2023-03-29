# Namespace trong K8s

Trong các phần trước, chúng ta đã tìm hiểu về nguồn gốc ra đời, kiến trúc các thành phần và cách thức cài đặt một cụm hạ tầng K8s bằng kubeadm. Bây giờ chúng ta sẽ cùng tìm hiểu một số khái niệm cơ bản trong Kubernetes để giúp quản trị và vận hành một hạ tầng Kubernetes.

Giả sử bạn bạn được bàn giao một hạ tầng K8s để vận hành, quản trị thì bạn sẽ cần tiếp cận cái gì đầu tiên?

Tùy vào kiến thức nền và vị trí công việc của mỗi người mà có các câu trả lời khác nhau. Nếu bạn được bàn giao tài khoản quản trị K8s cluster, bạn sẽ cần biết hạ tầng K8s được cài đặt bằng cách thức nào, có HA hay không, mức độ khai thác tài nguyên ra sao, đang dùng storage gì, tích hợp với các hệ thống nào, có bao nhiêu ứng dụng đang triển khai trên đó, triển khai trên các namespace nào,... Còn nếu bạn là người triển khai ứng dụng thì bạn quan tâm tới việc đang bị limit resource ra sao, tài khoản được cấp quyền gì, có storageclass không, có những policy nào phải tuân thủ, namespace được cấp tên là gì,...

Bài này chúng ta sẽ cùng nhau tìm hiểu một khái niệm đầu tiên khi làm việc với Kubernetes, đó là namespace. 

Các bạn hẳn rất quen thuộc với thuật ngữ folder (thư mục) trong hệ điều hành Windows, Linux, vậy trong Kubernetes có thể hiểu về mặt logic thì namespace như một folder. Nhưng folder này trong K8s nó trải dài trên tất cả các node. Bạn không thể tạo được 2 tập tin (file) có trùng tên trong cùng một thư mục (folder), thì tính chất này cũng tương tự trong namespace, nhưng thay vì là tập tin thì trong namespace sẽ được đặt các resource.

**Resource:** được hiểu là một loại tài nguyên được kubernetes quản lý như pods, volume, service, serviceaccount, configMap, secret,... Các resource này sẽ được làm rõ ở bài tiếp theo. Bản thân namespace cũng được coi là một resource

![](./images/K8s_Namespace_1.png)

Theo như hình trên, nhìn tổng quát từ bên ngoài Kubernetes vào thì sẽ thấy:
- 1 Kubernetes Cluster sẽ bao gồm rất nhiều node (master, worker)
- Một namespace trong K8s cluster sẽ nằm trên tất cả các node
- Mọi ứng dụng khi triển khai trong K8s phải thuộc vào một namespace nào đó

Namespace là một thành phần logic mà tất cả mọi người đều phải hiểu và tương tác nếu làm việc với K8s

Mặc định khi cài đặt xong một cụm K8s ta sẽ có 3 namespace là: ```kube-system```, ```default``` và ```public```.

Nếu bạn đang nắm quyền quản trị (admin) thì bạn có thể tạo một namespace tên là test bằng lệnh

```sh
kubectl create namespace test
```

Hay viết tắt là ```ns```. Kiểm tra các namespace đang có trong cluster bằng lệnh

```sh
kubectl get ns
```

Khi muốn tương tác với các resource trong namepsace thì các bạn thêm tham số ```-n <tên_ns>``` vào câu lệnh, ví dụ

```sh
kubectl -n kube-system get all
```

Để xem những resource nào thuộc K8s nằm trong phạm vi của namespace thì ta dùng lệnh

```sh
kubectl api-resources --namespaced=true
```

Ngoài ra, còn một số khái niệm khác liên quan tới namespace nữa như thiết lập label, phân giải service name giữa các namespace khi kết kết nối,...

**Tóm tắt:**
- Namespace là một thành phần logic được K8s sử dụng để xác định phạm vi quản lý các resource
- Một resource trong cùng một namespace không thể đặt tên giống nhau