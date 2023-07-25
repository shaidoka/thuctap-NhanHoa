# Agentless monitoring

Wazuh server phân tích dữ liệu nó nhận được từ Wazuh agent để giám sát, phát hiện, và kích hoạt cảnh báo cho các sự kiện bảo mật hay hoạt động đáng ngờ trên endpoint. Tuy nhiên, không phải hệ thống nào cũng cho phép agent này được cài đặt. Wazuh giải quyết vấn đề này bằng tính năng Agentless monitoring.

Agentless monitoring là loại giám sát mà không cần cài đặt agent hay phần mềm nào lên endpoint. Cách tiếp cận này sử dụng các giao thức có sẵn để truy cập và thu thập thông tin từ endpoint được giám sát.

Tính năng agentless monitoring của wazuh sử dụng SSH để thu thập và chuyển sự kiện từ endpoint đến Wazuh server. Các nền tảng được hỗ trợ bao gồm router, firewall, switch, Linux/BSD. Nó cho phép endpoint với các hạn chế cài đặt phần mềm có thể được sử dụng bởi Wazuh.

## Cách thức hoạt động

Để giám sát endpoint mà không sử dụng agent, Wazuh cần 1 kết nối SSH giữa Wazuh server và endpoint được giám. Wazuh agentless monitoring module có thể thực hiện những hành động sau:
- Giám sát file, directories, hoặc cấu hình của endpoint
- Chạy lệnh trên 1 endpoint

**Giám sát files, directories, hoặc cấu hình của endpoint**: Ta có thể cấu hình Wazuh agentless monitoring module để giám sát file, directories, và Cisco PIX firewall và router configurations. Nếu có bất kỳ thay đổi nào trên các file cấu hình và directories của firewall hay router 

**Run command on an endpoint**: Ta có thể chỉ định lệnh để chạy trên endpoint được giám sát, và agentless monitoring module phát hiện output của những command này. Khi output của những lệnh này thay đổi, nó phát hiện và tạo cảnh báo

