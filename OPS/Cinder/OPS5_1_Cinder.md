# Tổng quan về Cinder

## I. Giới thiệu

- Cinder là 1 dịch vụ lưu trữ khối (block storage service) cho OPS
- Mô tả ngắn gọn Cinder ảo hóa việc quản lý các block storage device và cung cấp cho end users API tự phục vụ để yêu cầu và sử dụng các tài nguyên đó mà không quan tâm đến về storage của họ được triển khai trên thiết bị nào
- Là 1 dịch vụ quản lý, Cinder kiểm soát việc cung cấp và quản lý block storage volumes
- Cinder và Nova Logical Architecture

![](./images/OPS5_1.jpg)

## II. Các hình thức lưu trữ trong OPS

||Lưu trữ tạm thời|Block storage|Object Storage|
|:-|:-|:-|:-|
|Hình thức sử dụng|Dùng để chạy hệ điều hành|Thêm 1 persistent storage vào VM|Lưu trữ các VM image, disk volume, snapshot VM,...|
|Hình thức truy cập|Qua 1 file system|Một block device có thể là 1 partition, formated, mounted|Thông qua REST API|
|Có thể truy cập từ|Trong 1 VM|Trong 1 VM|Bất kỳ đâu|
|Quản lý bởi|NOVA|Cinder|Swift|
|Những vấn đề tồn tại|VM được kết thúc|Có thể được xóa bởi user|Có thể xóa được bởi user|
|Kích cỡ được xác định bởi|Người quản trị cấu hình hệ thống|Dựa theo yêu cầu của người dùng|Số lượng lưu trữ vật lý hiện có|

## III. Một số khái niệm

**Share storage:** là hệ thống lưu trữ được sử dụng chung bởi nhiều người hay máy tính. Nó lưu trữ tất cả các tệp trong một kho lưu trữ tập trung và cho phép nhiều người dùng truy cập chúng cùng 1 lúc

**Scale up:** nâng cấp những thứ hiện có để có hiệu năng tốt hơn và xử lý nhiều tải hơn. VD: thay thế CPU 2 core thành 4 core

**Scale out:** thêm nhiều thành phần tương tự hiện có để chia tải, đồng thời phải sử dụng các giải pháp cân bằng tải (load balancing)

**File storage:** lưu trữ cấp độ tệp hoặc lưu trữ dựa trên tệp, là 1 phương pháp lưu trữ phân cấp được sử dụng để tổ chức và lưu trữ dữ liệu trên ổ cứng máy tính hoặc trên NAS (network-attached storage). Thường được sử dụng cho dữ liệu có cấu trúc và dung lượng không quá lớn

**Block storage:** lưu trữ dựa trên các khối. Là một công nghệ được sử dụng để lưu trữ các file dữ liệu trên SANs (Storage Area Networks) hoặc cloud. Block storage chia dữ liệu thành các khối và sau đó lưu trữ các khối dưới dạng các phần riêng biệt, mỗi khối có mã định danh duy nhất. Điều đó có nghĩa là nó có thể lưu trữ các khối đó trên hệ thống khác nhau và mỗi khối có thể được cấu hình (hoặc phân vùng) để hoạt động với các hệ điều hành khác nhau. Nó tách dữ liệu môi trường người dùng, cho phép dữ liệu đó được trải rộng trên nhiều môi trường

**Object storage:** lưu trữ dựa trên đối tượng. Thường được sử dụng để xử lý khối lượng lớn dữ liệu phi cấu trúc. Đây là dữ liệu không phù hợp hoặc không thể được tổ chức dễ dàng vào CSDL quan hệ truyền thống với các hàng và cột. Dữ liệu phi cấu trúc bao gồm: email, hình ảnh, video,... Object storage không sử dụng thư mục hay hệ thống phân cấp phức tạp nào. Thay vào đó, mỗi object là một kho lưu trữ độc lập gồm nhiều dữ liệu, metadata, và ID xác thực để ứng dụng truy cập. Object storage thường lưu trữ dữ liệu không thay đổi thường xuyên hoặc hoàn toàn tĩnh, chẳng hạn như hồ sơ giao dịch hoặc tệp nhạc, hình ảnh và video

## IV. Kiến trúc Cinder

![](./images/OPS5_2.jpg)

