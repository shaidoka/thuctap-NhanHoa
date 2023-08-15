# Xây dựng luồng CICD với Gitlab và Jenkins

Một lợi thế lớn mà K8s đem lại đó là khả năng CICD vô cùng thuận tiện cho developer. Là một người phát triển phần mềm, hẳn chúng ta không muốn cứ mỗi lần thay đổi một điều gì đó nhỏ nhặt trong code là lại phải compile, đóng chart, rồi deploy lên server tốn kém rất nhiều thời gian. CICD sinh ra để giải quyết bài toán này.

Trong bài trước chúng ta đã tìm hiểu cách để đóng gói ứng dụng thành helmchart và triển khai lên K8s. Sau khi dựng được helmchart thì việc áp dụng vào luồng CICD sẽ trở nên đơn giản và thuận tiện hơn nhiều.

Khi áp dụng CICD thì ngay trong môi trường dev ta đã thấy được lợi ích to lớn mà nó mang lại. Dev sau khi commit xong muốn test deploy lên môi trường Dev thì chỉ cần 1 click và ngồi chờ kết quả.

## Mô hình CICD cơ bản

Mô hình CICD được tham khảo có dạng như sau:

![](./images/K8s_CICD_1.jpg)

*Nguồn: Trịnh Quốc Việt - viblo.asia's content writer*

Trong đó tùy theo yêu cầu mà có thể tích hợp thêm các bước scan code, automation test nhưng trong phạm vi bài viết này không đề cập tới. Ngoài Gitlab và Jenkins, chúng ta hoàn toàn có thể sử dụng các công cụ có chung mục đích, như AWS Code Commit, Azure Repos, Gitlab Runner,...

Ý tưởng của bài viết này như sau:
- Commit code lên gitlab
- Pull source về Jenkins server để build
- Build docker image và push image lên registry
- Triển khai/cập nhật lên K8s bằng kubectl/helm

Do đó, các bước cần thực hiện trong bài này là:
- Tạo helmchart cho ứng dụng
- Cài đặt và cấu hình gitlab để quản lý source code
- Cài đặt và cấu hình Jenkins để tạo luồng CICD
- Tạo job pipline cho Jenkins, thực hiện và test từng bước nhỏ trong cả luồng CICD
- Thay đổi code và chạy CICD job để kiểm tra kết quả

## Tạo helmchart cho ứng dụng

Đã giới thiệu ở bài trước rồi.

## Cài đặt và cấu hình Gitlab

