# Logging trên K8s

Logging, hay middleware logging có thể giúp ích rất nhiều khi cần troubleshoot, statisics, hay thậm chí là các vấn đề liên quan đến security.

Khi cài đặt một ứng dụng lên k8s thì ứng dụng có thể được cấu hình để chạy với nhiều replicas (sử dụng deployment có nhiều pod). Và quan trọng hơn là các pod này được phân bố trên các node một cách tự động do k8s điều phối, trừ khi ta cấu hình node selector. Nhưng việc này cũng không quá phổ biến.

Thông thường, khi cần xem log của 1 pod, ta sẽ sử dụng lệnh ```kubectl logs```, tuy nhiên vấn đề là pod đó có thể có nhiều replicas.

Hoặc nếu muốn kiểm tra log file trong pod hoặc container, ta sẽ phải kết nối vào pod rồi mới kiểm tra được file.

Trong trường hợp pod được tạo lại vì 1 lý do nào đó, các log cũ sẽ hoàn toàn biến mất. 

Để giải quyết các vấn đề trên, trong bài này sẽ giới thiệu về ELK - 1 giải pháp ghi log tập trung vô cùng phổ biến ở thời điểm hiện tại.

## Giới thiệu

Hiện tại có 1 vài giải pháp logging phổ biến như ELK, EFK, hay Promtail/Loki của Grafana. Về cơ bản thì ý tưởng của chúng không khác nhau là mấy, mỗi nhà phát triển sẽ có những đặc thù riêng. 

Trong chủ đề về Logging trong K8s, chúng ta sẽ bàn luận về ELK và EFK.

### ELK (Elasticsearch - Logstash - Kibana)

ELK là bộ giải pháp của Elastic, chi tiết về mô hình đã được giới thiệu ở 1 bài viết khác, tuy nhiên chúng ta vẫn sẽ điểm qua 1 vài thành phần chính của nó:

- **Beats:** (filebeat, metricbeat,...) là các thành phần đóng vai trò lấy log từ target (ở đây là lấy log trên K8s). Output của beats có thể là Logstash (để phân tích và tổng hợp dữ liệu log trước khi lưu và elasticsearch) hoặc có thể đẩy trực tiếp vào Elastic search.
- **Logstash:** Đóng vai trò là Data Aggregation & Data Processing trong luồng logging này. Trên logstash ta có thể định nghĩa các pipeline để xử lý dữ liệu đầu vào (input) để đi qua filter-plugin. Đơn giản là tùy chọn từng loại log input để thực hiện thêm các trường mới, hoặc xử lý các dữ liệu log không có cấu trúc thành các dạng log có cấu trúc bằng pattern (thường là regex). Đây cũng là công đoạn cấu hình phức tạp nhất của hệ thống logging.
- **Elastic Search:** Là nơi lưu trữ log vào các index phục vụ cho việc query dữ liệu sau này.
- **Kibana:** Làm nhiệm vụ query dữ liệu từ Elastic search và hiển thị theo các template một cách trực quan theo dạng list hoặc graph tùy nhu cầu của người dùng.

### EFK (Elasticsearch - Fluentd - Kibana)

EFK là bộ giải pháp của **Traesure Data**. Mô hình của EFK thì không khác so với ELK là mấy, ta có thể đề cập đến 2 điểm nổi bật của EFK là:
- **Fluentbit** và **Fluentd** có hiệu suất rất tốt mà lại nhẹ nhàng
- Fluentd nằm dưới sự quản lý của CNCF, do đó xu hướng logging trên k8s sẽ ưu tiên dùng EFK hơn ELK

Tuy nhiên, nếu ta quen với việc dùng bộ phần mềm nào thì nên sử dụng nó, thay vì chạy theo công nghệ.

Các thành phần chính của EFK bao gồm:

- **Fluentbit/Fluentd:** Cả Fluentbit và Fluentd đều có thể thực hiện việc Data Collection, tức là lấy log từ K8s. Tuy nhiên khác biệt lớn nhất giữa chúng là Fluentbit được thiết kế chuyên biệt cho việc lấy dữ liệu. Ánh xạ sang ELK thì Fluentbit tương đương với Filebeat còn Fluentd tương đương với Logstash.
- **Elastic search:** Là nơi lưu trữ log vào các index phục vụ cho việc query dữ liệu sau này.
- **Kibana:** Làm nhiệm vụ query dữ liệu từ Elastic search và hiển thị theo các template một các trực quan theo dạng list hoặc graph tùy theo nhu cầu sử dụng của người dùng.

### Bài toán thực tế

Hệ thống logging phải giải quyết được các vấn đề sau:
- Hệ thống có sử dụng một vài opensource như vernemq, kafka và chỉ lưu dữ liệu trong vòng 7 ngày
- Các service được triển khai dưới dạng deployment và lưu dữ liệu trong 30 ngày
- Các dữ liệu log không cần thực hiện parsing, tuy nhiên vẫn cần xây dựng hệ thống phân tích log, các rule parsing sẽ được bổ sung sau
- Thực hiện khai báo các template để query dữ liệu log của từng service trên kibana