# Một số mailserver hay gặp

## Zimbra Mailserver

### Giới thiệu chung

Zimbra được biết đến là bộ phần mềm bao gồm máy chủ Email và máy khách website. Zimbra nổi tiếng về tính năng, độ ổn định và bảo mật cao. Zimbra không chỉ là tên của 1 ứng dụng về email mà còn là 1 giải pháp, 1 hệ thống khá hoàn chỉnh để triển khai môi trường chia sẻ công tác phục vụ cho quản lý và công việc

### Tính năng chính

- Thư điện tử: 1 hệ thống Email hoàn chỉnh bao gồm Mail Server (có cài đặt SMTP, POP3/IMAP, antivirus, antispam, openLDAP, backup,..., có đầy đủ các tính năng như auto-reply, auto-forward, mail filter,...) và Mail Client (Zimbra desktop và Zimbra Web Client)
- Lịch công tác (calendar): lịch cá nhân và lịch nhóm, tự động gửi mail mời họp,...
- Sổ địa chỉ (contacts): sổ cá nhân và sổ chung của nhóm
- Danh mục công việc (task): của cá nhân và nhóm
- Tài liệu (Documents): tài liệu dưới dạng wiki của cá nhân hoặc soạn tập thể
- Cặp hồ sơ (briefcase): lưu file dùng riêng hoặc dùng chung
- Chat: chat nội bộ trong mạng LAN hoặc trên internet
- Tất cả các mục trên đều có phần chạy trên máy chủ (nằm trong Zimbra server), lưu trên máy chủ để có thể dùng chung được và truy cập từ bất kỳ đâu trên Internet (nếu cài trên máy chủ có Internet). Các mục đó đều có khả năng share (kể cả các thư mục email: Inbox, Sent) cho người khác dùng chung

### Tương thích người dùng

- Zimbra có 2 phần mềm Client: Zimbra desktop và Zimbra web client là giao diện với người dùng. Zimbra desktop (tương tự như Outlook, KMail,...) cài được trên Windows, Mac, Linux. Ngoài ra có thể dùng các mail client khác như Outlook, Evolution, KMail, Thunderbird,... Hai loại mail client trên ứng với 2 cách làm việc:
    - Làm việc online: dùng Zimbra web client, mọi thông tin sẽ được lưu trên máy chủ Zimbra
    - Làm việc offline: dùng các mail client còn lại. Riêng Outlook, Apple desktop và Evolution có thể đồng bộ email, calendar, contacts và task với máy chủ Zimbra, các mail client khác chỉ có thể gửi và đọc email
- Zimbra cũng hỗ trợ làm việc với các điện thoại di động Iphone, Blackberry,...

### Kiến trúc

- Về kiến trúc bên trong, Zimbra vẫn sử dụng các bộ phần mềm mã nguồn mở như OpenLDAP, Postfix, SpamAssassin, Amavisd, Tomcat,... cùng với một số phần mềm riêng tạo nên 1 hệ thống tích hợp chặt chẽ
- Hiện tại, Zimbra server có các bản cài đặt trên RedHat, Fedora, CentOS, Debian, SUSE, Ubuntu và MacOS. Nếu chỉ cài trên một máy chủ độc lập thì cách cài đặt khá đơn giản và nhanh
- Zimbra có thể cài theo nhiều cấu hình khác nhau từ 1 hệ thống nhỏ vài chục account trên 1 máy chủ duy nhất cho đến hệ thống rất lớn hàng nghìn account trên nhiều máy chủ có các chức năng khác nhau. Có khả năng mở rộng (scalability) bằng cách thêm máy chủ dễ dàng
- Zimbra có 1 kho các Zimlet (extensions) mà các quản trị mạng có thể chọn cài để bổ sung tính năng. Mọi người có thể tự viết các Zimlet để kết nối hệ thống Zimbra với các hệ thống thông tin khác hoặc mở rộng tính năng
- Quản trị hệ thống qua giao diện web khá đầy đủ và chi tiết với nhiều tiện ích. VD có thể tạo hàng trăm account trong vài phút

