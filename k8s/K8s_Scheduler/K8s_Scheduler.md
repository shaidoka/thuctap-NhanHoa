# Kubernetes Scheduler

Trong K8s, việc lập lịch (scheduling) đề cập đến việc đảm bảo rằng các Pod được khớp (phù hợp) với các Node để Kubelet có thể chạy chúng

## Tổng quan về scheduling

**Scheduler** (trình lập lịch) theo dõi các Pod mới được tạo ra mà chưa được phân bổ cho Node. Đối với mỗi Pod mà Scheduler phát hiện, **Scheduler sẽ chịu trách nhiệm tìm Node tốt nhất cho Pod đó để chạy**. Scheduler đưa ra quyết định về vị trí này có tính đến các nguyên tắc lập lịch trình được mô tả dưới đây.

Nếu muốn hiểu lý do tại sao các Pod được đặt vào một Node cụ thể hoặc nếu đang định tự triển khai một scheduler tùy biến thì phần này sẽ giúp ta tìm hiểu về cách lập lịch

## Kube-scheduler

**Kube-scheduler** là scheduler (trình lập lịch) mặc định cho K8s và chạy như một phần của control plane. Kube-scheduler được thiết kế để nếu ta muốn và cần, ta có thể viết thành phần lập lịch của riêng mình và sử dụng thành phần đó thay thế.

