# Tìm hiểu về DirectAdmin

## Giới thiệu chung

DirectAdmin là công cụ quản trị server được phát triển để dễ dàng thực hiện các công việc hàng ngày của webmaster, đặc biệt là những người có ít hoặc không có kinh nghiệm về lĩnh vực này. DirectAdmin được sử dụng thông qua trình duyệt web, có giao diện trực quan và rất dễ sử dụng

Phần mềm DirectAdmin cung cấp cho người dùng nhiều tính năng như quản lý domain, subdomain, DNS, FTP và cơ sở dữ liệu MySQL. Không những vậy, khi sử dụng DirectAdmin cũng có thể tạo thêm được các email theo tên miền, SSH key, bảo mật SSL,... Với DirectAdmin, người dùng sẽ dễ dàng upload và quản lý các file với file manager 1 cách nhanh chóng và dễ dàng

Tương tự như cPanel, DirectAdmin có thể chạy rất tốt trong Linux và các bản phân phối chính của nó - CloudLinux, CentOS, Ubuntu, Debian, Red Hat,... và không hỗ trợ Windows

## Ưu, nhược điểm

### 1. Ưu điểm

DirectAdmin có rất nhiều tính năng hữu ích, mặc dù không phải là duy nhất, nhưng DirectAdmin vẫn cố gắng cải thiển mọi khía cạnh của nó qua mỗi phiên bản mới
- **Giao diện thân thiện với người sử dụng:** không có quá nhiều thành phần và tùy chọn, tất cả tính năng của DA được xếp chồng lên nhau dưới 3 nhánh chính (quản lý tài khoản, quản lý email, tính năng bổ sung)
- **Giá thành hợp lí:** giá cả là điều vẫn giữ cho DA cạnh tranh trên thị trường, nếu so với 2 đối thủ cùng lĩnh vực là cPanel và Plesk thì chi phí cho DA vô cùng dễ chịu. DA cung cấp 1 tài khoản dùng thử miễn phí, cũng như nhiều tùy chọn trả phí khác nhau bắt đầu từ 2$/tháng
- **Hỗ trợ:** ngoài sự hỗ trợ của nhà cung cấp dịch vụ lưu trữ, bạn cũng có thể nhận được sự hỗ trợ trực tiếp từ các kỹ thuật viên của DA. Người dùng các gói trả phí Standard hay Lite trở lên có thể sử dụng hệ thống ticket. Qua đó, nếu gặp vấn đề với DA hay các hoạt động của nó, bạn có thể nhận sự trợ giúp trực tiếp
- **Phục hồi sự cố tự động:** 1 điều tuyệt vời khác của DA là tính ổn định của các dịch vụ. Nếu có sự cố bất ngờ xảy ra, trước tiên DA sẽ thử khởi động lại dịch vụ để xem liệu điều này có khắc phục được sự cố hay không. Nếu không hiệu quả, hệ thống sẽ gửi thông báo lên quản trị viên web, giúp giải quyết vấn đề trong thời gian thích hợp
- **Tốc độ:** DA được thiết kế tương đối nhẹ và nhanh. Việc tải các tài nguyên từ DA cũng vô cùng thấp
- **Giao diện quản trị:** khác với cPanel vô cùng phức tạp với người dùng mới, DA sở hữu 1 giao diện đơn giản, dễ dàng sử dụng và quản lý
- **Hỗ trợ nhiều phân cấp user:** hệ thống phân cấp người dùng (admin level, reseller level, user level) hỗ trợ tốt cho việc quản trị người dùng và đối tượng người dùng. Vì thế, DA phù hợp với các đơn vị cung cấp hosting cho nhiều người dùng trực thuộc thông qua tài khoản reseller
- **Thiết lập thủ công:** mặc dù hầu hết tính năng của DA có thể thiết lập qua GUI, song người dùng vẫn có thể thay đổi chúng nhờ command line interface. Thực tế, nhiều người sử dụng thích sử dụng cli hơn so với GUI

### 2. Nhược điểm

- **Tiện ích bổ sung:** về mặt này thì DA còn rất hạn chế. Tuy nhiên vẫn có thể thêm các chức năng nhưng sẽ tốn thêm chi phí cho việc này
- **Cộng đồng nhỏ:** người dùng khó có thể tìm câu trả lời cho những câu hỏi về DA trên Internet, đặc biệt là những vấn đề chuyên sâu
- **Giao diện thân thiện nhưng khó tìm:** DA được chia thành nhiều phân cấp, và điều đó khiến cho những người dùng mới có thể sẽ gặp khó khăn khi cần xác định vị trí của tính năng mình cần tìm

## Các tính năng chính của DA

### 1. Chức năng của Aministrator trong DA

