# Cân bằng tải - Load balancing

### 1. Khái niệm load balancing

- Load balancing là tính năng giúp máy chủ ảo hoạt động đồng bộ và hiệu quả hơn thông qua việc phân phối đồng đều tài nguyên
- Load balancing hay "cân bằng tải" là 1 trong những tính năng rất quan trọng với những nhà phát triển, lập trình mạng
- Khi truy cập vào website mà ko có load balancing, rất có thể trang web đó sẽ không kịp xử lý khi lượng truy cập tăng lên, khiến cho nội dung tải chậm, thậm chí không kết nối được khi máy chủ down. Do vậy, load balancing là rất quan trọng để giải quyết vấn đề kể trên
- Khi máy chủ down hoặc không thể xử lý, 1 load balancer sẽ được bổ sung. Người dùng truy cập vào load balancer. Tiếp tục được chuyển đến 1 máy khác để thực hiện tác vụ. Dù máy chủ chính bị down hoặc nghẽn thì tất cả các yêu cầu của người dùng đều được giải quyết

### 2. Công dụng

- Tăng uptime: với load balancing, khi máy chủ gặp sự cố, lưu lượng truy cập sẽ được tự động chuyển đến máy chủ còn lại. Nhờ đó, trong hầu hết mọi trường hợp, sự cố bất ngờ có thể được phát hiện và xử lý kịp thời, không làm gián đoạn các truy cập của người dùng 
- Datacenter linh hoạt: khả năng linh hoạt trong việc điều phối giữa các máy chủ cũng là 1 ưu điểm khác của load balancing. Tự động điều phối giữa các máy chủ cũ và mới để lý các yêu cầu dịch vụ mà không làm gián đoạn các hoạt động chung của hệ thống
- Bảo mật cho Datacenter: bằng cách sử dụng load balancing, những yêu cầu từ người dùng sẽ được tiếp nhận và xử lý trước khi phân chia đến các máy chủ. Đồng thời, quá trình phản hồi cũng được thông qua load balancing, ngăn cản việc người dùng giao tiếp trực tiếp với máy chủ, ẩn đi thông tin và cấu trúc mạng nội bộ, từ đó chặn đứng những cuộc tấn công mạng hay truy cập trái trái phép

### 3. Các giao thức mà load balancing có thể xử lý là gì?

- Có 4 loại giao thức chính mà quản trị load balancer có thể tạo quy định chuyển tiếp:
    - HTTP: dựa trên cơ chế HTTP chuẩn, HTTP Balancing đưa ra yêu cầu tác vụ. Load Balancer đặt X-Forwarded-For, X-Forwarded-Proto và tiêu đề X-Forwarded-Port cung cấp các thông tin backends về những yêu cầu ban đầu
    - HTTPS: các chứng năng tương tự HTTP Balancing. HTTPS Balancing được bổ sung mã hóa và nó được xử lý bằng 2 cách: passthrough SSL duy trì mã hóa tất cả con đường đến backend hoặc chấm dứt SSL, đặt gánh nặng giải mã vào load balancer và gửi lưu lượng được mã hóa đến backend
    - TCP: trong 1 số trường hợp khi ứng dụng ko sử dụng giao thức HTTP hoặc HTTPS, TCP sẽ là 1 giải pháp để cân bằng lưu lượng. Cụ thể, khi có 1 lượng truy cập vào 1 cụm CSDL, TCP sẽ giúp lan truyền lưu lượng trên tất cả các máy chủ
    - UDP: trong thời gian gần đây, load balancer đã bổ sung thêm hỗ trợ cho cần bằng tải giao thức internet lõi như DNS và syslogd sử dụng UDP
- Các quy tắc chuyển tiếp sẽ xác định loại giao thức và cổng vào load balancer để di chuyển đến các giao thức. Cổng load balancer lúc này được sử dụng để định tuyến lưu lượng trên backend

### 4. Health Checks

- Load balancer sẽ kiểm tra từng máy chủ trước khi phân bổ tài nguyên
- Có thể hiểu 1 cách đơn giản, Health Checks là việc kiểm tra tình trạng của 1 backend server. Bằng cách kết nối đến backend server dùng giao thức và cổng được định nghĩa bởi các quy tắc chuyển tiếp, nó đảm bảo rằng các máy chủ vẫn hoạt động ổn định
- Trong trường hợp máy chủ không hoạt động, Health Checks sẽ loại chúng ra khỏi vùng chứa. Điều này đồng nghĩa với việc các request sẽ không được chuyển tiếp đến máy chủ này nữa cho đến khi chúng vượt qua "bài kiểm tra" Health Checks
- Qua quá trình này, load balancing có thể chuyển tiếp trực tiếp lưu lượng đến các backend server đang thật sự hoạt động nhằm giải quyết mọi tác vụ của người dùng

### 5. Các thuật toán load balancing là gì?

- Load balancer sử dụng thuật toán cho việc xác định tình trạng các máy chủ
- Tùy thuộc công nghệ load balancing mà các thuật toán khác nhau sẽ được sủ dụng để xác định tình trạng của máy chủ có hoạt động hay không. Có các loại thuật toán thường thấy là: Round Robin, Weighted Round Robin, Dynamic Round Robin, Fastest, Least Connections