- ```cinder-client```: User sử dụng CLI/UI để tạo request
- ```cinder-api```: Chấp nhận và định tuyến cho các request
- ```cinder-scheduler```: Lên lịch trình và định tuyến cho các request đến volume service thích hợp
- ```cinder-volume```: Quản lý thiết bị block storage
- ```driver```: Chứa các loại mã backend cụ thể để giao tiếp với các loại storage khác nhau
- ```storage```: Các thiết bị lưu trữ từ các provider khác nhau
- ```SQL DB```: Lưu lại thông tin về các volumes sử dụng
- ```cinder-backup```: Cung cấp phương pháp để backup 1 volume đến Swift/Ceph,...

## V. Các thành phần trong Cinder

- Backend Storage device:
  - Mặc định sử dụng LVM trên nhóm local volume (cinder-volume)
  - Hỗ trợ thiết bị như mảng external RAID hoặc các thiết bị lưu trữ
  - Kích thước Block có thể điều chỉnh khi dùng KVM hoặc QEMU
- Users / Project:
  - Dùng Role-based Access Control (RBAC) khi nhiều người sử dụng để kiểm soát các hành động mà người dùng được phép thực hiện
  - Sử dụng file "policy.json" để cấu hình các thiết lập cho mỗi vai trò
  - Volume được mở cho mỗi user truy cập vào và sử dụng Key Pairs, nhưng hạn ngạch để kiểm soát sự tiêu thụ tài nguyên trên các tài nguyên phần cứng đối với mỗi project
- Volumes, Snapshots và Backups:
  - **Volumes**: Phân bổ block storage resource có thể gắn liền với các trường hợp như lưu trữ thứ cấp hoặc chúng có thể được sử dụng là vùng lưu trữ cho root dùng để boot máy ảo. Là thiết bị lưu trữ RW gắn kết vào compute node thông qua iSCSI
  - **Snapshots**: Một bản copy trong 1 thời điểm nhất định của một volume. Các snapshot có thể được tạo ra từ volume đang sử dụng. Các snapshot có thể được sử dụng để tạo volume mới
  - **Backups**: Một bản sao lưu của volume được lưu trong OPS object storage (Swift)

## VI. Các phương thức boot máy ảo (Cinder POV)

- **Image:** Tạo một ephemeral disk từ image đã chọn

- **Volume:** Boot máy ảo từ 1 bootable volume đã có sẵn

- **Image (tạo một volume mới):** Tạo một bootable volume mới từ image đã chọn và boot máy ảo từ đó

- **Volume snapshot (tạo một volume mới):** Tạo 1 volume từ volume snapshot đã chọn và boot máy ảo từ đó

### Điểm khác nhau giữa Ephemeral và Volume boot disk

**Ephemeral Boot Disk**
- Ephemeral disk là disk ảo mà được tạo cho mục đích boot một máy ảo và nên được coi là nhất thời
- Ephemeral disk hữu dụng trong trường hợp ta không lo lắng về nhu cầu nhân đôi một máy ảo hoặc hủy 1 máy ảo và dữ liệu trong đó sẽ mất hết. Ta vẫn có thể mount một volume trên một máy ảo được boot từ 1 ephemeral disk và đẩy bất kỳ data nào cần thiết để lưu lại trong volume

Một số đặc tính:
- Không sử dụng hết volume quota: nếu bạn có nhiều instance quota, bạn có thể boot chúng từ ephemeral disk ngay cả khi không có nhiều volume quota
- Bị xóa khi VM bị xóa. Dữ liệu trong ephemeral disk sẽ bị mất khi xóa máy ảo

**Volume Boot Disk**
- Volume là dạng lưu trữ bền vững hơn ephemeral disk và có thể dùng để boot như 1 block device có thể mount được
- Volume boot disk hữu dụng khi bạn cần duplicate 1 VM hoặc backup chúng bằng cách snapshot, hoặc nếu bạn muốn dùng phương pháp lưu trữ đáng tin cậy hơn là ephemeral disk. Nếu dùng dạng này, cần có đủ quota cho các VM cần boot

Một số đặc tính:
- Có thể snapshot
- Không bị xóa khi xóa máy ảo: có thể xóa máy ảo nhưng dữ liệu vẫn còn trong volume
- Sử dụng hết volume quota: volume quota sẽ được sử dụng hết khi dùng tùy chọn này