## Kerio Mailserver

### Giới thiệu chung

Kerio Mailserver đại diện cho 1 thế hệ các mail server mới được thiết kế cho các mạng công ty

Để đối phó với các mối đe dọa bảo mật đang gia tăng, Kerio Mailserver cung cấp hàng loạt các tính năng để bảo vệ email khỏi sự ngăn chặn và lây nhiễm do virus máy tính hoặc gửi email rác 

Kerio Mailserver là 1 email server an toàn và hiện đại cho phép các công ty cộng tác với nhau qua email, các địa chỉ liên lạc, các lịch biểu và công việc chia sẻ

### Đặc điểm

**Bảo mật**: Kerio Mailserver là một mail server đa domain bảo mật và cực nhanh, hoạt động với tất cả các mail client POP3 hay IMAP trên Windows, Linux và MacOS

**Chống virus**: Chương trình chống virus là 1 phần của 2 phiên bản mail server: Kerio Mailserver được tích hợp với McAfee Antivirus và Kerio Mailserver hỗ trợ các phần mềm chống virus khác như Avast, AVG, eTrust,...

**Chống thư rác**: Theo chuẩn, Kerio Mailserver được tích hợp phần mềm SpamEliminator cung cấp các chức năng phát hiện và cô lập các thư rác toàn diện. 1 loạt các công cụ chống thư rác tiên tiến và mạnh mẽ như Caller ID, bảo vệ khỏi sự tấn công các thư mục và giới hạn băng thông giúp các công ty giảm đáng kể những nguy cơ bảo mật và pháp lý được liên kết với các thư rác

**Kerio WebMail & Kerio WebMail Mini**: 2 email client có cơ sở web khác nhau, 1 có hình thức giống Microsoft Outlook và trình kia được tối ưu để xem email trên các thiết bị DPA cung cấp cho cả người dùng sử dụng thoải mái và tốc độ trong khi làm việc với các trình duyệt web hiện đại nhất kể cả Safari và Firefox

**Nhóm phần mềm**: Nhằm thay thế cho Microsoft Exchange, Kerio Mailserver cung cấp cách truy cập đến các lịch biểu, các địa chỉ liên lạc và các công việc đã được chia sẻ từ Microsoft Outlook, Microsoft Encourage, và Kerio Webmail, trong khi đó làm giảm chi phí bản quyền (TCO - Total Cost of Ownership) và mang lại kinh nghiệm sử dụng tốt hơn cho các doanh nghiệp vừa và nhỏ

**Dễ quản trị**: Các quản trị viên có thể download, cài đặt và cấu hình Kerio Mailserver chỉ trong vài phút. Các hướng dẫn trực quan đơn giản giúp hầu hết các công việc quản trị thông dụng nhất. Bảng điều khiển quản trị cho phép truy cập từ xa an toàn và cung cấp các bookmarks cho nhiều server

**Công cụ chuyển dời từ Microsoft Exchange**: Để giúp các công ty chuyển từ Microsoft Exchange sang Kerio Mailserver. Kerio cung cấp công cụ Kerio Exchange Migration Tool. Nó chuyển dời các người sử dụng, cấu trúc thư mục, email, tất cả các attachment, lịch, sổ liên lạc và công việc

**Dịch vụ thư mục**: Quản lý các account người sử dụng trong Kerio Mail server có thể sử dụng cơ sở dữ liệu lưu trú hoặc các dịch vụ thư mục ngoại trú, Kerio Mailserver tích hợp với Active Directory trên Windows và Apple Open Directory trên Mac OS X Server

**Khả năng mở rộng**: Kerio Mail server có thể mở rộng server gởi tin hỗ trợ 20 người sử dụng tại bất kỳ nơi nào trong mạng nội bộ nhỏ, cho đến hàng ngàn người sử dụng hoạt động chỉ với 1 server. 1 server dễ dàng hỗ trợ cùng lúc 500 người sử dụng IMAP với các bộ lọc chống thư rác và chống virus mà không ảnh hưởng đến hiệu quả hoạt động của nó

