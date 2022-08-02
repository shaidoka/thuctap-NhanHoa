## Giới thiệu chung

FTP (hay File Transfer Protocol) là giao thức giúp truyền tải file giữa các máy tính khác nhau, được đặc tả trong RFC 959

Mô hình Client/Server:
- Client: trạm làm việc của user
- Server: máy chủ lưu file

Cổng hoạt động: cổng 21

## Cách thức hoạt động

FTP Client kết nối với FTP Server tại port 21 và kết nối điều khiển
- Server sẽ xác thực Client trên kết nối điều khiển qua user và pass
- Client sẽ làm việc với hệ thống tệp tin trên Server
- Server nhận lệnh, đáp ứng yêu cầu 

Khác với HTTP, FTP duy trì các trái thái "state" trong một phiên 

Client và Server của FTP "nói chuyện" thông qua kết nối điều khiển nhưng việc giao vận dữ liệu được thực hiện trên một kết nối riêng (port 20)

## Một số câu lệnh thường gặp trong FTP và các bản tin phản hồi

Lệnh trong FTP được gửi dưới dạng text qua kết nối điều khiển (port 21)
- **USER**: được đưa ra để xác định người dùng, thứ cần thiết để truy cập vào hệ thống tệp tin của hệ thống
- **PASS**: dùng để đưa ra mật khẩu của người dùng, kết hợp USER và PASS giúp hoàn thiện bước xác thực danh tính
- **CWD**: lệnh này cho phép người dùng làm việc với một tập dữ liệu hay 1 kho dữ liệu khác mà không phải thay đổi tài khoản
- **MKD**: lệnh này giúp tạo directory được chỉ định trong pathname
- **LIST**: trả về một danh sách các tệp tin trong thư mục hiện tại hoặc đường dẫn được chỉ định
- **RETR**: dùng để Server gửi 1 bản copy của tệp tin được chỉ định trong pathname cho Client
- **STOR**: lệnh này giúp Server chấp nhận dữ liệu được truyền qua kết nối dữ liệu (cổng 20) và lưu trữ nó thành tệp ở phía Server

Một số mã phản hồi thường gặp:
- **331** username OK, password required
- **125** connection already open; Transfer starting
- **425** can't open data connection
- **452** error writting file