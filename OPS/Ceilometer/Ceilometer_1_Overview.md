# Telemetry Data Collection service overview

Telemetry Data Collection service cung cấp các tính năng sau đây:

- Thu thập dữ liệu nhanh và hiệu quả về các dịch vụ liên quan đến OpenStack
- Thu thập sự kiện và dữ liệu đo lường bằng việc giám sát các cảnh báo được gửi về từ các service đó
- Gửi dữ liệu đã thu thập về nhiều target bao gồm dữ liệu lưu trữ và hàng đợi message

Dịch vụ Telemetry bao gồm các thành phần sau đây:

- **A compute agent** (ceilometer-agent-compute): Chạy trên mỗi compute node và polls cho resource utilization statistics. Đây là polling agent ```ceilometer-polling``` chạy với tham số ```--polling-namespace compute```
- **A central agent** (ceilometer-agent-notification): Chạy trên 1 server quản lý trung tâm để poll cho resource utilization statistics cho các resources mà không gắn với 1 instances hay compute nodes cụ thể. Nhiều agents có thể được start để service có thể scale theo chiều ngang. Đây thực ra là polling agent ```ceilometer-polling``` chạy với tham số ```--polling-namespace central```
- **A notification agent** (ceilomter-agent-notification): Chạy trên 1 server quản lý trung tâm và sử dụng message từ message queue để xây dựng build event và metering data. Dữ liệu này sau đó được đăng tải thông qua các target đã được định nghĩa. Mặc định, dữ liệu được đưa qua **Gnocchi**

Những dịch vụ này giao tiếp bằng cách sử dụng OpenStack messaging bus. Ceilometer data được thiết kế để đăng tải đến nhiều endpoints khác nhau để phân tích và lưu trữ.

