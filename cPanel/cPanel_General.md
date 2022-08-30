# Giới thiệu chung về cPanel

cPanel là Web Hosting Control Panel trên nền tảng Linux phổ biến nhất hiện nay

cPanel có giao diện đơn giản, linh hoạt, giúp người dùng quản lý tất cả các dịch vụ của web hosting 1 cách dễ dàng

cPanel phân cấp người dùng thành 3 lớp
- Hosting Company
- Reseller
- End User

Hosting Company và Reseller đều sử dụng giao diện Web Host Manager (WHM). Trong đó, Hosting Company có quyền quản trị cao nhất và có thể hạn chế quyền truy cập vào 1 số tính năng nhất định trong Reseller

End User có quyền truy cập trực tiếp vào cPanel Interface để có thể thực hiện các tác vụ cho trang web của họ

Ngoài ra, cPanel cũng cho phép các nhà cung cấp bên thứ 3 tích hợp dịch vụ của họ để khách hàng có thể sử dụng dịch vụ ngay trên giao diện cPanel

cPanel có thể được cài đặt trên các hệ điều hành như CentOS, RedHat Enterprise Linux (RHEL), CloudLinux hay FreeBSD

End User sử dụng hosting cPanel bằng cách truy cập qua cổng 2083

## Các tính năng chính của cPanel

### Quản lý tệp tin

- **File Manager:** truy cập và quản lý file nhanh chóng (thêm, sửa, xóa) mà không cần FTP
- **Disk Usage:** các giao diện đồ họa để thể hiện tình trạng sử dụng ổ cứng để hiểu và quản lý ổ cứng tốt hơn
- **FTP Connection:** cung cấp tổng quan về các phiên kết nối FTP
- **Backup** và **Backup Wizard:** sao lưu các tệp tin trên web hosting dễ dàng
- **Image:** cho phép người dùng thay đổi kích thước, chuyển đổi và xem hình ảnh
- **Web Disk:** cho phép quản trị viên web xem và quản lý không gian ổ cứng (chỉnh sửa, di chuyển, upload hay download file)
- **Anonymous FTP:** dùng để tải xuống file từ các nguồn công khai
- **Directory Privacy:** thư mục được bảo vệ bằng mật khẩu để bảo mật tốt hơn
- **FTP Account:** quản lý tài khoản FTP

### Quản lý cơ sở dữ liệu

- **phpMyAdmin:** giao diện của bên thứ 3 dùng để quản trị cơ sở dữ liệu MySQL
- **Remote SQL:** cho phép truy cập cơ sở dữ liệu từ xa
- **MySQL:** cơ sở dữ liệu để các ứng dụng web chạy
- **PostgreSQL Database:** cơ sở dữ liệu thay thế cho MySQL
- **MySQL Database Wizard:** trình tạo và quản lý cơ sở dữ liệu MySQL
- **PostgreSQL Database Wizard:** trình tạo và quản lý cơ sở dữ liệu PostgreSQL

### Quản lý tên miền

- **Site Publisher:** tạo trang web cơ bản hoặc trang giữ để chuẩn bị cho 1 trang web mới
- **Alias:** chuyển hướng tên miền đến các trang web khác nhau
- **Advanced & Simple Zone Editor:** quản lý các bản ghi DNS
- **Addon Domain:** giảm chi phí bằng cách thêm tên miền và tạo trang web với địa chỉ email mới cho mỗi tên miền mà không cần phải mua hosting mới cho chúng
- **Redirect:** thiết lập chuyển hướng từ một trang cụ thể sang 1 trang khác
- **Subdomain:** tạo các phần phụ của trang web cho mục đích cụ thể như blog của công ty hoặc cơ sở tri thức

### Email

