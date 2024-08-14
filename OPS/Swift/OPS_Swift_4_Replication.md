# Replication

Vì mỗi replica trong Object Storage hoạt động độc lập và clients thường chỉ cần đa số các nodes phản hồi để xem xét 1 hành động là thành công, do đó các lỗi ngay cả khi là nhất thời như lỗi mạng có thể nhanh chóng khiến các bản replicas bị bất đồng bộ. Những thay đổi này cuối cùng được xử lý bởi các tiến trình asynchronous, peer-to-peer replicator. Các tiến trình replicator đi qua local filesystem và thực hiện các hành động đồng thời theo cách cân bằng tải trên các đĩa vật lý.

Replication sử dụng 1 mô hình push, với các bản ghi và files cơ bản là chỉ được sao chép từ local sang remote replicas. Điều này là quan trọng vì dữ liệu trên node có thể không thuộc về nơi đó (như trong trường hợp chuyển giao và thay đổi ring), và 1 replicator không thể biết được nó nên pull data nào từ đâu trong cluster. Bất kỳ node mà chứa data phải đảm bảo data này được lấy từ nơi nó thuộc về. Ring xử lý phần replica placement.

Để replicate các thao tác xóa thay vì chỉ tạo, mọi bản ghi hoặc tệp đã xóa trong hệ thống phải được đánh dấu bởi tombstone. Tiến trình replication dọn dẹp các tombstones sau 1 khoảng thời gian mà được cấu hình trong tham số ```consistency window```. Khoảng thời gian này định nghĩa thời gian mà replication kéo dài, và bao lâu để các lỗi tạm thời có thể xóa 1 node khỏi cluster. Tombstone cleanup phải được liên kết chặt chẽ với replication để giúp replica đồng bộ.

Nếu 1 replicator phát hiện rằng 1 remote drive lỗi, replicator sử dụng ```get_more_nodes``` interface cho ring để chọn 1 node thay thế để đồng bộ hóa. Replicator có thể duy trì replication level mong muốn khi disk bị lỗi, mặc dù một vài vị trí replicas có thể không ở vị trí có thể sử dụng ngay lập tức.

Có 2 loại replication chính là:

- **Database replication**: Replicate containers và objects
- **Object replication**: Replicates object data

## Database replication

Database replication hoàn thành 1 phép so sánh low-cost hash để xác định liệu 2 replicas có khớp nhau hay chưa. Thông thường, kiểm tra này có thể nhanh chóng xác nhận rằng hầu hết databases trong hệ thống đã được đồng bộ rồi. Nếu có các mã băm khác biệt, replicator sẽ đồng bộ các databases bằng cách chia sẻ các bản ghi đã thêm kể từ lần đồng bộ trước.

Thời điểm đồng bộ là 1 con dấu mà ghi lại thời điểm cuối cùng mà 2 databases được biết là đã đồng bộ, và nó lưu trữ trong mỗi database như 1 tuple của remote database ID và record ID. Database IDs là duy nhất trên toàn bộ replicas của database, và record IDs là các số tự nhiên tăng dần. Nếu tất cả các records được push đến remote database, toàn bộ bảng đồng bộ của local database được push, thì remote database có thể chắc chắn là đã đồng bộ tất cả mọi thứ với local database.

Nếu 1 replica bị thiếu đi, toàn bộ tệp trong local database sẽ được truyền đến peer bằng rsync và được cấp 1 ID mới.

Trong thực tế, database replication có thể xử lý hàng trăm databases mỗi giây dựa trên cấu hình (lên tới con số của CPUs hoặc disks khả dụng) và được giới hạn bởi số lượng database transactions mà phải được thực hiện.

## Object replication

Ban đầu thì object replication sẽ thực hiện 1 rsync để đẩy dữ liệu từ local partition đến tất cả remote servers nơi mà dự định sẽ đặt dữ liệu. Mặc dù điều này hoạt động tốt ở quy mô nhỏ, thời gian sao chép tăng lên rất cao khi cấu trúc thư mục không đủ nhỏ để lưu giữ trong RAM. Sơ đồ này đã được sửa đổi để lưu 1 hash của nội dung cho mỗi đường dẫn hậu tốt vào 1 tệp hash cho mỗi partition. Mã hash cho mỗi đường dẫn hậu tố không còn khả dụng khi nội dung của đường dẫn hậu tố đó bị thay đổi.

Tiến trình object replication đọc trong các tệp hash và tính toán bất kỳ hash không hợp lệ nào. Sau đó, nó truyền các mã hash đến từng remote server mà giữ partition, và chỉ các đường dẫn hậu tố với các hash khác nhau trên remote server là được rsync. Sau khi đẩy các file đến remote server, tiến trình replication thông báo nó tính toán các hash cho các đường dẫn hậu tố đã rsync.

Số lượng đường dẫn không được cache mà object replication phải đi qua, thông thường là do các mã hash của đường dẫn hậu tố bị vô hiệu hóa, làm giảm hiệu suất. Để cung cấp tốc độ replication chấp nhận được, object replication được thiết kế để vô hiệu hóa khoảng 2% không gian hash trên 1 node bình thường mỗi ngày.