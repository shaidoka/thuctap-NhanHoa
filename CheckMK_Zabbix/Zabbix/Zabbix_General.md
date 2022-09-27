# Zabbix

Zabbix là 1 công cụ để giám sát hệ thống mạng, các thiết bị mạng, giám sát khả năng sẵn sàng và hiệu năng của mạng và thiết bị mạng. Nếu có xảy ra lỗi thì sẽ có cảnh báo gửi tới người quản trị mạng qua sms, email...

Là công cụ mã nguồn mở miễn phí

Được phát hành theo giấy phép GPIv2, không giới hạn về sức chứa và số lượng thiết bị được giám sát

Hỗ trợ bất kỳ kích thước của mô hình mạng nào. Có thể là mô hình nhỏ hoặc mô hình lớn, thường xuyên cập nhật và phát hành phiên bản mới

Zabbix được viết năm 1998, là dự án của Alexei Vlandishev (Alexei Vladishev dùng để monitor hệ thống database)

## Tính năng của Zabbix

Zabbix cung cấp những tính năng quan trọng và cần thiết cho việc monitor hệ thống và các thiết bị mạng

Zabbix dựa trên các agent và agentless để giám sát hệ thống mạng và các thiết bị mạng. Các thiết bị mạng phải hỗ trợ giao thức SNMP. Zabbix giám sát hiệu suất, hiệu năng của máy chủ vật lý cũng như máy ảo

Trong trường hợp có lỗi xảy ra Zabbix cảnh báo cho người quản trị, tuy nhiên Zabbix không có khả năng phát hiện hay dự đoán lỗi có thể xảy ra

**Mã nguồn mở!**

**Agent-based và Agentless:**
- Agent-based:
    - Đây là 1 phần mềm được gọi là agent được cài đặt trên máy chủ local và các thiết bị cần monitor. Mục tiêu của nó là thu thập thông tin gửi về zabbix-server và có thể cảnh báo tới người quản trị
    - Agent được cài đặt đơn giản nhẹ nhàng, tiêu thụ ít tài nguyên của server
    - Lợi ích của việc sử dụng agent là phân tích sâu hơn, ngoài ra có thể chuẩn đoán đc hiệu suất phần cứng, cung cấp khả năng cảnh báo và report
- Agentless:
    - Agentless là 1 giải pháp không yêu cầu bất kỳ cài đặt agent riêng biệt nào. Phân tích mạng dựa trên giám sát package trực tiếp
    - Dựa trên giao thức SNMP hoặc WMI: 1 trạm quản lý trung tâm, giám sát tất cả các thiết bị mạng khác
    - Việc cài đặt không ảnh hưởng đến hiệu suất của server. Quá trình triển khai dễ dàng hơn, không phải cập nhật thường xuyên từ các agent. Tuy nhiên lại không đi sâu thu thập được các số liệu, không cung cấp khả năng phân tích và báo cáo
    - Trong khi zabbix-agent cung cấp những tính năng tuyệt vời trên 1 số nền tảng, nhưng cũng có trường hợp cơ nhũng nền tảng không thể cài đặt được nó. Đối với trường hợp này, phương thức agentless được cung cấp bởi zabbix server

**Tính năng của Agentless:**
- ```Network Services Check```: Zabbix server có thể kiểm tra 1 service đang lắng nghe trên port nào hoặc chúng phản hồi có đúng không. Phương thức này hiện tại support cho 1 số service như: FTP, IMAP, HTTP, HTTPS, LDAP, NNTP, POP3, SMTP, SSH, TCP và Telnet. Đối với các trường hợp không được xử lý bởi mục trước đó, Zabbix server có thể kiểm tra xem có gì đang lắng nghe trên cổng TCP hay không, thông báo nếu 1 dịch vụ có sẵn hay không. Tóm lại có 3 chức năng: **TCP port availability**, **TCP port response time** và **Service check**
- ```ICMP Ping```: mặc dù đơn giản nhưng quan trọng, Zabbix có thể kiểm tra xem máy chủ có đang phản hồi các gói ping ICMP hay không. Vì vậy, nó có thể kiểm soát sự sẵn sàng của 1 máy chủ, cũng như thời gian phản hồi và mất gói tin. Kiểm tra có thể được tùy chỉnh bằng cách thiết lập kích thước và số lượng gói tin, thời gian chờ và độ trễ giữa mỗi gói. Tiếp tục túm lại là: **Server availability**, **ICMP response time**, **Package loss**
- ```Remote Check```: khi cấu hình agent zabbix không hỗ trợ, nhưng truy cập thông qua SSH hoặc Telnet sẵn sàng, một máy chủ Zabbix có thể chạy bất kỳ lệnh tùy chỉnh nào và sử dụng lệnh trả về của nó như là 1 giá trị được thu thập. Từ giá trị này có thể làm nhiều thứ như tạo ra các đồ thị và cảnh báo. Chức năng này gọi là **Executing commands via SSH or Telnet**

**Auto discovery:**

