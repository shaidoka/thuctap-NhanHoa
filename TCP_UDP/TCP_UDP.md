# Giao thức TCP và UDP

## Giới thiệu chung 

TCP/IP là một bộ giao thức được tạo ra để giao tiếp qua Internet và hầu hết các mạng cục bộ. Nó được đặt tên theo hai giao thức ban đầu của nó là Transmission Control Protocol (TCP) và Internet Protocol (IP). TCP cung cấp cho các ứng dụng cách để chuyển và nhận gói thông tin đã được đặt hàng và kiểm tra lỗi qua mạng.

Trong khi đó, giao thức User Datagram Protocol (UDP) được các ứng dụng sử dụng để vận chuyển một luồng dữ liệu nhanh hơn bằng cách bỏ qua kiểm tra lỗi.

## Những điều cơ bản về TCP và UDP

|TCP|UDP|
|:-|:-|
|Đảm bảo tính toàn vẹn của dữ liệu|Không đảm bảo tính toàn vẹn|
|Kiểm tra lỗi các luồng dữ liệu|Không cung cấp tính năng kiểm tra lỗi|
|Header 20 byte cho phép 40 byte dữ liệu tùy chọn|Header 8 byte chỉ cho phép dữ liệu bắt buộc|
|Xử lý kiểm soát luồng|Không có tùy chọn để kiểm soát luồng|
|Chậm hơn UDP|Nhanh hơn TCP|
|Tốt nhất cho các ứng dụng yêu cầu độ tin cậy cao|Phù hợp với các ứng dụng yêu cầu tốc độ|

 **Điểm giống nhau giữa TCP và UDP:** TCP và UDP đều là các giao thức được sử dụng để gửi các gói tin qua Internet. Cả 2 đều được xây dựng trên giao thức IP. Tức là, dù sử dụng TCP hay UDP, gói này sẽ được gửi đến một địa chỉ IP.
 
 ## Cách thức hoạt động của TCP
 
 Khi bạn yêu cầu một trang web, máy tính sẽ gửi các gói tin TCP đến địa chỉ của máy chủ web, yêu cầu nó gửi lại trang web. Máy chủ web phản hồi bằng một loạt các gói tin TCP, browser sẽ kết hợp chúng với nhau để tạo thành trang web. Mọi thao tác cần sự giao tiếp với server của bạn trên trang web đó cũng khiến browser gửi gói tin TCP cho server
 
 TCP có độ tin cậy cao, các gói tin được gửi bằng TCP sẽ được theo dõi, do vậy dữ liệu sẽ không bị mất hoặc hỏng trong quá trình vận chuyển. Đó là lý do tại sao file tải xuống không bị hỏng ngay cả khi mạng có vấn đề (tuy nhiên nếu máy tính hoàn toàn ngoại tuyến thì kết nối TCP sẽ bị hủy và giao tiếp thất bại)
 
 Để đạt được điều này thì TCP thực hiện 2 cách. Đầu tiên, nó yêu cầu các gói tin bằng cách đánh số chúng. Thứ hai, nó kiểm tra lỗi bằng cách yêu cầu bên nhận gửi phản hồi đã nhận được được cho bên gửi. Nếu bên gửi không nhận được phản hồi đúng, nó có thể gửi lại gói tin để đảm bảo bên nhận nhận chúng một cách chính xác
 
 TCP thường được ứng dụng cho:
 - Thiết lập kết nối giữa các loại máy tính khác nhau
 - TCP cho phép kết nối Internet giữa các tổ chức
 - Web
 - Truyền file, email
 - SSH
 
 Nhược điểm của TCP:
 - Không thể dùng TCP để broadcast hoặc truyền đa hướng
 - TCP không có ranh giới khối, vì vậy cần phải tạo ranh giới riêng cho mình
 - TCP cung cấp nhiều tính năng không cần thiết gây lãng phí băng thông
 
 ## Cách thức hoạt động của UDP
 
 Giao thức UDP hoạt động tương tự như TCP nhưng nó bỏ qua quá trình kiểm tra lỗi. Khi một ứng dụng sử dụng UDP, các gói tin được gửi cho bên nhận sẽ không phải chờ để bên nhận phản hồi đã nhận được gói tin mà sẽ tiếp tục gửi các gói tin tiếp theo. Nếu bên nhận có bỏ lỡ một vài gói tin thì chúng cũng không được gửi lại.
 
 UDP được sử dụng khi tốc độ nhanh và không cần thiết sửa lỗi. Thường thấy ở những nền tảng phát sóng trực tuyến hay game online. UDP tương thích với các chương trình phát gói để gửi trên toàn mạng và gửi đa hướng. UDP cũng được sử dụng trong Domain Name System, voice over IP.
 
 Nhược điểm của UDP:
 - Người nhận các gói UDP không được quản lý chúng
 - Mất dữ liệu có thể xảy ra
 - Trong giao thức UDP, một gói có thể không được phân phối hoặc phân phối 2 lần. Nó có thể được truyền không theo thứ tự
 - Các router không bao giờ truyền lại nếu xảy ra xung đột
 - UDP không có congestion control và tính năng kiểm soát luồng, vì vậy việc triển khai là của ứng dụng người dùng
 
## Tổng hợp

 ||TCP|UDP|
 |:-|:-|:-|
 |Loại dịch vụ|Hướng kết nối|Hướng dữ liệu|
 |Độ tin cậy|Đảm bảo tính toàn vẹn của dữ liệu|Không đảm bảo|
 |Kiểm tra lỗi|Cung cấp khả năng kiểm tra và sửa lỗi nhờ khả năng điều khiển luồng|UDP chỉ kiểm tra lỗi cơ bản bằng checksums|
 |Phân đoạn|Thực hiện phân đoạn dữ liệu, giúp dữ liệu được gửi đúng thứ tự cho bên nhận|Dữ liệu được gửi có thể không theo thứ tự|
 |Tốc độ|Chậm hơn nhiều khi so với UDP|Nhanh, đơn giản và hiệu quả hơn TCP|
 |Gửi lại|TCP hỗ trợ gửi lại gói tin bị mất|Không gửi lại gói tin|
 |Độ dài Header|20-60 bytes|8 byte|
 |Độ nặng|Nặng|Nhẹ|
 |Kỹ thuật bắt tay|Bắt tay 3 bước sử dụng SYN, ACK, SYN-ACK|Không kết nối - Không bắt tay|
 |Broadcast|Không hỗ trợ|Hỗ trợ|
 |Giao thức|Sử dụng bởi HTTP, HTTPS, FTP, SMTP, Telnet|Sử dụng bởi DNS, DHCP, TFTP, SNMP, RIP|
 |Loại luồng|Liên kết TCP là luồng byte|UDP là luồng bản tin|
 
