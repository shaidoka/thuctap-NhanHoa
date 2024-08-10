# Replication

Vì mỗi replica trong Object Storage hoạt động độc lập và clients thường chỉ cần đa số các nodes phản hồi để xem xét 1 hành động là thành công, do đó các lỗi ngay cả khi là nhất thời như lỗi mạng có thể nhanh chóng khiến các bản replicas bị bất đồng bộ. Những thay đổi này cuối cùng được xử lý bởi các tiến trình asynchronous, peer-to-peer replicator. Các tiến trình replicator đi qua local filesystem và thực hiện các hành động đồng thời theo cách cân bằng tải trên các đĩa vật lý.

Replication sử dụng 1 mô hình push, với các bản ghi và files cơ bản là chỉ được sao chép từ local sang remote replicas. Điều này là quan trọng vì dữ liệu trên node có thể không thuộc về nơi đó (như trong trường hợp chuyển giao và thay đổi ring), và 1 replicator không thể biết được nó nên pull data nào từ bất kể đâu trong cluster. Bất kỳ node mà chứa data phải đảm bảo data này được lấy từ nơi nó thuộc về. Ring xử lý phần replica placement.

Để replicate các thao tác xóa thay vì chỉ tạo, mọi bản ghi hoặc tệp đã xóa trong hệ thống phải được đánh dấu bởi tombstone. Tiến trình replication dọn dẹp các tombstones sau 1 khoảng thời gian mà được cấu hình trong tham số ```consistency window```. Khoảng thời gian này định nghĩa thời gian mà replication kéo dài, và bao lâu để các lỗi tạm thời có thể xóa 1 node khỏi cluster. Tombstone cleanup phải được liên kết chặt chẽ với replication để giúp replica đồng bộ.

Nếu 1 replicator phát hiện rằng 1 remote drive lỗi, replicator sử dụng ```get_more_nodes``` interface cho ring để chọn 1 node thay thế để đồng bộ hóa. Replicator có thể duy trì replication level mong muốn khi disk bị lỗi, mặc dù một vài vị trí replicas có thể không ngay lập tức sử dụng được luôn.

Có 2 loại replication chính là:

- **Database replication**: Replicate containers và objects
- **Object replication**: Replicates object data

## Data replication

