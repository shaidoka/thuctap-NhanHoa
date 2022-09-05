# OpenVPN

### Giới thiệu chung

VPN là một mạng riêng sử dụng hệ thống mạng công cộng (thường là Internet) để kết nối các địa điểm hoặc kết nối những người sử dụng từ xa với 1 mạng LAN ở trụ sở trung tâm. Thay cho những kết nối phức tạp như đường dây thuê bao số, VPN tạo ra những liên kết ảo được truyền qua Internet giữa hệ thống mạng riêng của 1 tổ chức với địa điểm hoặc người sử dụng ở xa

Máy của bạn và máy chủ OpenVPN đóng vai trò như router sẽ liên kết với nhau bằng cách sử dụng chứng chỉ xác nhận. Sau khi xác nhận, cả máy chủ và máy khách đều sẽ đồng ý cho phép truy cập vào mạng của Server

Thông thường khi triển khai phần mềm VPN và phần cứng sẽ tốn nhiều thời gian và chi phí. Do đó, OpenVPN là 1 giải pháp mã nguồn mở VPN hoàn toàn miễn phí cho người dùng

### Các thành phần của OpenVPN

Mặc dù là giao thức mã hóa bảo mật nhất, nhưng OpenVPN vẫn dựa vào vào 1 số yếu tố quan trọng
nhất định, và trừ khi VPN nhận được mọi thành phần quan trọng của giao thức, nếu không, tính bảo mật của toàn bộ giao thức mã hóa sẽ bị ảnh hưởng. Các thành phần này như sau:

- **Mật mã:** là thuật toán mà VPN sử dụng để mã hóa dữ liệu. Khả năng mã hóa chỉ mạnh bằng mật mã mà giao thức VPN sử dụng. Các mật mã phổ biến nhất mà các nhà cung cấp VPN sử dụng là AES và Blowfish

- **Các kênh mã hóa:** OpenVPN sử dụng 2 kênh dữ liệu và kênh điều khiển. Các thành phần cho mỗi kênh như sau:
    - Kênh dữ liệu = Mật mã + Xác thực hash
    - Kênh điều khiển = Mật mã + Mã hóa handshake TLS + xác thực hash + việc Perfect Forward Secrecy có được sử dụng hay không (và dùng như thế nào)

- **Mã hóa handshake:** điều này được sử dụng để bảo mật trao đổi key TLS. RSA thường được sử dụng, nhưng DHE hoặc ECDH có thể được dùng thay thế và cũng cung cấp PFS

- **Xác thực hash:** điều này sử dụng 1 hàm hash mật mã xác minh rằng dữ liệu không bị giả mạo. Trong OpenVPN, nó thường được thực hiện bằng HMAC SHA, nhưng nếu mật mã AES-GCM đang được sử dụng thay vì AES-CBC thì GCM có thể cung cấp xác thực hash thay thế

- **Perfect Forward Secrecy:** PFS là 1 hệ thống trong đó một key mã hóa riêng tư duy nhất được tạo cho mỗi phiên. Có nghĩa là mỗi phiên Transport Layer Security (TLS) có 1 bộ key riêng. Chúng chỉ được sử dụng 1 lần và sau đó biến mất

Những cài đặt tối thiểu được đề xuất cho các kết nối OpenVPN là:

- **Kênh dữ liệu:** mật mã AES-128-CBC với HMAC SHA1 có xác thực. Nếu sử dụng mật mã AES-GCM thì không cần xác thực bổ sung

- **Kênh điều khiển:** mật mã AES-128-CBC với mã hóa handshake RSA-2048 hoặc ECDH-385 và xác thực hash HMAC SHA1. Bất kỳ quá trình trao đổi key DHE hoặc ECDH nào cũng có thể cung cấp Perfect Forward Secrecy

### Những OpenVPN Client tốt nhất

- **ExpressVPN:** OpenVPN Client tốt nhất. Nó có 1 mạng lưới lớn các máy chủ tốc độ cao, giúp bạn bảo mật tại nhà hay đang di chuyển cùng các ứng dụng tuyệt vời

- **NordVPN:** một OpenVPN Client siêu bảo mật. Nó cũng có các máy chủ hỗ trợ P2P và chuyển tiếp cổng

- **PrivateVPN:** dịch vụ VPN rẻ nhất với mã hóa OpenVPN trên ứng dụng cho tất cả các thiết bị phổ biến và không có chính sách ghi nhật ký

- **IPVanish:** máy chủ nhanh, giúp bạn phát trực tiếp, tải xuống hoặc thực hiện các tác vụ khác 1 cách tuyệt vời mà không làm bạn bị chậm lại

- **VPNArea:** dịch vụ bảo mật nhất trong danh sách. Chính sách không ghi nhật ký và bảo vệ chống rò rỉ DNS cho phép bạn duyệt web ẩn danh