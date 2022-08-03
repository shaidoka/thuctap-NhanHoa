# Giao thức ARP

### Giới thiệu chung

ARP (Address Resolution Protocol) được hiểu là một giao thức phân giải địa chỉ động giữa địa chỉ lớp network và địa chỉ lớp datalink. Nói cách khác, ARP là giao thức dùng để tìm ra địa chỉ MAC của thiết bị từ một địa chỉ IP nguồn. Nó được sử dụng khi một thiết bị cần giao tiếp với thiết bị khác trên mạng local network.

Thiết bị gửi sử dụng ARP có thể dịch địa chỉ IP sang địa chỉ MAC. Thiết bị gửi sẽ broadcast 1 ARP Request chứa địa chỉ IP của thiết bị nhận, thiết bị có địa chỉ IP đó sẽ gửi lại phản hồi với thông điệp có chứa địa chỉ MAC của nó. Khi đó thiết bị gửi sẽ có đầy đủ thông tin để gửi packet tới thiết bị nhận.

### Cách thức hoạt động

- **Source Device Checks Cache**: thiết bị nguồn kiểm tra bộ đệm của mình. Nếu đã có địa chỉ IP đích tương thích với MAC đó rồi thì update địa chỉ vào ARP cache
- **Source Device Generates ARP Request Message**: Hệ thống bắt đầu khởi tạo gói tin ARP Request với các trường địa chỉ như trên
- **Source Device Broadcasts ARP Request Message**: Thiết bị nguồn truyền gói tin ARP Request trên toàn mạng
- **Local Devices Process ARP Request Message**: Tất cả các thiết bị trong mạng đều nhận được gói tin ARP Request. Chúng đưa thiết bị vào trường địa chỉ Target Protocol Address, nếu trùng với địa chỉ của mình thì tiếp tục xử lý, nếu không thì hủy gói tin
- **Destination Device Generate ARP Reply Message**: Thiết bị có IP trùng với IP trong trường Target Protocol Addres sẽ khởi tạo gói tin ARP Reply. Đồng thời thiết bị sẽ lấy địa chỉ datalink của mình để tiến hành đưa vào trường Sender Hardware Address
- **Destination Device Updates ARP Cache**: Thiết bị đích cập nhật địa chỉ IP và MAC tương ứng của thiết bị nguồn vào bảng ARP cache của mình để giảm bớt thời gian xử lý cho những lần sau
- **Destination Device Sends ARP Reply Message**: Thiết bị đích sẽ bắt đầu gửi gói tin Reply đã được khởi tạo đến thiết bị nguồn
- **Source Device Processes ARP Reply Message**: Thiết bị nguồn nhận được gói tin Reply và lưu trường Sender Hardware Address trong gói Reply như những địa chỉ phần cứng của thiết bị đích
- **Source Device Updates ARP Cache**: Thiết bị nguồn update vào ARP cache giá trị tương ứng giữa địa chỉ network và địa chỉ datalink của thiết bị đích để những lần sau không cần tới request nữa

### Các loại bản tin ARP

- Bản tin Request: Bản tin gửi từ thiết bị nguồn tới thiết bị đích, sử dụng để khởi tạo quá trình lấy địa chỉ MAC
- Bản tin Reply: Bản tin gửi từ thiết bị đích đến thiết bị nguồn, dùng để phản hồi lại gói tin Request

Có 4 loại địa chỉ nằm trong 1 bản tin ARP:

- Sender Hardware Address: địa chỉ MAC của thiết bị gửi
- Sender Protocol Address: địa chỉ IP của thiết bị gửi
- Target Hardware Address: địa chỉ MAC của thiết bị đích
- Target Protocol Address: địa chỉ IP của thiết bị đích

### Các loại ARP

- **Proxy ARP**: Trong phương pháp Proxy ARP, các thiết bị Layer 3 có thể phản hồi ARP Request. Loại ARP này được cấu hình sao cho router sẽ phản hồi địa chỉ IP đích và ánh xạ địa chỉ MAC đến địa chỉ IP đích và người gửi khi nó đến được đích
- **Gratuitous ARP**: Đây là một loại ARP Request khác của host. Loại Request này giúp mạng có thể xác định các địa chỉ IP bị trùng lặp. Do đó, khi router hay switch gửi ARP Request để lấy địa chỉ IP, nó sẽ không nhận được phản hồi ARP nào. Vì vậy cũng không có node nào có thể sử dụng địa chỉ IP được cấp cho router hay switch đó
- **Reverse ARP**: Reverse ARP là một loại giao thức ARP được hệ thống client trong LAN sử dụng để yêu cầu IPv4 của nó từ bảng ARP router
- **Inverse ARP**: Đây là một loại ARP để tìm IP của các node từ địa chỉ lớp liên kết dữ liệu. 