#### Thuật toán Round Robin

- Round Robin là thuật toán lựa chọn các máy chủ theo trình tự. Theo đó, Load Balancer sẽ bắt đầu đi từ máy chủ số 1 trong danh sách của nó ứng với yêu cầu đầu tiên. Tiếp đó, nó sẽ di chuyển dần xuống trong danh sách theo thứ tự và bắt đầu lại ở đầu trang khi đến máy chủ cuối cùng
- Nhược điểm: khi có 2 yêu cầu liên tục từ phía người dùng sẽ có thể được gửi vào 2 server khác nhau. Điều này làm tốn thời gian tạo thêm kết nối với server thứ 2 trong khi đó server thứ nhất cũng có thể trả lời được thông tin mà người dùng đang cần

#### Thuật toán Weighted Round Robin (WRR)

- Tương tự như kỹ thuật Round Robin nhưng WRR còn có khả năng xử lý theo cấu hình của từng server đích. Mỗi máy chủ được đánh giá bằng 1 số nguyên (giá trị trọng số Weight, mặc định là 1). Một server có khả năng xử lý gấp đôi server khác sẽ được đánh số lớn hơn và nhận được số request gấp đôi từ load balancer
- Nhược điểm: WRR gây mất cân bằng tải động nếu như tải của các request liên tục thay đổi trong 1 khoảng thời gian rộng

#### Thuật toán Dynamic Round Robin (DRR)

- Thuật toán DRR hoạt động gần giống với thuật toán WRR. Điểm khác biệt là trọng số ở đây dựa trên sự kiểm tra server 1 cách liên tục, do đó trọng số liên tục thay đổi
- Việc chọn server sẽ dựa trên rất nhiều khía cạnh trong việc phân tích hiệu năng của server trên thời gian thực. VD: số kết nối hiện đang có trên các server hoặc server trả lời nhanh nhất,...
- Thuật toán này thường không được cài đặt trong các bộ cân bằng tải đơn giản. Nó thường được sử dụng trong các sản phẩm cân bằng tải của F5 Networks

#### Thuật toán Fastest

- Đây là thuật toán dựa trên tính toán thời gian đáp ứng của mỗi server (response time). Thuật toán này sẽ chọn server nào có thời gian đáp ứng nhanh nhất. Thời gian đáp ứng được xác định bởi khoảng thời gian giữa thời điểm gửi một gói tin đến server và thời điểm nhận được gói tin trả lời
- Việc gửi và nhận này sẽ được bộ cân bằng tải đảm nhiệm. Dựa trên thời gian đáp ứng, bộ cân bằng tải sẽ biết chuyển yêu cầu tiếp theo đến server nào
- Thuật toán Fastest thường được dùng khi các server ở các vị trí địa lý khác nhau. Như vậy người dùng ở gần server nào thì thời gian đáp ứng của server đó sẽ nhanh nhất. Cuối cùng server đó sẽ được chọn để phục vụ

#### Thuật toán Least Connection 

- Các request sẽ được chuyển vào server có ít kết nối nhất trong hệ thống. Thuật toán này được coi như thuật toán động, vì nó phải đếm số kết nối đang hoạt động của server
- Least Connection có khả năng hoạt động tốt. Ngay cả khi tải của các kết nối biến thiên trong 1 khoảng lớn. Do đó nếu sử dụng LC sẽ khắc phục được nhược điểm của Round Robin

### 6. Cách Load Balancing xử lý trạng thái

- Trong nhiều trường hợp ứng dụng yêu cầu người truy cập tiếp tục kết nối đến cùng 1 Backend Server. Một thuật toán mã nguồn sẽ tạo ra 1 mối quan hệ dựa trên thông tin là IP của khách hàng. Tức là đối với ứng dụng web sử dụng sticky sessions, load balancer sẽ đặt 1 cookie, tất cả các requests từ sessions sẽ hướng đến 1 máy chủ vật lý

### 7. Load Balancer dự phòng

- Trong nhiều trường hợp, chỉ có 1 load balancer là điểm truy cập duy nhất. Chính vì vậy, chúng ta cần có 1 load balancer thứ 2. Nó sẽ được kết nối với load balancer ban đầu. Mục đích để mỗi load balancer đều có khả năng phát hiện lỗi và phục hồi
- Khi load balancer chính bị lỗi, balancer thứ 2 sẽ nhận trách nhiệm thay thế, do DNS di chuyển người dùng đến. Tuy nhiên, việc thay đổi DNS có thể mất nhiều thời gian trên Internet. Và để chuyển đổi dự phòng được tự động, các quản trị viên sẽ cho phép linh hoạt địa chỉ IP Remapping. Chẳng hạn như trường hợp này là floating IPs
- IP Remapping giúp loại bỏ các vấn đề bộ nhớ đệm vốn có trong những thay đổi DNS. IP Remapping sẽ cung cấp 1 địa chỉ IP tĩnh. Địa chỉ IP này có thể được dễ dàng ánh xạ lại khi cần thiết. Tên miền có thể duy trì liên kết với các địa chỉ IP. Trong khi các địa chỉ IP của chính nó được di chuyển giữa các máy chủ