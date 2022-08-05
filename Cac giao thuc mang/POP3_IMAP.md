# POP3 và IMAP

## POP3

**1. Mục đích của giao thức POP3**

Post Office Protocol - Version 3 (POP3) được tạo ra với mục đích cho phép người nhận có thể truy cập linh động tới hệ thống maildrop của 1 server theo 1 cách thuận tiện. Điều này có nghĩa là, giao thức POP3 cho phép người nhận có thể lấy được mail từ server đang giữ mail đó.

Thông thường, với POP3, mail sẽ được tải về và xóa nó đi ở phía server, khác với IMAP (1 giao thức nâng cao và phức tạp hơn POP3).

POP3 hoạt động ở cổng 110 và được mô tả chi tiết trong rfc 1939.

**2. Cách thức hoạt động của POP3**

Một giao dịch truyền email giữa client và server diễn ra theo các bước sau:

- Ban đầu, server host chạy dịch vụ POP3 ở cổng TCP 110. Khi client host muốn sử dụng dịch vụ, nó sẽ thiết lập 1 kết nối TCP với server host
- Khi kết nối đã được tạo, POP3 server sẽ gửi một lời chào hỏi. Sau đó client và POP3 server sẽ có thể trao đổi và phản hồi (cho tới khi kết nối đóng lại)
- Lúc này, phiên làm việc sẽ vào trạng thái AUTHORIZATION (xác thực). Ở trạng thái này, client phải chứng thực bản thân với bên POP3 server
- Sau khi chứng thực thành công, bên server sẽ có được những tài nguyên liên quan đến hòm thư của client, và phiên làm việc vào trạng thái TRANSACTION (giao dịch)
- Ở trạng thái này, client yêu cầu các hành động liên quan đến tài nguyên của POP3 server (cụ thể là email). Khi client đưa ra lệnh QUIT, phiên làm việc bước vào trạng thái UPDATE (cập nhật)
- Trong trạng thái UPDATE, POP3 server giải phóng bất kỳ tài nguyên nào có được ở phiên TRANSACTION và gửi đi lời chào tạm biệt. Sau đó kết nối TCP được đóng lại

**3. Các lệnh cơ bản của POP3**

- Lệnh ```USER```: Dùng để xác thực người dùng

Cú pháp: ```USER <name>```

Phản hồi: ```+OK name is a valid mailbox``` hoặc ```-ERR never heard of mailbox name```

- Lệnh ```PASS```: Dùng để xác thực người dùng (đi kèm với lệnh USER)

Cú pháp: ```PASS <password>```

Phản hồi: ```+OK maildrop locked and ready``` hoặc ```-ERR invalid password``` hoặc ```-ERR unable to lock maildrop```

- Lệnh ```LIST```: Dùng để lấy danh sách email trong hộp thư hoặc kiểm tra xem có thư với chỉ số tương ứng hay không

Cú pháp: ```LIST [msg]``` với ```[msg]``` là chỉ số của email (có thể có hoặc không)

Phản hồi: ```+OK sscan listing follows``` hoặc ```-ERR no such message```

- Lệnh ```STAT```: Dùng để thống kê hòm thư

Cú pháp: ```STAT```

Phản hồi: ```+OK nn mm```

- Lệnh ```RETR```: Dùng để tải thư cụ thể từ mail server

Cú pháp: ```RETR <msg>``` với ```<msg>``` là chỉ số của email

Phản hồi: ```+OK message follows (nội dung email) .(CRLF)``` hoặc ```-ERR no such message```

- Lệnh ```DELE```: Dùng để đánh dấu xóa email

Cú pháp: ```DELE <msg>``` với ```<msg>``` là chỉ số của email

Phản hồi: ```+OK message deleted``` hoặc ```-ERR no such message```

- Lệnh ```QUIT```: Dùng để xóa email nếu được đánh dấu xóa và kết thúc phiên

Cú pháp ```QUIT```

Phản hồi: ```+OK``` hoặc ```-ERR some deleted messages not removed```

**Ưu và nhược điểm của POP3**

- Ưu điểm:
    - Kết nối internet chỉ dùng để gửi và nhận email
    - Tiết kiệm không gian lưu trữ cho mail server
    - Có lựa chọn để lại bản sao mail trên server
    - Hợp nhất nhiều tài khoản email và nhiều server vào một hộp thư

- Nhược điểm:
    - Không thể truy cập cùng một tài khoản email từ nhiều thiết bị

## IMAP

**1. Mục đích của IMAP**

IMAp (hay Internet Access Protocol) là giao thức dùng để nhận email tương tự như POP3 nhưng phức tạp hơn. Meial được lưu trữ trên server và sẽ không bị mất đi sau khi người dùng tải về. IMAP tuân theo RFC 3501 IMAP hoạt động trên cổng 143

Cho phép truy cập cùng 1 tài khoản trên nhiều thiết bị. Cho phép truy cập email trực tiếp trên server mà không cần tải xuống. Có khả năng lưu nháp tin nhắn trên server

**2. Ưu và nhược điểm**

- Ưu điểm:
    - Mail được lưu trên server nên có truy cập từ nhiều thiết bị khác nhau
    - Có thể xem trước 1 phần của mail để quyết định có tải về hay không
    - Tiết kiệm không gian lưu trữ nội bộ nhưng vẫn có tùy chọn lưu mail cục bộ

- Nhược điểm:
    - Bắt buộc phải có kết nối internet để thao tác với email

## POP3 Và IMAP

|Tiêu chí|POP3|IMAP|
|:-|:-|:-|
|Cơ bản|POP3 cần phải tải thu để có thể đọc|Nội dung mail có thể được kiểm tra một phần trước khi tải về|
|Cách tổ chức|Không thể tổ chức email trong hộp thư trên mail server|Có khả năng tổ chức email trên server|
|Thư mục|Người dùng không thể tạo, xóa hoặc sửa tên hộp hộp thư trên mail server|Người dùng có thể tạo, xóa hoặc sửa tên hộp thư trên mail server|
|Nội dung|Người dùng không thể tìm kiếm nội dung của mail trước khi tải về|Người dùng có thể tìm kiếm nội dung của mail trước khi tải về|
|Các tính năng|POP3 đơn giản và bị giới hạn về tính năng|IMAP mạnh hơn, phức tạp hơn và nhiều tính năng hơn so với POP3|

