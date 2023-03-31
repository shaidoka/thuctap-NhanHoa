# Kubernetes Scheduler

Trong K8s, việc lập lịch (scheduling) đề cập đến việc đảm bảo rằng các Pod được khớp (phù hợp) với các Node để Kubelet có thể chạy chúng

## Tổng quan về scheduling

**Scheduler** (trình lập lịch) theo dõi các Pod mới được tạo ra mà chưa được phân bổ cho Node. Đối với mỗi Pod mà Scheduler phát hiện, **Scheduler sẽ chịu trách nhiệm tìm Node tốt nhất cho Pod đó để chạy**. Scheduler đưa ra quyết định về vị trí này có tính đến các nguyên tắc lập lịch trình được mô tả dưới đây.

Nếu muốn hiểu lý do tại sao các Pod được đặt vào một Node cụ thể hoặc nếu đang định tự triển khai một scheduler tùy biến thì phần này sẽ giúp ta tìm hiểu về cách lập lịch

## Kube-scheduler

**Kube-scheduler** là scheduler (trình lập lịch) mặc định cho K8s và chạy như một phần của control plane. Kube-scheduler được thiết kế để nếu ta muốn và cần, ta có thể viết thành phần lập lịch của riêng mình và sử dụng thành phần đó thay thế.

Đối với mỗi pod được tạo ra hoặc các pod chưa được lên lịch khác, kube-scheduler lựa chọn một node tối ưu để chúng chạy trên đó. Tuy nhiên, mỗi container trong pod có các yêu cầu khác nhau về tài nguyên và mỗi pod cũng có các yêu cầu khác nhau. Do đó, các node hiện có cần được lọc theo các yêu cầu lập lịch cụ thể.

Trong một cluster, các node đáp ứng các yêu cầu lập lịch cho một pod được gọi là các **node khả thi**. Nếu không có node nào phù hợp, pod vẫn chưa được lập lịch cho đến khi scheduler có thể tìm thấy node phù hợp để đặt pod.

Scheduler tìm các Node khả thi cho một Pod và sau đó chạy một tập hợp các hàm để chấm điểm (score) các Node khả thi và chọn một Node có điểm cao nhất trong số các Node khả thi để chạy Pod. Sau đó, scheduler thông báo cho API server về quyết định này trong một process được gọi là **binding** (liên kết).

Các yếu tố cần tính đến khi đưa ra quyết định lập lịch bao gồm các yêu cầu về tài nguyên cá nhân và tập thể, các ràng buộc về phần cứng/phần mềm/chính sách, đặc tả về affinity và anti-affinity, vị trí dữ liệu, sự giao thoa giữa các workload,...

## Lựa chọn Node trong kube-scheduler

Kube-scheduler lựa chọn một node cho pod trong một thao tác gồm 2 bước:
- Lọc (filter)
- Chấm điểm (score)

Bước **lọc** sẽ tìm kiếm tập hợp các node nơi có thể lập lịch cho Pod. Ví dụ: bộ lọc PodFitsResources sẽ kiểm tra xem Node ứng viên có đủ tài nguyên khả dụng để đáp ứng các yêu cầu tài nguyên cụ thể của Pod hay không. Sau bước này, danh sách node có sẵn/khả dụng sẽ chứa bất kỳ node nào phù hợp (thường có nhiều hơn 1 node). Nếu danh sách trống (empty), Pod đó chưa thể được lập lịch.

Ở bước **tính điểm**, scheduler sẽ xếp hạng các node còn lại để lựa chọn vị trí phù hợp nhất để đặt pod. Scheduler sẽ cho điểm mỗi Node trong danh sách Node khả dụng, điểm này dựa trên các quy tắc tính điểm đang hoạt động.

Cuối cùng, kube-scheduler phân bổ Pod cho Node có thứ hạng cao nhất. Nếu có nhiều hơn một Node có điểm số bằng nhau, kube-scheduler sẽ chọn ngẫu nhiên một trong những node này.

Có 2 cách được hỗ trợ để cấu hình hành vi lọc và tính điểm của scheduler:
- **Chính sách lập lịch:** cho phép ta cấu hình *Predicates* để lọc và *Priorities* để tính điểm
- **Hồ sơ lập lịch:** cho phép ta cấu hình các Plugin để triển khai các giai đoạn lập lịch khác nhau, bao gồm: ```QueueSort```, ```Filter```, ```Score```, ```Bind```, ```Reserve```, ```Permit``` và các phần khác. Ta cũng có thể cấu hình kube-scheduler để chạy các profile khác nhau.