- **Create/ Modify Admins and Reseller:** Admin có thể tạo Reseller hoặc Admin bổ sung 1 cách nhanh chóng và dễ dàng với tính năng này
- **Reseller Package:** Admin có thể tạo các gói tài khoản với các thông số được xác định trước. Đến khi tạo tài khoản, Admin chỉ cần chọn 1 gói thay vì thiết lập thủ công từng tính năng cho tài khoản
- **Show All Users:** Cho phép Admin xem nhanh từng tài khoản trên hệ thống và sắp xếp danh sách này theo nhiều cách khác nhau
- **DNS Administrator:** cho phép Admin tạo, sử đổi hoặc xóa bất kỳ bản ghi DNS nào trên máy chủ
- **IP Manager:** Đây là nơi Admin đặt địa chỉ IP có sẵn cho máy chủ. Admin cũng có thể phân bổ địa chỉ IP cho Reseller từ menu này
- **Mail Queue Administration:** Công cụ để xem danh sách mail và message. Bao gồm các công cụ để thực hiện hành động đối với các message đó
- **System/Services Info:** Admin có thể xem, dừng, bắt đầu và khởi động lại các dịch vụ từ menu này
- **Complete Usage Statics:** Tính năng này cung cấp cho Admin 1 cái nhìn tổng quan đầy đủ về việc sử dụng hệ thống. Đầu vào và đầu ra chính xác từ Ethernet của máy chủ cũng được giamsast
- **DNS Clustering:** Giao tiếp với các máy DA khác để tự động chuyển dữ liệu DNS giữa chúng. Nó có khả năng kiểm tra máy chủ khác để tìm tên miền và không cho phép các tên miền trùng lặp trên Direct Admin của bạn
- **SPAM fighting tools in DirectAdmin:** Nhiều công cụ chống SPAM được cung cấp bởi DA
- **Licensing/ Updates:** Admin có thể xem trạng thái giấy phép của mình và tải xuống các bản cập nhật phần mềm và bảo mật DA mới nhất từ menu này

### 2. Chức năng của Reseller trong DA

- **Create/ List/ Modify Accounts:** tạo, liệt kê, sửa đổi và xóa tài khoản
- **User Packages:** tạo các Packages được xác định trước. Khi tạo tài khoản, Reseller chỉ cần chọn 1 Package thay vì thiết lập thủ công từng tính năng cho tài khoản
- **Reseller Statics:** Reseller được cung cấp thông tin tổng quan đầy đủ về tổng mức sử dụng của họ. Reseller cũng có thể sắp xếp dữ liệu theo User để nhanh chóng đánh giá tình hình tổng thể
- **Message All Users:** Reseller có thể nhanh chóng gửi tin nhắn đến tất cả khách hàng của họ bằng cách sử dụng hệ thống hỗ trợ ticket được tích hợp sẵn của DA
- **Import/ Manage Skins:** với tùy chọn menu này, Reseller có thể nhanh chóng import và áp dụng giao diện mới chỉ bằng 1 nút bấm
- **IP Assignment:** Reseller có thể phân bổ địa chỉ IP cho khách hàng của họ bằng cách sử dụng hệ thống hỗ trợ ticket được tích hợp sẵn của DA
- **Import/ Manage Skins:** import và áp dụng giao diện mới
- **IP Assignment:** phân bổ địa chỉ IP cho khách hàng của họ bằng cách sử dụng tùy chọn menu này
- **System/ Services Information:** truy cập vào trạng thái máy chủ và thông tin hệ thống
- **Name Servers:** tạo nameserver được cá nhân hóa cho khách hàng

### 3. Chức năng của User trong DA

- **E-mail Administration:** User có thể tạo tài khoản POP/ IMAP, địa chỉ email, forwarder, danh sách gửi thư, thư trả lời tự động và webmail, bộ lọc cho phép người dùng chặn mail theo tên miền, từ khóa và kích thước
- **FTP Management:** User có thể tjao tài khoản FTP và thiết lập quyền thư mục cho từng tài khoản. FTP ẩn danh cũng được hỗ trợ
- **DNS Menu:** User có thể thêm và xóa các bản ghi, thay đổi cài đặt MX và bất kỳ thứ gì khác với toàn quyền kiểm soát DNS
- **Statics Menu:** User có sẵn mọi thống kê về tài khoản của họ. Các tùy chọn nâng cao hơn và Webalizer cũng được bao gồm
- **Subdomains Menu:** User có thể liệt kê, tạo, xóa và lấy số liệu thống kê về các subdomain
- **File Manager:** 1 sự thay thế nhanh chóng và thân thiện với người dùng cho FTP. Bao gồm mọi tính năng cần thiết để xây dựng và duy trì 1 trang web
- **MySQL Databases:** User có thể dễ dàng tạo, sửa đổi và xóa cơ sở dữ liệu MySQL từ menu này
- **Site Backup:** hỗ trợ sao lưu và khôi phục
- **Error pages:** tạo các thông báo và kết quả đầu ra tùy chỉnh cho các mã lỗi 401, 403, 404 và 500
- **Directory Password Protection:** đặt mật khẩu bảo vệ bất kỳ thư mục nào bằng tên username và password
- **PHP Selector:** cho phép khách hàng chọn phiên bản PHP nào được liên kết với phần mở rộng .php
- **Advanced Tools:** nhiều tính năng nâng cao như cài đặt chứng chỉ SSL, xem thông tin máy chủ và các module đã cài đặt, đặt cron job, mime types và trình xử lý apache, đồng thời cho phép chuyển hướng trang web và trỏ tên miền

### 4. Chức năng chung trong DA

- **Integrated Ticket Support System:** trợ giúp việc hỗ trợ khách hàng với hệ thống ticket
- **Two-Factor Authentication:** cho phép bất kỳ tài khoản DA nào được yêu cầu xác thực 2 yếu tố bằng mã từ ứng dụng trên smartphone
- **Plugin System:** cho phép mở rộng chức năng trên DA
- **Live Updates:** xem trạng thái giấy phép hiện tại, tự động thực hiện tải và cài đặt các bản cập nhật hệ thống
- **Completely Customizable:** tùy biến giao diện theo cách của bạn
- **Automatic Recovery From Crashes:** DA TaskQueue đảm bảo rằng tất cả các dịch vụ luôn hoạt động. Nếu sự cố xảy ra, DA sẽ cố gắng khắc phục bằng cách khởi động lại dịch vụ. Nếu không thành công, DA sẽ thông báo cho quản trị viên ngay lập tức
- **We Support Your Customers Through Site-Helper:** Site-Helper được thiết kế để giúp bạn và khách hàng sử dụng DirectAdmin