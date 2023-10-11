# Nova Placement và Nova Conductor

## I. Nova placement

Dịch vụ API placement được giới thiệu trong bản phát hành Newton 14.0.0 trong kho lưu trữ Nova và được trích xuất vào kho lưu trữ vị trí trong bản phát hành Stein 19.0.0

Gồm có một REST API và data model sử dụng cho việc theo dõi các tài nguyên đã sử dụng và chưa được sử dụng giữa các loại tài nguyên khác nhau

VD: 1 resource provider có thể là 1 compute node, storage pool hoặc là 1 dải IP. Placement service theo dõi tài nguyên dư thừa và tài nguyên đã được sử dụng trên mỗi resource provider. Khi 1 instance được tạo trên compute node, sẽ sử dụng tài nguyên RAM, CPU từ compute node resource provider, disk từ một external storage provider

Các loại tài nguyên được theo dõi như classes. Dịch vụ này cung cấp một chuẩn resource classes (ví dụ DISK_GB, MEMORY_MB và vCPU) và cung cấp khả năng định nghĩa tùy chọn các resource classes nếu cần

Mỗi resource provider cũng có thể bao gồm nhiều tập hợp các đặc điểm mô tả từng khía cạnh của resource provider. VD available disk có thể không chỉ HDD mà còn có thể là SSD (traits)

## II. Nova-conductor

Conductor như 1 nơi điều phối các task. Rebuilt, resize/migrate và building một instance đều được quản lý ở đây. Điều này làm cho việc phân chia trách nhiệm tốt hơn giữa những gì compute nodes nên xử lý và những gì scheduler nên được xử lý, để dọn dẹp các path của execution

VD: một old process để bulding một instance là:
- API nhận request để build một instance
- API gửi 1 RPC cast để scheduler chọn 1 compute
- Scheduler gửi 1 RPC cast để compute build một instance, scheduler có thể sẽ cần giao tiếp với tất cả các compute
   - Nếu build thành công thì dừng ở đây
   - Nếu thất bại thì compute sẽ quyết định nếu max number của scheduler retries là hit thì dừng lại ở đó. Nếu việc build được lên lịch lại thì compute sẽ gửi 1 RPC cast tới scheduler để chọn 1 compute khác

```Nova-conductor``` là 1 RPC server. Trong ```nova-conductor``` sẽ có hàng loạt các API, nhiệm vụ chính sẽ là một proxy line tới database và tới các RPC server khác như ```nova-api``` và ```nova-network```. RPC client sẽ nằm trong ```nova-compute```

Khi muốn upstate một VM trên ```nova-compute```, thay vì kết nối trực tiếp đến DB thì ```nova-compute``` sẽ call đến ```nova-conductor``` trước, sau đó ```nova-conductor``` sẽ thực hiện kết nối tới DB và upstate VM trong DB

### Lợi ích và hạn chế của Nova-conductor

**Bảo mật:**
- **Lợi ích:** nếu không có thành phần nova-conductor service, tất cả các compute node có nova-compute service sẽ có quyền truy cập trực tiếp vào database bằng việc sử dụng conductor API, khi compute-node bị tấn công thì attacker sẽ có toàn quyền để xâm nhập vào DB
- **Hạn chế:** Nova-conductor API đã hạn chế quyền hạn kết nối tới database của nova-compute nhưng các service khác vẫn có quyền truy cập trực tiếp vào DB. Với 1 môi trường multi-host, nova-compute, nova-api,metadata, nova-network đều chạy trên compute node và vẫn tham chiếu trực tiếp đến DB

**Nâng cấp:** Nova-conductor đứng giữa nova-compute và database. Nếu DB schema update thì sẽ không update trên nova-compute trên cùng 1 thời điểm, thay vào đó nova-conductor sẽ sử dụng những API tương thích để làm việc với DB