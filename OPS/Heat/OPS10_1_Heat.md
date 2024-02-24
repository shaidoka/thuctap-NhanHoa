# Heat - Openstack Orchestration Service

Heat là 1 dịch vụ để điều phối các ứng dụng trên cloud sử dụng 1 định dạng mẫu khai báo (declarative template format) thông qua 1 OpenStack-native REST API.

Mục đích và tầm nhìn của **Heat**:

- Heat cung cấp 1 template điều phối cơ sở để mô tả 1 ứng dụng cloud bằng cách thực thi các lời gọi đến OpenStack API thích hợp để khởi tạo các ứng dụng cloud.
- 1 Heat template mô tả cấu trúc cho 1 ứng dụng đám mây trong những tệp văn bản bằng 1 ngôn ngữ mà có con người có thể đọc và hiểu được, và có thể quản lý bởi các công cụ quản lý phiên bản được (version control tools).
- Các template chỉ định mối liên hệ giữa các tài nguyên (VD: volume này được kết nối với server kia). Điều này cho phép Heat gọi đến OpenStack APIs để tạo cơ sở hạ tầng theo một trình tự chuẩn xác để chạy ứng dụng của bạn một cách hoàn thiện.
- Ứng dụng tích hợp với các thành phần khác của OpenStack. Các template cho phép tạo hầu hết các loại tài nguyên trong OpenStack (như instance, floating IPs, volumes, security groups, users, etc...), cũng như các chức năng cao cấp hơn như instance với HA, instance autoscaling, và nested-stack.
- Heat mặc định quản lý cơ sở hạ tầng, nhưng các template tích hợp với nhiều công cụ quản lý cấu hình phần mềm khác như Puppet hay Ansible.
- Người quản trị có thể tùy biến khả năng của Heat bằng cách cài đặt các plugins.