# Spam Filter

Để phát hiện và loại bỏ thư rác, Kerio Connect sử dụng các phương pháp sau:

- ```Spam Rating```: Kerio Connect đặt giới hạn cho việc spam hay không
- ```Kerio Anti-spam```: Bộ lọc nâng cao tin nhắn spam bằng các dịch vụ quét trực tuyến của Bitdefender
- ```Backlists```: Ta có thể tạo danh sách địa chỉ IP và đưa vào Blacklists để chặn tất cả các thư từ các địa chỉ đó
- ```Custom Rules```: Trong Kerio Connect, ta có thể tạo các quy tắc chống thư rác của riêng mình. Các quy tắc lọc tiêu đề email hoặc nội dung email
- ```Caller ID``` và ```SPF```: Có thể lọc ra các thư có địa chỉ gửi giả
- ```Greylisting```: Phương pháp Greylisting chỉ gửi tin nhắn từ những người đã biết
- ```Spam Repellent```: Đặt SMTP greeting trì hoãn để ngăn việc thư được gửi từ máy chủ thư rác

### 1. Spam Rating

Kerio Connect đặt giới hạn cho việc đánh dấu thư là thư rác hay không là thư rác dựa trên ```Spam Rating```. Để thiết lập cho ```Spam filter``` ta làm như sau:
- ```Tag Score```: Nếu tin nhắn đạt đến ```Tag Score```, Kerio sẽ đánh dấu nó là thư rác
- ```Block Score```: Nếu tin nhắn đạt đến ```Block Score```, Kerio sẽ loại bỏ tin nhắn đó

### 2. Kerio Antispam

Kerio antispam sử dụng dịch vụ quét trực tuyến của Bitdefender và cung cấp chức năng lọc thư rác nâng cao đối với các thư gửi đến. Hoạt động của Kerio antispam
- Kerio Connect gửi dữ liệu được mã hóa tới dịch vụ quét trực tuyến Bitdefender
- Bitdefender quét dữ liệu và gửi kết quả là điểm số cho Kerio Connect. Điểm có giá trị:
    - 0: Không phải thư rác
    - 1-9: Mức độ spam
    - Kerio Connect tính toán điểm thư rác bằng 1 thuật toán đặc biệt và thêm điểm vào ```Spam Rating```
    - Nếu Bitdefender nhận ra phần mềm độc hại hoặc tin nhắn lừa đảo, Kerio Connect sẽ tự động chặn tin nhắn bất kể các cài đặt trên Kerio như nào

### 3. Blacklists

Trong Kerio Connect, ta có thể tự động chặn các máy chủ (địa chỉ IP) được cho là đang gửi tin nhắn rác. Để tạo blacklist, trước hết ta phải có địa chỉ IP của máy chủ mà mình muốn chặn
- ```Configuration``` -> ```IP address Groups``` và tạo một group mới với địa chỉ IP của máy chủ thư rác
- Quay lại ```Spam Filter``` -> ```Blacklists```
- Trong phần ```Custom blacklist of spammer IP addresses```, chọn ```Use IP address group```
- Chọn hoặc tạo 1 nhóm địa chỉ IP
- Chọn thiết lập theo mong muốn:
    - ```Block the message```: chặn tin nhắn
    - ```Add spam score to the message```: thêm điểm thư rác vào tin nhắn
- Nhấp vào ```Apply```

### 4. Custom Rules

Trong Kerio, ta có thể tạo các quy tắc chống thư rác của riêng mình, các quy tắc lọc tiêu đề email hoặc nội dung email Kerio Connect sẽ xử lý các quy tắc theo thứ tự đc liệt kê. Nếu bộ lọc thư rác đánh dấu thư không phải là thư rác hoặc từ chối thư đó, Kerio Connect sẽ ngừng xử lý các quy tắc còn lại

### 5. Caller ID và SPF

Caller IP và SPF cho phép lọc ra các thư có địa chỉ người gửi giả 

Việc kiểm tra giúp xác minh xem địa chỉ IP của máy chủ SMTP từ xa có được phép gửi email đến tên miền được chỉ định hay không. Spammer do đó phải sử dụng địa chỉ thật của chúng và các email spam có thể bị nhận ra nhanh chóng nhờ vào nhiều blacklist khác nhau

Thiết lập Caller ID:
- ```Configuration``` -> ```Spam filter``` -> ```Caller ID```
- Nếu 1 tin nhắn bị chặn, Kerio Connect có thể:
    - Ghi nó vào ```Security Log```
    - Từ chối nó
    - Tăng/giảm điểm thư rác
- Caller ID thường chỉ được sử dụng bởi các miền ở chế độ thử nghiệm. Do đó, nên bật tùy chọn ```Apply this policy also to testing Caller ID records```
- Nếu thư được gửi qua máy chủ dự phòng, tạo 1 nhóm địa chỉ IP của những server đó mà sẽ không được kiểm tra bởi Caller ID

### 6. Greylisting

```Greylisting``` là một phương pháp chống thư rác bổ sung cho các phương pháp và cơ chế chống thư rác khác trong Kerio Connect

Cách thức hoạt động:
- Kerio liên hệ với server ```Greylisting``` và cung cấp thông tin về thư. ```Greylisting``` server bao gồm danh sách các địa chỉ IP đáng tin cậy
- Nếu danh sách chứa địa chỉ IP của người gửi thư, thư sẽ vượt qua kiểm tra ```Greylisting``` ngay lập tức
- Nếu danh sách không chứa địa chỉ IP của người gửi, server ```Greylisting``` sẽ trì hoãn việc gửi thư. Những người gửi thư đáng tin cậy sẽ cố gắng gửi lại các thư sau đó. Người gửi thư rác thường không làm vậy
- Sau khi nhận lại được thư đó, Kerio Greylisting Service sẽ thêm địa chỉ IP của người gửi vào whitelist. Nhờ đó, thư của người gửi này sẽ luôn pass greylisting check

### 7. Spam Repellent 

Phần lớn thư spam được tạo bởi các ứng dụng gửi thư hàng loạt chuyên biệt. Mục tiêu của phần mềm này là phân phối càng nhiều thư rác càng tốt trong 1 khoảng thời gian nhỏ 

Tính năng chống thư rác Spam Repellent hoạt động bằng cách tạo độ trễ cho lời chào SMTP, Các mail server hợp pháp thường sẽ đợi ít nhất 2 phút trước khi đóng kết nối, trong khi các công cụ thư rác chỉ đợi vài giây

Giá trị mặc định là 25 giây. Lượng thời gian này sẽ loại bỏ một lượng đáng kể thư rác mà không gây mất email hợp lệ. Tuy nhiên, việc nhận các email thông thường sẽ bị trễ đi 25 giây