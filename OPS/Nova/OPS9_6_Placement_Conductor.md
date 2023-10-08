# Nova Placement và Nova Conductor

## I. Nova placement

Dịch vụ API placement được giới thiệu trong bản phát hành Newton 14.0.0 trong kho lưu trữ Nova và được trích xuất vào kho lưu trữ vị trí trong bản phát hành Stein 19.0.0

Gồm có một REST API và data model sử dụng cho việc theo dõi các tài nguyên đã sử dụng và chưa được sử dụng giữa các loại tài nguyên khác nhau

VD: 1 resource provider có thể là 1 compute node, storage pool hoặc là 1 dải IP. Placement service theo dõi tài nguyên dư thừa và tài nguyên đã được sử dụng trên mỗi resource provider. Khi 1 instance được tạo trên compute node, sẽ sử dụng tài nguyên RAM, CPU từ compute node resource provider, disk từ một external storage provider

Các loại tài nguyên được theo dõi như classes. Dịch vụ này