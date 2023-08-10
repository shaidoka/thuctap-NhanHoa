# Xây dựng luồng CICD với Gitlab và Jenkins

Một lợi thế lớn mà K8s đem lại đó là khả năng CICD vô cùng thuận tiện cho developer. Là một người phát triển phần mềm, hẳn chúng ta không muốn cứ mỗi lần thay đổi một điều gì đó nhỏ nhặt trong code là lại phải compile, đóng chart, rồi deploy lên server tốn kém rất nhiều thời gian. CICD sinh ra để giải quyết bài toán này.

Trong bài trước chúng ta đã tìm hiểu cách để đóng gói ứng dụng thành helmchart và triển khai lên K8s. Sau khi dựng được helmchart thì việc áp dụng vào luồng CICD sẽ trở nên đơn giản và thuận tiện hơn nhiều.

Khi áp dụng CICD thì ngay trong môi trường dev ta đã thấy được lợi ích to lớn mà nó mang lại. Dev sau khi commit xong muốn test deploy lên môi trường Dev thì chỉ cần 1 click và ngồi chờ kết quả.

## Mô hình CICD cơ bản

