# So sánh các loại PHP Handler

Khi cần chạy 1 website PHP, server phải thông dịch PHP và tạo ra trang web khi người dùng truy cập vào. Tùy từng người dùng, thời gian địa điểm mà website có thể tạo ra khác nhau. PHP Handler sẽ điều khiển quá trình những gì load lên từ bộ thư viện PHP

Có nhiều PHP Handler hiện nay được sử dụng như DSO, CGI, SuPHP, FastCGI. Mỗi Handler có những tác động đến hiệu suất của Apache khác nhau bởi nó xác định Apache sẽ dùng PHP như thế nào

#### 1. CGI - Common Gateway Interface

CGI Handler sẽ chạy PHP script như 1 CGI module. Nó vẫn chạy tiến trình PHP dưới danh nghĩa user *nobody*. CGI được xem như là 1 hình thức dự phòng khi DSO không có hiệu lực. Phương pháp này không nhanh cũng như không an toàn, dù cho SuExec có được bật hay không

#### 2. FastCGI

FastCGI là 1 giải pháp thay thế có hiệu suất cao thay cho CGI. Nó giống SuPHP ở chỗ sẽ chạy PHP Script dưới quyền sở hữu PHP Scripts đó. Điểm khác là FastCGI chạy tốn ít tài nguyên CPU hơn và đạt tốc độ gần bằng DSO. FastCGI sử dụng được opcode cacher như eAccelerator để load web nhanh hơn

Điểm yếu của FastCGI là sử dụng Ram nhiều. Nếu muốn có tốc độ nhanh và bảo mật tốn ít CPU, ta có thể sử dụng FastCGI

#### 3. SuPHP

SuPHP cũng chạy PHP như CGI module. Nó khá với CGI là PHP scripts được gọi từ webserver sẽ được chạy dưới quyền của user sở hữu PHP scripts đó. SuPHP thông thường là 1 handler mặc định và được recommend bởi cPanel vì nó giúp bạn thấy được user nào đang chạy PHP scripts

SuPHP có 1 điểm lợi là khi bạn sử dụng công cụ upload file lên website của bạn, các file này sẽ được phân đúng quyền hạn của user đó. Upload và 1 vài tính năng khác của WordPress không hoạt động nếu không sử dụng SuPHP hoặc FastCGI

SuPHP cũng cung cấp 1 lợi thế bảo mật hơn DSO hay CGI. Tất cả những PHP Scripts không thuộc 1 user cụ thể nào đó sẽ không thể nào thực thi được hoặc user này sẽ không thể nào thực thi được các PHP Scripts của user khác. Nói cách khác, nếu 1 tài khoản bị đánh cắp, các scripts cũng không thể nào lây lan sang các tài khoản khác được

SuPHP có 1 nhược điểm là mức độ sử dụng CPU cao. Thêm vào đó, bạn không thể sử dụng Opcode Cache (như xCache) với SuPHP. Khi sử dụng SuPHP nếu CPU load cao bạn có thể chuyển lại dùng DSO hoặc FastCGI

#### 4. DSO (mod_php)

Mặc dù là 1 phiên bản cấu hình cũ nhưng lại sở hữu tốc độ nhanh nhất trong các Handler. DSO chạy PHP như 1 Apache Module. Điều đó có nghĩa là các PHP Scripts chạy dưới quyền Apache user. Đó là user *nobody*

Mặc dù sở hữu tốc độ vượt trội nhưng DSO cũng có những khuyết điểm. Tất cả các file được tạo ra từ PHP scripts sẽ được sở hữu bởi user *nobody*. Chúng không có khả năng đọc được từ Web. Điều này khá phổ biến với người dùng WordPress. Nếu họ dùng tính năng upload file thông qua WordPress Interface hay dùng tính năng auto update thì sẽ bị fail với DSO

Một điều nữa mà DSO làm chưa tốt, việc tạo file với danh nghĩa *nobody* có thể tạo lỗ hổng giúp hacker khai thác nhờ đó chạy được file hệ thống cũng được sở hữu bởi *nobody*. Điều này làm hacker có khả năng chỉnh sửa các file hệ thống khác

#### 5. Bảng so sánh

||DSO|CGI|SuPHP|FastCGI|
|:-|:-|:-|:-|:-|
|Tốn ít CPU|v|||v|
|Tốn ít Ram|v|v|v||
|Chạy Script với quyền sở hữu của owner||v (với SuExec)|v|v|
|Bảo mật tốt|||v|v|