## Gmail

### Giới thiệu chung

Gmail là dịch vụ email miễn phí của Google. Người dùng có thể đăng ký, tạo tài khoản Gmail tại địa chỉ mail.google.com. Hiện nay, Gmail là địa chỉ được nhiều người sử dụng nhất vì tính tiện dụng của nó và vì càng ngày càng nhiều người biết đến Gmail

### Tính năng chính của Gmail

**Lọc thư rác**: Hầu hết các dịch vụ email đều cung cấp chức năng lọc và loại bỏ thư rác tuy nhiên chức năng này của Gmail hiệu quả hơn hết. Gmail có thể loại bỏ hầu hết những thư quảng cáo, thư dính virus hay thư rác. Mặc dù không hẳn là hoàn hảo nhưng Gmail làm tốt hơn Yahoo rất nhiều

**Kết nối với những ứng dụng khác**: Một tiện ích khác của Gmail chính là nó có thể tự động kết nối hoặc giúp bạn đăng ký nhanh chóng ở các ứng dụng, dịch vụ khác bằng tài khoản của mình như Google Hangouts, Google Analytics, hay những dịch vụ, phần mềm khác được cung cấp bởi bên thứ 3

**Dung lượng lớn**: Gmail trở nên nổi tiếng nhờ vào dung lượng lưu trữ lớn của mình. 1 tài khoản miễn phí có dung lượng 15GB, kể cả khi bộ nhớ đầy thì bạn vẫn có thể lựa chọn lưu trữ chúng, giúp giải phóng dung lượng mà vẫn không phải xóa hoàn toàn email cũ

**Chức năng tìm kiếm hiệu quả**: So với Yahoo mail hay Hotmail thì Gmail có bộ tìm kiếm email nhanh chóng và chính xác hơn cả

**Truy cập offline**: Gmail có thể truy cập vào dù đang offline bằng Extension Google Offline của Chrome. Tuy nhiên, vẫn cần Internet để cập nhật thư mới về

## Outlook

### Giới thiệu chung

Outlook là một ứng dụng mail hỗ trợ người dùng email quản lý thời gian, dung lượng của email. Ứng dụng này giúp người dùng có thể sắp xếp, quản lý vào tìm kiếm thông tin dễ dàng, nhanh chóng

Outlook cũng hỗ trợ người dùng trong việc quản lý liên lạc, tài liệu, công việc,... với các chức năng như phân loại thư, gửi thư theo nhóm,...

Outlook có thể được xem là một phần mềm quản lý cá nhân tối ưu nhất cho người sử dụng. Tuy vậy, vẫn còn nhiều người chưa thành thạo và biết cách sử dụng Outlook hiệu quả để có thể áp dụng nó vào cuộc sống 1 cách dễ dàng

### Tính năng chính của Outlook

**Tốc độ truy cập nhanh, không gian lưu trữ rộng**: Outlook cung cấp cho người dùng tốc độ truy cập không giới hạn, email được sắp xếp theo dung lượng/ thời gian nhận/ thời gian gửi...để dễ dàng tra cứu

**Hỗ trợ gửi mail đính kèm tệp tin dung lượng lớn**: Kết hợp với OneDrive, Skype Drive, Outlook còn hỗ trợ khôi phục email đã xóa ngay cả khi nó không còn trong thùng rác

**Cho phép sử dụng HTML và CSS**: người dùng có thể custom email của mình bằng những lệnh HTML và CSS riêng

**Bảo mật và chống spam tốt**: Outlook có tính bảo mật cao, khả năng chống spam bằng việc chặn theo địa chỉ hoặc tên miền

**Đa dạng kết nối**: Tích hợp với các mạng xã hội phổ biến hiện nay và cả ứng dụng trò chuyện từ xa Skype


