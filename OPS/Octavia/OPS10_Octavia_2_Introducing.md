# Introducing Octavia

Octavia là 1 giải pháp open source, operator-scale load balancing thiết kế để hoạt động với OpenStack.

Octavia ra đời dựa trên Neutron LBaaS, ý tưởng của nó lấy cảm hứng nhiều từ việc chuyển đổi Neutron LBaaS project, như là Neutron LBaaS chuyển đổi từ version 1 sang version 2.

Octavia xây dựng delivery service và load balancing service của nó bằng cách quản lý 1 cụm VMs, containers, hoặc bare metal servers (gọi là ```amphora```) và có thể tự scaling theo nhu cầu. Chỉnh bởi khả năng scaling theo chiều ngang này mà Octavia trở nên khác biệt so với các giải pháp load balancing khác trong môi trường Cloud.

## Where Octavia fits into the OpenStack ecosystem

Load balancing rất thiết yếu để mang lại khả năng scaling và availability một cách đơn giản và tự động. Cùng với đó, tính năng scaling và availability cũng là những thứ tối quan trọng trong cloud. Cả 2 điều trên cho thấy Load Balancing là tính năng không thể thiếu với bất kỳ cloud nào.

Theo đó, chúng ta cân nhắc Octavia trở thành "must have" project như Nova, Neutron, Glance hoặc bất kỳ "core" project nào khác của OpenStack cloud.

Octavia sử dụng tính năng của những project sau:

- **Nova**: để quản lý amphora lifcycle và tự động scaling tài nguyên tính toán
- **Neutron**: sử dụng cho kết nối mạng giữa amphora, môi trường tenant, và external networks
- **Barbican**: để quản lý TLS cerificates và credentials, khi TLS session termination được cấu hình ở amphora
- **Keystone**: sử dụng để xác thực với Octavia API, và cho Octavia xác thực được với các project khác
- **Glance**: để lưu trữ amphora virtual machine image
- **Oslo**: for communication between Octavia controller components, making Octavia work within the standard OpenStack framework and review system, and project code structure.
- **Taskflow**: là thành phần kỹ thuật của Oslo; tuy nhiên, Octavia sử dụng rộng rãi job flow system này khi điều phối cấu hình và quản lý các backend service 

Octavia được thiết kế để tương tác với các thành phần liệt kê bên trên. Trong mỗi trường hợp, chúng tôi đã làm việc để định nghĩa những tương tác này thông qua 1 driver interface. Bằng cách đó, các thành phần bên ngoài hoàn toàn có thể bị thay thế (nhưng tương đồng về tính năng) mà không cần phải tái cấu trúc các thành phần của Octavia. Ví dụ, nếu bạn sử dụng 1 giải pháp SDN khác với Neutron, bạn hoàn toàn có thể viết 1 Octavia networking driver cho SDN của bạn, thứ mà sẽ thay thế Neutron networking driver của Octavia.

Trong bản phát hành Queens, Neutron LBaaS đã deprecated và thay thế bởi Octavia.

## Octavia Glossary

**Amphora**: Virtual machine, container, dedicated hardware, appliance hoặc thiết bị mà thực sự thực hiện công việc load balancing trong hệ thống Octavia. Cụ thể hơn, 1 amphora nhận requests từ client trên frontend và phân phối chúng về backend. Amphora giao tiếp với các controller của chúng trên LB network thông qua 1 driver interface trên controller.

**Amphora Load Balancer Driver**: Thành phần của controller mà xử lý tất cả các giao tiếp với amphora. Drivers giao tiếp với controller thông qua 1 generic base class và khởi tạo phương thức, và dịch chúng thành lệnh điều khiển tương ứng với loại phần mềm đang chạy ở backend amphora tương ứng với driver. Giao tiếp này xảy ra trên LB network.

**Apolocation**: Thuật ngữ sử dụng để mô tả khi 2 hoặc nhiều amphora không được đặt cùng 1 phần cứng vật lý. Cũng có thể được sử dụng để mô tả 2 hoặc nhiều LB mà không được đặt chung 1 amphora.

**Controller**: Daemon với khả năng truy cập đến cả LB Network và các thành phần OpenStack, thứ mà định vị và quản lý hoạt động chung của hệ thống cân bằng tải Octavia. Controllers sẽ luôn sử dụng 1 abstracted driver interface (thường là 1 base class) để giao tiếp với nhiều thành phần khác nhau trong môi trường OpenStack để tạo kết nối lỏng (loose coupling) với những thành phần này. Controllers còn được gọi là bộ não của Octavia.

**HAProxy**: Phần mềm LB được dùng trong triển khai của Octavia. HAProxy chạy trên amphora và thực sự là thành phần thực hiện các tác vụ cân bằng tải.

**Health Monitor**: Một đối tượng mà định nghĩa phương thức kiểm tra cho mỗi thành viên của pool. Bản thân health monitor là 1 pure-db object, thứ mà mô tả phương thức phần mềm cân bằng tải trên amphora nên sử dụng để giám sát health của các thành viên backend trong pool.

