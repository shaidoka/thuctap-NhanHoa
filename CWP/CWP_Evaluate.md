# So sánh aaPanel - CyberPanel -  CWP

### aaPanel

aaPanel là 1 Control Panel miễn phí dành cho máy chủ Linux với rất nhiều tính năng nổi bật

aaPanel rất nhẹ, nó chỉ chiếm khoảng 200MB RAM sau khi cài đặt và mức độ sử dụng CPU cũng rất thấp. aaPanel nhẹ như vậy do thực tế khi cài đặt thì chúng ta chỉ cài giao diện và bộ nguồn của nó. Còn sau đó muốn sử dụng các ứng dụng nào thì cài đặt thêm vào

Hiện nay aaPanel hỗ trợ rất tốt 2 webserver phổ biến nhất là Nginx và Apache, và hỗ trợ PHP từ những phiên bản thấp như 5.6 đến những phiên bản hiện tại như 8.0. Ngoài ra, nó còn hỗ trợ cả OpenLiteSpeed và reverse-proxy

aaPanel có 1 kho thư viện phần mềm đồ sộ, tức là nếu muốn sử dụng thêm tính năng nào thì ta chỉ cần cài đặt thêm rất nhanh chóng

Tuy nhiên aaPanel cũng có 1 vài nhược điểm như vẫn còn tồn đọng lỗi, ví dụ MySQL/MariaDB có thể sẽ bị sập mà không thể tự khởi động lại được do bị thiếu tài nguyên dẫn đến treo dịch vụ. Nguyên nhân cho lỗi này là thiết lập mặc định của aaPanel cho MySQL/MariaDB hơi cao, buộc ta phải tự thiết lập chỉnh cấu hình xuống. Ngoài ra, aaPanel cũng chưa hỗ trợ tính năng phân quyền người dùng mà chỉ có thể truy cập vào bảng điều khiển bởi 1 tài khoản duy nhất

**=>** Nhìn chung, aaPanel phù hợp với nhu cầu cần control panel nhỏ gọn dành cho các VPS cấu hình thấp nhưng lại tối ưu với người dùng cá nhân

### CyberPanel

Cũng như aaPanel, CyberPanel là 1 control panel miễn phí, hỗ trợ cả OpenLiteSpeed và LiteSpeed Webserver Enterprise

CyberPanel có hỗ trợ phân quyền người dùng, tức là người sử dụng có thể tạo ra nhiều tài khoản truy cập riêng cho từng website (giống như 1 tài khoản host riêng), và có hỗ trợ tài khoản reseller để người dùng tự tạo ra các gói host cho riêng mình

Thêm một tính năng nữa đó là CyberPanel có hỗ trợ cả CloudLinux OS giúp tăng cường bảo mật giữa các tài khoản trên máy chủ, tránh trường hợp bị tấn công leo thang đặc quyền thông qua phương thức Local Attack

Không chỉ vậy, CloudLinux còn giúp mỗi tài khoản có thể sử dụng nhiều phiên bản PHP khác nhau cho các website nhờ vào công nghệ CageFS giúp mỗi tài khoản như một phân vùng ảo hóa riêng với các thiết lập riêng biệt

Nhược điểm của CyberPanel lại chính do nó sử dụng OpenLiteSpeed nên đôi lúc sẽ cần người dùng phải thiết lập thủ công để website có thể hoạt động trơn tru. 1 vài thao tác vẫn còn hỗ trợ chưa tốt, như việc cấu hình lại .htaccess thì phải khởi động lại dịch vụ LiteSpeed. Ngoài ra, vẫn còn gặp lỗi lặt vặt khi cập nhật lên phiên bản mới

**=>** Tóm lại, CyberPanel phù hợp với những người dùng cần khả năng phân quyền đa dạng, cho phép nhiều người cùng truy cập vào làm việc. Hoặc với những trang web muốn tận dụng tối đa khả năng của OpenLiteSpeed

### CWP

CWP là control panel lâu đời nhất trong những CP kể trên, nhưng không phải vì vậy mà nó kém hiệu quả. Là 1 control panel miễn phí , CWP hỗ trợ nhiều tính năng và các phần mềm thứ 3 như LiteSpeed Webserver Enterprise, CloudLinux, Softaculous, Varnish Cache, FFMPEG, ShoutCast,... và rất nhiều phần mềm/tính năng khác có thể cài đặt thêm vào. Ngoài ra, CWP cũng có hệ thống phân quyền người dùng rất mạnh mẽ

CWP có thể giúp chuyển đổi loại webserver rất dễ dàng và nhanh chóng chỉ với 1 cú click, bạn có thể chọn Nginx Proxy-Apache, Nginx + PHP-FPM, Nginx + PHP-FPM + Varnish,...

Ngoài ra, CWP cũng có thể biến VPS không chỉ là 1 webserver mà còn có thể là 1 Email Server với các tính năng hỗ trợ email khá chuyên nghiệp. CWP cũng hoàn toàn có thể được cấu hình để trở thành 1 DNS Server

Nhược điểm mà có lẽ là lớn nhất của CWP đó là rất nhiều tính năng nổi bật của CWP lại không được bao gồm trong phiên bản miễn phí. Không chỉ vậy, CWP lại là Panel nặng nhất trong những Panel kể trên do nó có nhiều tính năng đa dạng (và có thể không sử dụng đến)

**=>** Nói ngắn gọn, CWP là 1 panel dễ sử dụng với rất nhiều tính năng nổi bật cùng với khả năng phân quyền mạnh mẽ, hỗ trợ cả email server và dns server, nhưng điểm yếu lại là bị giới hạn nhiều tính năng trong bản Free. CWP có lẽ sẽ phù hợp nhất với những VPS có cấu hình mạnh mà số lượng người dùng lớn
