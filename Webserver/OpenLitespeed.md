# OpenLiteSpeed 

#### 1. Giới thiệu chung

OpenLiteSpeed là phiên bản mã nguồn mở và miễn phí của phiên bản LiteSpeed Web Server Enterprise. OpenLiteSpeed chứa gần hết các tính năng cần thiết có trong bản Enterprise, bao gồm cả LSCache (1 plugin cần thiết cho WordPress)

#### 2. Tính năng chính

- Tiết kiệm băng thông
    - Sendfile() support
    - Gzip compression
    - Brotli compression for static files
- Tốc độ cao
    - All version of SPDY/2, 3, 3.1 and HTTP/2 support
    - Piplined requests
    - TCP_FASTOPEN support
    - HTTP/2 Server Push
- OpenLiteSpeed giúp xử lý nội dung tĩnh nhanh gấp 5 lần Apache, PHP nhanh gấp 3 lần và HTTPS nhanh gấp 4 lần
- Hỗ trợ SSL, Security controls, bảo vệ chống tràn bộ đệm
- Hỗ trợ các ứng dụng bên ngoài
    - PHP, Ruby, Python, Perl, Java,...
    - LSAPI, SAPI
    - Daemon CGI
    - Hỗ trợ bộ đệm cho các yêu cầu và phản hồi đối với các ứng dụng bên ngoài
    - Tương thích trình tăng tốc PHP của bên thứ 3
    - Khả năng mở rộng cao
- OLS hoạt động trên hđh Unix-based và MacOS 10.3 hoặc cao hơn
- Về mặt tốc độ, OLS vượt trội hoàn toàn khi đặt lên bàn cân với Apache và Nginx
- Và rất nhiều những tính năng nâng cao khác