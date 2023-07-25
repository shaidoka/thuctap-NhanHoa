# Blocking a known malicious actor

Trong bài viết này, chúng ta sẽ tìm hiểu cách để block địa chỉ IP khả nghi từ việc truy nhập tài nguyên web trên 1 web server. 

Trường hợp này sử dụng 1 public IP reputation database mà bao gồm những địa chỉ IP của 1 vài tác nhân bất hợp pháp. 1 IP reputation database là 1 tổng hợp của các địa chỉ IP mà bị đánh dấu là đáng ngờ. Chúng ta sẽ thêm IP của 1 endpoint bất kỳ vào reputation database. Sau đó, cấu hình Wazuh để block endpoint này khỏi truy nhập tài nguyên web trên Apache webserver trong vòng 60s. Đây chính là 1 cách để cảnh cáo kẻ tấn công không nên tiếp tục hành vi bất chính.

Trong use case này, chúng ta sử dụng **Wazuh CDB list** và **active response** capabilities