**L7 Policy**: Tập hợp của các L7 rule mà được thực hiện phép toán Logic AND với nhau cũng như 1 policy định tuyến cho bất kỳ HTTP hoặc HTTPS termination mà khớp với rules trên. 1 L7 Policy được tạo ra với chính xác 1 HTTP hoặc terminated HTTPS listener. VD: 1 người dùng có thể chỉ định 1 L7 policy mà bất kỳ client request nào khớp L7 rule "request URI start with '/api" sẽ được định tuyến đến "api" pool.

**L7 Rule**: Một biểu thức logic sử dụng để khớp 1 điều kiện đưa ra trong HTTP hoặc terminated HTTPS request. L7 rules thường khớp với 1 header chỉ định hoặc 1 phần của URI và thường được dùng chung với L7 policies để đạt được L7 switching. 1 L7 rule được tạo ra với chính xác 1 L7 policy. VD: ta có thể chỉ định L7 rule khớp với bất kỳ request có URI path bắt đầu với "/api".

**L7 Switching**: Đây là 1 tính năng cân bằng tải chỉ định cho HTTP hoặc terminated HTTPS sessions, ở đây các request khác nhau từ client được định tuyến đến nhiều backend pool khác nhau phụ thuộc vào 1 hoặc nhiều L7 policies. VD: sử dụng L7 switching, 1 người dùng có thể chỉ định rằng bất kỳ request với 1 URI path bắt đầu bằng "/api" sẽ được định tuyến về "api" backend pool, tất cả request còn lại định tuyến về default pool.

**LB Network**: Load Balancer Network, là nơi mà controllers và amphora giao tiếp với nhau. Bản thân LB network thường là nova hoặc neutron network, thứ mà controller và amphora đều có thể truy cập, nhưng không được tạo ra với bất kỳ tenant nào. LB Network nhìn chung cũng không phải là 1 phần của undercloud và không nên được expose trực tiếp đến bất kỳ thành phần OpenStack core khác ngoài Octavia Controllers.

**Listener**: Đối tượng đại diện cho endpoint lắng nghe của LB service. TCP/UDP port, cunghx như thông tin giao thức và các chi tiết chỉ định giao thức khác là thuộc tính của listener. Lưu ý rằng, địa chỉ IP **không** phải là 1 trong những thuộc tính của Listener.

**Load Balancer**: Đối tượng mô tả 1 nhóm logic của các listener trên 1 hoặc nhiều VIPs và liên kết với 1 hoặc nhiều amphora. Load balancer tồn tại trên nhiều hơn 1 amphora phụ thuộc vào topology được sử dụng. Load balancer cũng thường là root object dùng trong nhiều Octavia APIs.

**Load Balancing**: Quá trình lấy client requests trên 1 frontend interface và phân phối chúng đến 1 số lượng backend server dựa theo các rule. Load balancing cho phép nhiều server tham gia vào vận chuyển TCP hoặc UDP service đến client mà trong suốt, tính sẵn sàng cao và scalable theo góc nhìn của client.

**Member**: Đối tượng đại diện 1 backend server hoặc hệ thống mà là 1 phần của 1 pool. 1 member chỉ được liên kết tới 1 pool.

**Octavia**: Octavia là 1 giải pháp cân bằng tải mã nguồn mở operator-grade. Còn được biết tới là Octavia system hoặc Octavia project. Thuật ngữ này đề cập đến tổng thể Octavia system chứ không phải là 1 thành phần cụ thể.

**Pool**: Đối tượng đại diện nhóm của các member mà listener điều hướng client request tới. Lưu ý là 1 pool được liên kết với chỉ 1 listener, nhưng 1 listener có thể tham chiếu tới một vài pool (và chuyển đổi linh hoạt giữa chúng thông qua L7 policy)

**TLS Termination**: (Transport Layer Security Termination) Là loại giao thức cân bằng tải nơi mà HTTPS sessions được terminated (giải mã) trên amphora để tránh các gói tin mã hóa được điều phối tới backend server mà không được giải mã ở amphora. Lợi ích chính của loại cân bằng tải này là payload có thể được đọc/xử lý bởi amphora, và nhờ đó các tác vụ xử lý liên quan đến mã hóa/giải mã không còn phải nhờ đến backend server.

**Virtual IP Address**: là IP mà gắn với load balancer. VIP có thể được chỉ định đến một vài amphora, và 1 giao thức layer-2 như CARP, VRRP, hoặc HSRP có thể được dùng để duy trì tính sẵn sàng của nó. Ở layer-3 (định tuyến) topologies, địa chỉ VIP có thể được chỉ định đến thiết bị upstream networking mà định tuyến gói tin đến amphora, thứ mà sau đó load balance client request đến backend member

![](/images/Octavia_2.png)