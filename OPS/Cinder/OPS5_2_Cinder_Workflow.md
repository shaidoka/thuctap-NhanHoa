# Cinder workflow

## I. Khởi tạo volume mới

![](./images/OPS5_1.png)

Quá trình tạo volume mới trên cinder:

1. Client yêu cầu tạo ra 1 Volume thông qua việc gọi REST API (Client cũng có thể sử dụng tiện ích CLI của python-client)

2. Cinder-api thực hiện xác nhận hợp lệ yêu cầu thông tin người dùng mỗi khi xác nhận được một message được gửi lên từ hàng chờ AMQP để xử lý

3. Cinder-volume đưa message ra khỏi hàng đợi, gửi thông báo tới cinder-scheduler để báo cáo xác định backend cung cấp volume

4. Cinder-scheduler thực hiện quá trình báo cáo sẽ đưa thông báo ra khỏi hàng đợi, tạo danh sách các ứng viên dựa trên trạng thái hiện tại và yêu cầu tạo volume theo tiêu chí như kích thước, vùng sẵn có, loại volume (bao gồm cả thông số kỹ thuật bổ sung)

5. Cinder-volume thực hiện quá trình đọc message phản hồi từ cinder-scheduler từ hàng đợi. Lặp lại qua các danh sách ứng viên bằng cách gọi backend driver cho đến khi thành công

6. Storage Cinder tạo ra volume được yêu cầu thông qua tương tác với hệ thống lưu trữ con (phụ thuộc vào cấu hình và giao thức)

7. Cinder-volume thực hiện quá trình thu thập dữ liệu và metadata volume và thông tin kết nối để trả lại thông báo đến AMQP

8. Cinder-api thực hiện quá trình đọc message phản hồi từ hàng đợi và đáp ứng tới client

9. Client nhận được thông tin bao gồm trạng thái của yêu cầu tạo, Volume UUID,...

## II. Attach volume

![](./images/OPS5_2.png)

1. Client yêu cầu attach volume thông qua Nova REST API (Client có thể sử dụng tiện ích CLI của python-novaclient)

2. Nova-api thực hiện quá trình xác nhận yêu cầu và thông tin người dùng. Một khi đã được xác thực, gọi API Cinder để có được thông tin kết nối cho volume được xác định

3. Cinder-api thực hiện quá trình xác nhận yêu cầu hợp lệ và thông tin người dùng hợp lệ. Một khi được xác nhận, một message sẽ được gửi đến người quản lý volume thông qua AMQP

4. 