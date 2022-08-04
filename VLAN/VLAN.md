# VLAN

## Giới thiệu chung

VLAN (hay Virtual Local Area Network) là mạng cục bộ ảo hoặc mạng LAN ảo. VLAN là một mạng tùy chỉnh được tạo từ một hoặc nhiều mạng LAN hiện có. Nó cho phép các nhóm thiết bị từ nhiều mạng được kết hợp thành 1 mạng logic duy nhất. Kết quả là 1 mạng LAN ảo có thể được quản lý giống như 1 mạng cục bộ vật lý

## Giao thức VLAN

Vì lượng truy cập từ nhiều VLAN có thể cùng đi qua 1 mạng vật lý, nên dữ liệu phải được ánh xạ tới 1 mạng cụ thể. Điều này được thực hiện bằng giao thức VLAN. Giao thức này chèn thêm 1 header hoặc "tag" vào mỗi khung Ethernet. Thẻ này xác định VLAN mà thiết bị gửi thuộc về, ngăn không cho dữ liệu được định tuyến đến các hệ thống bên ngoài mạng ảo. Dữ liệu được gửi giữa các switch bằng cách sử dụng 1 liên kết vật lý gọi là trunking kết nối giữa các switch với nhau. Trunking phải được bật để một switch chuyển thông tin VLAN sang 1 switch khác

## Làm việc với VLAN

### 1. Cấp phát

VLAN có thể được cấp phát bằng cách sử dụng một hoặc nhiều cổng và được nhóm thành các lớp logic tùy thuộc vào kết nối hoặc kiểu điều khiển và sự tương tác của chúng với chính chúng. Cùng 1 ID VLAN được sử dụng để quản lý các cổng kết nối với switch cho tất cả các máy chủ sử dụng liên kết dữ liệu do VLAN cung cấp. Trong Ethernet header, các VLAN tag là 1 trường 12 bit. IEEE chuẩn hóa VLAN là 802.1Q hay còn gọi là dot1q.

### 2. Gửi thông tin đến mục tiêu

Khi máy chủ kết nối nhận được một frame không được bảo mật bằng việc sử dụng định dạng dot1q được đính kèm với phần header khung liên kết dữ liệu, VLAN ID tag sẽ được cài đặt trên 1 cổng giao tiếp. Frame dot1q sau đó sẽ được gửi đến mục tiêu. VLAN được thiết lập để giữ cho lưu lượng luôn tách biệt giữa các VLAN khác nhau. Mỗi switch sử dụng tên và chỉ vận chuyển nó. Các liên kết backbone giữa các switch vận hành nhiều VLAN, và được phân tách ra bởi tag và name. Khi mà frame đến switch đích, VLAN tag sẽ được bỏ đi trước khi frame được gửi tới máy tính đích

### 3. Nguyên tắc cấu hình VLAN

Liên kết trunk có thể tạo ra nhiều VLAN trên 1 cổng duy nhất. Để gửi và chấp nhận frame tag, bạn cần phải có 1 giao diện hệ thống lân cận trên máy chủ, hệ thống, hoặc switch khác mà chấp nhận tag dot1q. Bất kỳ frame Ethernet nào không được lên lịch đều được cấp phát cho 1 VLAN mặc định trong quá trình thiết lập switch

### 4. Nhận bản tin không xác định

Khi 1 Ethernet frame không có tag từ 1 máy chủ kết nối đến 1 VLAN switch, VLAN tag mà đã được cấp cho giao diện đầu vào đó sẽ được áp dụng. Frame đó sẽ được gắn với địa chỉ MAC và gửi đến server port. Broadcast và multicast sẽ được gửi đến tất cả các cổng VLAN. Nếu 1 server không xác định phân giải được 1 hệ thống unicast ẩn danh, switch sẽ tìm ra được địa điểm của server đó và không gửi frame đến server đó nữa

## Các loại VLAN

- Protocol-based VLAN: Mỗi địa chỉ logic hay địa chỉ IP được đánh dấu với một VLAN xác định. Cách cấu hình này không còn thông dụng do sử dụng giao thức DHCP
- VLAN tĩnh: 1 LAN tĩnh là 1 tập hợp của những port được xác định là cùng chung 1 miền quảng bá của 1 switch. Nói cách khác, tất cả các cổng có lưu lượng truy cập trong 1 subnet nhất định đều thuộc về cùng 1 VLAN
- VLAN động: 1 switch gán 1 VLAN vào 1 cổng sử dụng dữ liệu từ hệ thống người dùng hoặc các thiết bị như địa chỉ IP và địa chỉ MAC tự động trong 1 VLAN động. Khi máy tính được kết nối với switch, switch sẽ yêu cầu thiết lập thành viên VLAN cho cơ sở dữ liệu. VLAN động cung cấp khả năng kích hoạt ngay lập tức các thiết bị đầu cuối. Các VLAN động có thể cấu hình động thành viên VLAN nếu hệ thống được chuyển từ cổng này sang cổng khác trên switch khác

## Lợi ích của VLAN

- Quản trị và phân chia lưu lượng mạng theo các phân vùng
- Nhóm các nút mạng ở các địa điểm khác nhau vào trong một mạng LAN logic
- Điều chỉnh số nút mạng, hạn chế phải thiết kế lắp đặt thêm cổng
- Cấu hình lại cấu trúc kết nối của mạng mà không cần di chuyển nút mạng
- Giảm kích thước broadcast domain
- Tăng tính bảo mật cho các thiết bị bằng cách đặt các thiết bị đó trên VLAN riêng
