# Máy chủ quản lý tên miền - NameServer

## Giới thiệu chung

NameServer là hệ thống có chức năng điều phối quá trình hoạt động của tên miền website, chuyển đổi từ tên miền sang địa chỉ IP. NameServer hay còn được gọi là DNS Server hay Domain NameServer, tạm dịch là máy chủ quản lý tên miền giúp người dùng truy cập vào trang web mình muốn đến thông qua tên miền

Nhìn chung, địa chỉ IP là 1 dãy số khó nhớ, nên khi cần truy cập trang web sẽ phải gõ tên miền vào thanh trình duyệt. Tuy nhiên, tên miền không phải là yếu tố dùng để truy cập trang web mà phải có 1 hệ thống trung gian để chuyển đổi từ tên miền sang địa chỉ IP

## Các loại NameServer

Việc tập trung cơ sở dữ liệu trên 1 nameserver duy nhất là không hợp lý, do đó để giải quyết vấn đề này, DNS triển khai cơ sở dữ liệu phân tán trên Internet. DNS sử dụng nhiều nameserver tổ chức phân cấp và phân tán trên toàn cầu. Không có nameserver nào chứa tất cả tên và địa chỉ của tất cả các máy tính trên Internet, những thông tin này được phân tán trên nhiều nameserver. 

Có 3 loại nameserver:
- Local nameserver: Thường gần với client, có thể là cơ quan hoặc tổ chức, nó có thể ở cùng mạng LAN với máy tính client
- Root nameserver: Trên thế giới có 13 root nameserver. Khi các local nameserver không thể trả lời truy vấn DNS của một máy tính thì local nameserver sẽ đóng vai trò client DNS và gửi câu hỏi truy vấn tới 1 trong số các root nameserver. Nếu root nameserver có thông tin truy vấn được hỏi, nó sẽ gửi một thông điệp DNS hồi âm tới local nameserver và sau đó thông tin này được local nameserver gửi trả lời cho máy tính yêu cầu
- Authoriative nameserver: Mỗi máy tính phải đăng ký tới 1 Authoriative nameserver. Tức là Authoriative nameserver luôn lưu trữ bản ghi DNS cho phép xác định địa chỉ IP của máy tính từ tên miền