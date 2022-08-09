# Cài đặt LAMP trên CentOS 7

LAMP là viết tắt của Linux, Apache, MySQL và PHP. Nó là 1 chồng các ứng dụng hoạt động cùng nhau trên 1 máy chủ web để lưu trữ 1 trang web. Mỗi chương trình riêng lẻ phục vụ 1 mục đích khác nhau, được kết hợp lại để tạo thành 1 giải pháp máy chủ web linh hoạt
- Trong LAMP, Linux đóng vai trò là hệ điều hành của máy chủ xử lý tất cả các lệnh trên máy
- Apache là 1 phần mềm máy chủ web quản lý các yêu cầu HTTP để cung cấp nội dung cho trang web
- MySQL là 1 hệ quản trị cơ sở dữ liệu có chức năng duy trì dữ liệu người dùng trên máy chủ
- PHP là 1 ngôn ngữ lập tình kịch bản cho phép giao tiếp phía máy chủ

## Cài đặt Apache webserver

Cài đặt Apache trên CentOS 7 xem tại [đây](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/Linux_basic/Install_Centos7/Cai%20dat%20Apache%20webserver%20tren%20Centos%207.md)

## Cài đặt MariaDB

MariaDB là 1 sản phẩm mã nguồn mở tách ra từ mã mở do cộng đồng phát triển của hệ quản trị cơ sở dữ liệu MySQL nhằm theo hướng không phải trả phí với GNU GPL

MariaDB được định hướng để duy trì khả năng tương thích cao với MySQL, để đảm bảo khả năng hỗ trợ về thư viện đồng thời kết hợp 1 cách tốt nhất với các API và câu lệnh của MySQL

1. Tạo repo cài đặt MariaDB 10

