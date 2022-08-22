# IIS - Internet Information Services

#### 1. Giới thiệu chung

IIS là một tập hợp các dịch vụ chạy trên nền hệ điều hành Windows nhằm cung cấp và phân tán các thông tin lên mạng bằng việc sử dụng giao thức HTTP. IIS có thể bao gồm nhiều dịch vụ như Webserver, FTP server, database remote access,...

#### 2. Cách thức hoạt động

IIS sử dụng các giao thức phổ biến là HTTP và FTP để tiếp nhận yêu cầu và truyền tải thông tin trên mạng với các định dạng khác nhau

Một trong các dịch vụ phổ biến nhất của IIS là WWW, hay dịch vụ Web. Nó sử dụng giao thức HTTP để tiếp nhận yêu cầu (Requests) của trình duyệt Web (Browser) dưới dạng 1 địa chỉ URL (Uniform Resource Locator) của 1 trang Web và IIS phản hồi lại các yêu cầu bằng cách gửi về cho Web browser nội dung của trang Web tương ứng

#### 3. Một số tính năng

- Một tính năng được sử dụng nhiều nhất của IIS là tạo 1 ứng dụng web bằng ASP.NET. Bên cạnh đó, IIS hoàn toàn có thể chạy được với các trang web viết bằng ngôn ngữ khác như PHP, Perl,...
- IIS hỗ trợ 1 số loại xác thực như Basic access authentication, digest access authentication, windows authentication, certificate authentication,...
- Hỗ trợ SSL/TLS, SNI, thiết lập bảo mật máy chủ FTP,...
- Với thiết kế dạng module, việc mở, tắt và cài đặt tùy biến IIS là vô cùng thuận tiện

#### 4. IIS và các webserver khác?

Được phát triển bởi Microsoft, IIS nhờ đó được tích hợp nhiều tính năng của Windows (như windows authentication). Cũng như hoạt động rất tốt với những ngôn ngữ hay framework thuộc nhà Microsoft như ASP.NET hay framework .NET

Tuy nhiên, IIS cũng có những nhược điểm như chỉ tương thích với Windows. Do đi kèm với Windows nên để sử dụng IIS ta phải trả tiền cho bản Windows mà nó được tích hợp. Như IIS 10.0.17763 đi kèm với Windows Server 2019 hay Windows 10 build 1809

Ngoài ra, cộng đồng sử dụng IIS cũng không lớn, điều này có thể làm việc tìm kiếm những câu hỏi về IIS trên mạng trở nên khó khăn hơn nhiều