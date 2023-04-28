# Báo cáo tìm hiểu K8s 

Dear các anh, trong tuần vừa rồi em tìm hiểu các vấn đề sau:

## Autoscaling

K8s Autoscaling có 3 level scale bao gồm:
- **Vertical Pod Autoscaler**: Scale bằng cách tăng/giảm tài nguyên **yêu cầu** của pod
- **Horizontal Pod Autoscaler**: Scale bằng cách tăng/giảm số lượng pod thực hiện cùng chức năng (chỉ áp dụng với ReplicasController như Deployment hay StatefulSets)
- **Cluster Autoscaler**: Khi scaling, tài nguyên của cluster có thể cạn kiệt, lúc này CA sẽ được sử dụng để tăng/giảm số lượng node. Cluster Autoscaler được hỗ trợ bởi các nền tảng Cloud lớn như GKE, GCE, AWS, Azure,....

### 1. Vertical Pod Autoscaler

VPA sẽ scale pod bằng cách thay đổi tài nguyên **requests** và **limits** của pod nhằm giúp chúng được tái tạo hay re-schedule vào 1 node có đủ tài nguyên khả dụng (nếu node hiện tại full tài nguyên), hoặc tính toán lại **limits** để phù hợp hơn với nhu cầu sử dụng của pod.

Thông số CPU và memory được đưa ra bởi **recommender**, cách mà **recommender** đưa ra những con số này phụ thuộc vào nhiều yếu tố khác nhau

### 2. Horizontal Pod Autoscaler

Không giống như VPA, HPA thay vì tái tạo pod để cấp phát lại tài nguyên phù hợp với nhu cầu. HPA sẽ tạo thêm pod để tăng số lượng pod thực hiện cùng 1 chức năng, từ đó tăng tính sẵn sàng của ứng dụng. Cách tính toán tài nguyên của HPA do đó cũng đơn giản hơn VPA.

HPA so với VPA thì scale được theo nhiều metrics hơn, bao gồm CPU, memory, QPS (query-per-second), RPS (request-per-second),...

Chi tiết về Autoscaling trong K8s cũng như các kết quả kiểm thử được đề cập chi tiết ở [Automatic scaling](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Auto_Scaling.md)

## Persistence Volume

Ngoài ra, trong tuần vừa rồi em có lab thêm về PV/PVC, bao gồm 2 phần chính là NFS và iSCSI

### NFS

Đối với NFS, vẫn giống tuần trước, em có thử làm theo docs của anh Khương tạo PV rồi tạo PVC thì có thể Bound được bình thường.

Tuy nhiên khi dùng NFS provisioner thì lại không thể Bound được PVC (kết quả mong đợi là khi PVC được tạo ra thì PV sẽ được Provisioner tạo tự động và Bind PVC vào).

Chi tiết về quá trình lab tại: [NFS Storage](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Storage/K8s_Storage_NFS.md)

### iSCSI

Tương tự iSCSI, em có thử lab tạo PV và PVC thủ công thì có thể Bind được với nhau. Nhưng khi sử dụng Provisioner thì lại không thể Bind được.

Có thể do cách cấu hình em chưa chính xác chỗ nào đó, em vẫn đang tiếp tục tìm hiểu

Chi tiết về quá trình lab tại: [iSCSI Storage](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Storage/K8s_iSCSI_targetd_provisioner.md)