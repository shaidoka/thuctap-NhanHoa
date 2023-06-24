# Giám sát tính toàn vẹn của file

File Intergrity Monitoring (FIM) là 1 tiến trình bảo mật sử dụng để giám sát tính toàn vẹn của tệp hệ thống và ứng dụng. FIM là 1 lớp bảo mật quan trọng cho bất kỳ tổ chức nào muốn giám sát các thông tin nhạy cảm. Nó cung cấp bảo vệ cho những dữ liệu nhạy cảm, ứng dụng, và tệp thiết bị bằng cách giám sát, quét định kỳ, và đảm bảo tính toàn vẹn của nó. Tính năng này giúp các tổ chức phát hiện những thay đổi đến file quan trọng trên hệ thống của họ, nhờ đó giảm rủi ro về mặt dữ liệu bị đánh cắp hoặc làm tổn hại.

Wazuh tích hợp tính năng để giám sát tính toàn vẹn của file. Wazuh FIM module giám sát tệp và đường dẫn và kích hoạt 1 cảnh báo khi 1 user hoặc tiến trình tạo, thay đổi, hay xóa tệp/đường dẫn đó. Khi 1 người dùng hoặc tiến trình thay đổi 1 file, module này sẽ so sánh checksum của nó và các thuộc tính với dữ liệu cơ sở. Cảnh báo được kích hoạt nếu nó tìm thấy điểm khác nhau. FIM module thực hiện real-time và lên lịch quét dựa vào thiết lập FIM cho agent và manager.

### Quản lý thay đổi

Wazuh FIM capability là 1 công cụ thiết yếu để đảm bảo tiến trình quản lý thay đổi đang hoạt động chính xác. Wazuh capability này cho phép ta phân tích các tệp để biết được nếu chúng thay đổi, cách thức, thời điểm, và người hoặc cái gì thay đổi chúng. Wazuh FIM module so sánh dữ liệu cơ sở với thông tin của phiên bản mới nhất của tệp. Việc so sánh này cung cấp cái nhìn vào sự thay đổi và cập nhật của các tệp quan trọng. Ví dụ, ta có thể sử dụng tính năng này để phát hiện các cập nhật không đúng vào ứng dụng hoặc những thay đổi không được cho phép vào tệp cấu hình.

### Phát hiện và phản hồi mối đe dọa

Ta có thể kết hợp FIM với các tính năng khác của Wazuh để phát hiện và phản hồi về threat. FIM capability giám sát tính toàn vẹn của tệp, phát hiện thay đổi về permission, và giám sát hoạt động của người và tệp.

### Tuân thủ quy định

FIM capability giúp các tổ chức đáp ứng các yêu cầu quy định về bảo mật dữ liệu, quyền riêng tư và lưu giữ dữ liệu. Theo dõi các tệp quan trọng để biết các thay đổi là một yêu cầu quan trọng đối với các quy định như PCI DSS, HIPAA và GDPR.