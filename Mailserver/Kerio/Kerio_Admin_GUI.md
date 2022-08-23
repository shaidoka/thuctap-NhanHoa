# Tìm hiểu về giao diện quản trị của mailserver Kerio Connect

## 1. Accounts

#### a. Users

- Tại đây, người quản trị có thể thêm, sửa, xóa các tài khoản user cũng như nhiều chức năng nâng cao khác liên quan đến user

![](./images/kerio_manage_user_interface.png)

![](./images/kerio_add_user.png)

#### b. Groups

- Giao diện quản lý Groups, cho phép tạo, sửa, xóa group theo tên miền, gán group cho user

![](./images/kerio_manage_group.png)

#### c. Aliases

- Giao diện quản lý Aliases (bí danh), có thể thêm/sửa/xóa bí danh cho user

![](./images/kerio_add_alias)

![](./images/kerio_manage_alias_interface.png)

#### d. Mailing Lists

- Mailing Lists là nhóm những địa chỉ email, nếu có email nào được gửi đến mailing list, nó sẽ được gửi tới toàn bộ thành viên của mailing list đó

- Giao diện quản lý Mailing Lists cho phép thêm sửa xóa danh sách thư, cho phép gán moderator/user vào danh sách thư

![](./images/kerio_manage_mailing_list_interface.png)

#### e. Resources

- Nơi quản lý các tài nguyên lập lịch như phòng họp, phòng hội nghị, bãi đậu xe và nhiều tiện ích khác

- Giao diện quản lý Resources cho phép thêm sửa xóa Resource

![](./images/kerio_add_resource.png)

## 2. Status

#### a. Dashboard

- Hiển thị thông tin về server, bao gồm:
    - Kerio News: giới thiệu về các chức năng mới trong phiên bản hiện tại
    - System: hiển thị thông tin phiên bản Kerio Connect, hđh và hostname
    - System status: hiển thị trạng thái của hệ thống
    - License Details: thông tin giấy phép bản quyền kerio
    - Kerio Antivirus: hiển thị trạng thái hiện tại của Kerio Antivirus
    - System Health: hiển thị RAM, CPU, Disk của hệ thống dưới dạng biểu đồ (%, time)
    - Disk Storage Info: hiển thị dung lượng disk tổng và dung lượng disk đang được sử dụng

![](./images/kerio_status_dashboard.png)

#### b. Message Queue

- Messages in Queue: hiển thị các thư đang được chờ trên hàng đợi để được gửi ra bên ngoài
- Message Queue Processing: tiến trình xếp hàng thư

#### c. Traffic Chart

- Traffic Chart: cho phép hiển thị các thông tin ```Connection``` hoặc các ```Message``` trong một khoảng thời gian (có thể tùy chỉnh tối đa 30 ngày)

#### d. Statistics

- Hiển thị các số liệu thống kê của hệ thống

#### e. Active Connections

- Hiển thị các ```Connection``` và các ```Session``` đang hoạt động

#### f. Opened Folders

- Hiển thị các thư mục đã mở 

#### g. System Health

- Hiển thị mức độ sử dụng RAM, CPU của hệ thống
- Hiển thị tổng dung lượng disk và dung lượng disk đã sử dụng

## 3. Configuration

#### a. Services

- Hiển thị các dịch vụ, port và trạng thái các dịch vụ của mail server

![](./images/kerio_services.png)

#### b. Domains

- Hiển thị các domain đã được tạo. Tại đây có thể tạo, sửa, xóa domain và thiết lập các tùy chọn cho domain đó

![](./images/kerio_manage_domains.png)

#### c. SMTP server

- Máy chủ SMTP xác định ai có thể gửi thư đi qua Kerio Connect và họ có thể thực hiện những hành động nào
- Để thiết lập gửi tin nhắn từ bên ngoài server Kerio Connect ta làm như sau:
    - Trong giao diện ```Configuration``` chọn ```SMTP server``` -> ```Relay Control```
    - Nhấp vào option ```Allow relay only for```
        - Để chỉ định một nhóm địa chỉ IP mà từ đó người dùng có thể gửi đi, chọn ```Users from IP addres group``` và thiết lập như mong muốn
        - Để cho phép người dùng đã xác thực gửi thư đi, chọn ```User authenticated through SMTP for outgoing mail```
        - Để cho phép người dùng đã xác thực trước đó qua POP3 gửi thư đi từ cùng 1 địa chỉ IP, chọn ```Users previously authenticated through POP3 from the same IP address```
        - Nhấp ```Apply``` để lưu thiết lập

#### d. Instant Messaging

- Dịch vụ trò chuyện tức thời trên Kerio Connect

#### e. Archiving and Backup

- Kerio Connect hỗ trợ ```Full Backup``` và nó cũng hỗ trợ ```Differential Backup``` - lưu các tệp đã được thêm vào hoặc thay đổi kể từ lần sao lưu đầy đủ nhất
- Các thao tác để lên lịch sao lưu:
    - Trong giao diện quản trị, vào ```Configuration``` -> ```Archiving and Backup``` -> ```Backup```
    - Chọn ```Enable message store and configuration recovery backup```
    - Chọn ```Add```
    - Nhập mô tả cho bản sao lưu trong ```Description```
    - Chọn thời gian và loại sao lưu và nhấp vào ```ok```