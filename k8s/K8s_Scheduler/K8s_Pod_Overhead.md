# Pod Overhead

Khi ta chạy pod trên node, chính pod sẽ chiếm 1 lượng tài nguyên hệ thống. Lượng tài nguyên bị chiếm này sẽ được cộng với các tài nguyên cần thiết để chạy (các) container bên trong Pod. **Pod Overhead** là một tính năng để hạch toán các tài nguyên được sử dụng bởi hạ tầng Pod trên nền của các yêu cầu (request) & giới hạn (limit) của container.

Trong K8s, Pod overhead (chi phí hoạt động của pod) được thiết lập tại thời điểm đăng ký tùy theo chi phí (overhead) liên kết với RuntimeClass của Pod

Khi Pod Overhead được bật, chi phí (overhead) sẽ được cộng thêm vào ngoài tổng số yêu cầu tài nguyên của container khi lập lịch cho pod. Tương tự, Kubelet sẽ bao gồm Pod overhead khi xác định kích thước Pod cgroup và khi thực hiện xếp hạng thu hồi/trục xuất Pod

## Kích hoạt Pod Overhead

Ta cần đảm bảo rằng [https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/](feature gate) ```PodOverhead``` được bật (theo mặc định từ 1.18) trên cluster và ```RuntimeClass``` được sử dụng để định nghĩa trường ```overhead```