- **Email Account:** thiết lập và quản lý tất cả các khía cạnh của tài khoản email 1 cách nhanh chóng và dễ dàng
- **Autoresponder:** trả lời tự động tới các email nhận được
- **Track Delivery:** theo dõi các email đã gửi
- **Authentication:** gửi email đã được xác thực
- **Archive:** lưu trữ email gửi và nhận trong một khoảng thời gian xác định
- **Calendar and Contact:** cập nhật thông tin về lịch và danh bạ
- **Forwarder:** thiết lập chuyển tiếp email cho các địa chỉ email cụ thể
- **Default Address:** bất kỳ email nào nhận được địa chỉ chính xác đều được gửi đến địa chỉ mặc định
- **Global Filter:** thiết lập bộ lọc email
- **Encryption:** tạo khóa công khai (public key) để liên lạc qua email an toàn hơn
- **Configure Greylisting:** biện pháp ngăn chặn thư rác cơ bản
- **MX Entry:** định tuyến lại email đến 1 máy chủ khác
- **Mailing List:** tạo 1 email gửi cho nhiều người
- **Email Filter:** chuyển hướng email, ngăn chặn thư rác hoặc chuyển email đến các ứng dụng
- **Apache SpamAssassin:** ứng dụng chống thư rác
- **Box Trapper:** ngăn chặn các email không xác định vào hộp thư đến

### Thống kê số liệu và phân tích

- **Visitor:** bản ghi đầy đủ về lượng khách truy cập trong file log Apache
- **Raw Access:** phiên bản nén của nhật ký khách truy cập vào máy chủ
- **Webalizer:** công cụ phân tích khách truy cập trang web
- **Error:** tập hợp các lỗi gần đây trên trang web
- **AWStat:** công cụ đo lường để hiển thị thông tin khách truy cập FTP vào trang web
- **Bandwidth:** hiển thị mức sử dụng băng thông
- **Analog Stat:** chế độ xem đơn giản các lượt truy cập trang web
- **Metric Editor:** chọn số liệu để chạy trên các miền

### Tính năng bảo mật

- **SSH Access - Secure:** xác thực tới máy chủ thông qua dòng lệnh
- **Hotlink Protection:** ngăn chặn hành vi chiếm băng thông khi nội dung được nhúng trên một trang web khác
- **ModSecurity Domain Manager:** kích hoạt hoặc vô hiệu hóa ModSecurity
- **IP Blocker:** quản lý chặn 1 số IP nhất định truy cập trang web
- **Leech Protection:** hạn chế số lần đăng nhập
- **Two-Factor Authentication:** bảo mật 2 lớp
- **SSL/TLS:** bảo mật nâng cao khi quản lý SSL/TLS
- **Security Policy:** chính xách bảo mật cho các IP không xác định
- **SSL/TLS Wizard:** tự động hóa quy trình cung cấp SSL

### Các ứng dụng phần mềm

- **PHP:** kiểm tra cấu hình PHP của server
- **RubyGem:** quản lý Ruby
- **Optimize Website:** tối ưu thời gian phản hồi của webserver Apache
- **PHP Pear Package:** gói Pear để có thể chạy trên PHP
- **Ruby On Rail:** triển khai các ứng dụng Ruby On Rail
- **MultiPHP Manager:** lựa chọn các phiên bản PHP khác nhau cho từng website
- **PERL Module:** tạo module PERL để tạo các tác vụ với PERL
- **Site Software:** thêm phần mềm bổ sung như bảng thương mại điện tử và bảng tin
- **MultiPHP INI Editor:** quản lý cấu hình PHP của nhiều phiên bản khác nhau

### Các cài đặt nâng cao

- **Index:** tùy chỉnh trang mục Apache mặc định
- **MIME Type:** đặt hướng dẫn xử lý các phần mở rộng tệp khác nhau như .html, .htm
- **Cron Job:** tự động hóa các nhiệm vụ lặp đi lặp lại vào thời gian đã lên lịch
- **Error Page:** định cấu hình cách các trang lỗi xuất hiện khi khách truy cập
- **Virus Scanner:** quét các mối đe dọa, phần mềm độc hại
- **Track DNS:** kiểm tra cài đặt DNS bằng cách truy tìm tuyến đường từ PC đến máy chủ
- **Apache Handler:** các lựa chọn xử lý của Apache
- **API Shell:** chạy các lệnh gọi API cPanel

### Các tùy chọn người dùng

- **User Preference:** đặt tùy chọn người dùng
- **User Manager:** đặt và chỉnh sửa quyền và quyền của người dùng