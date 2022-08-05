# NAT

## Giới thiệu chung

NAT (hay Network Address Translation) là một kỹ thuật cho phép chuyển đổi từ một địa chỉ IP này thành 1 địa chỉ IP khác. Thông thường, NAT được dùng phổ biến trong mạng sử dụng địa chỉ cục bộ, cần truy cập đến mạng công cộng (Internet) Vị trí thực hiện NAT là router biên kết nối giữa 2 mạng

## Một số thuật ngữ:

- Địa chỉ inside local: là địa chỉ IP gán cho một thiết bị ở mạng bên trong. Địa chỉ này hầu như không phải địa chỉ được cấp bởi NIC (Network Information Center) hay nhà cung cấp dịch vụ

- Địa chỉ inside global: là địa chỉ đã được đăng ký với NIC, dùng để thay thế 1 hay nhiều địa chỉ IP inside local

- Địa chỉ outside local: là địa chỉ IP của một thiết bị ở mạng bên ngoài. Các thiết bị thuộc mạng bên trong sẽ tìm thấy thiết bị thuộc mạng bên ngoài thông qua địa chỉ IP này. Địa chỉ này không nhất thiết là địa chỉ được đăng ký, nó được lấy từ không gian địa chỉ bên trong

- Địa chỉ outside global: là địa chỉ IP gán cho 1 thiết bị ở mạng bên ngoài. Địa chỉ này được lấy ừ địa chỉ có thể dùng để định tuyến toàn cầu hay từ không gian địa chỉ mạng

## Cách thức hoạt động của NAT

NAT sử dụng IP của chính nó làm IP công cộng cho mỗi máy client với IP riêng. Khi một máy con thực hiện kết nối hoặc gửi dữ liệu tới 1 máy tính nào đó trên Internet, dữ liệu sẽ được gửi tới NAT, sau đó NAT sẽ thay thế địa chỉ IP gốc của máy con đó rồi gửi gói dữ liệu với địa chỉ IP của NAT. Máy tính từ xa hoặc máy tính nào đó trên Internet khi nhận được tín hiệu sẽ gửi gói tin trở về cho NAT computer bởi chúng nghĩ rằng NAT computer là máy đã gửi những gói dữ liệu đi. NAT ghi lại bảng thông tin của những máy tính đã gửi những gói thông tin ra ngoài trên mỗi cổng dịch vụ và gửi những gói tin nhận được về đúng client đó.

## STATIC NAT 

Static NAT được dùng để chuyển đổi 1 địa chỉ IP này sang 1 địa chỉ khác một cách cố định, thông thường là từ một địa chỉ cục bộ sang một địa chỉ công cộng và quá trình này được cài đặt thủ công, nghĩa là địa chỉ được ánh xạ được chỉ định rõ ràng tương ứng duy nhất

STatic NAT rất hữu ích trong trường hợp những thiết bị cần phải có địa chỉ cố định để có thể truy cập từ bên ngoài Internet. Những thiết bị này phổ biến là Server như Web, Mail,...

**Cách cấu hình Static NAT**

- Thiết lập mối quan hệ chuyển đổi giữa địa chỉ nội bộ bên trong và địa chỉ đại diện bên ngoài

```sh
Router(config)#ip nat inside source static local-ip global-ip
```

- Xác định các cổng kết nối vào mạng bên trong và thực hiện lệnh

```sh
Router(config-if)#ip nat inside
```

- Xác định các cổng kết nối ra mạng công cộng bên ngoài và thực hiện lệnh

```sh
Router(config-if)#ip nat outside
```

**VD**

```sh
Router(config)#ip nat inside source static 192.168.1.100 202.1.1.10
Router(config)#interface fa0/0
Router(config-if)#ip nat inside 
Router(config)#interface S0/0/0
Router(config-if)#ip nat outside
```

## DYNAMIC NAT

Dynamic NAT được dùng để ánh xạ một địa chỉ IP này sang một địa chỉ khác một cách tự động, thông thường là ánh xạ từ một địa chỉ cục bộ sang một địa chỉ được đăng ký. Bất kỳ một địa chỉ IP nào nằm trong dải địa chỉ IP công cộng đã được định trước đều có thể gán cho một thiết bị trong mạng

**Cách cấu hình Dynamic NAT**

- Xác định dải địa chỉ đại diện bên ngoài (public): các địa chỉ NAT

```sh
Router(config)#ip nat pool name start-ip end-ip [netmask <netmask>/prefix-length <prefix-length>]
```

- Thiết lập ACL cho phép những địa chỉ nội bộ bên trong nào được chuyển đổi: các địa chỉ được NAT

```sh
Router(config)#access-list access-list-number permit source [source-wildcard]
```

- Thiết lập mối quan hệ giữa địa chỉ nguồn đã được xác định trong ACL với dải địa chỉ đại diện ra bên ngoài

```sh
Router(config)#ip nat inside source list <acl-number> pool <name>
```

- Xác định các cổng kết nối vào mạng nội bộ

```sh
Router(config-if)#ip nat inside
```

- Xác định các cổng kết nối ra bên ngoài

```sh
Router(config-if)#ip nat outside
```

**VD**

```sh
Router(config)#ip nat pool abc 202.1.1.177 202.1.1.185 netmask 255.255.255.0
Router(config)#access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)#ip nat inside source list 1 pool abc
Router(config-if)#ip nat inside
Router(config)#interface S0/0/0
Router(config-if)#ip nat outside
```

## NAT OVERLOAD

NAT Overload là một dạng của Dynamic NAT, nó thực hiện ánh xạ nhiều địa chỉ IP thành 1 địa chỉ (many-to-one) và sử dụng các chỉ số cổng khác nhau để phân biệt cho từng chuyển đổi. NAT Overload còn có tên gọi khác là PAT (Port Address Translation)

Chỉ số cổng được mã hóa thành 16 bit, do đó có tới 65536 địa chỉ nội bộ có thể được chuyển sang 1 địa chỉ công cộng

**Cách cấu hình NAT Overload**

- Xác định dãy địa chỉ bên trong cần chuyển dịch ra beenngoafi (private ip addresses range)

```sh
Router(config)#access-list <ACL-number> permit <source> <wildcard>
```

- Cấu hình chuyển đổi dia chi IP sang cổng nối ra ngoài

```sh
Router(config)#ip nat inside source list <ACL-number> interface <interface> overload
```

- Xác định các cổng nối vào mạng bên trong và nối ra mạng bên ngoài

```sh
#Đối với các cổng nối vào mạng bên trong
Router(config-if)#ip nat inside
#Đối với các cổng nối ra mạng bên ngoài
Router(config-if)#ip nat outside
```

**VD**

```sh
R(config)#access-list 1 permit 192.168.1.0 0.0.0.255
R(config)#ip nat inside source list 1 interface s0/0/0 overload
R(config)#interface fa0/0
R(config-if)#ip nat inside
R(config)#interface S0/0/0
R(config-if)#ip nat outside
```

## Ưu nhước điểm của NAT

- Ưu điểm:
   - Tiết kiệm không gian địa chỉ IPv4
   - Giúp che giấu IP bên trong mạng LAN
   - NAT có thể chia sẻ kết nối internet cho nhiều máy tính, thiết bị di động khác nhau trong mạng LAN chỉ với một địa chỉ IP duy nhất
   - NAT giúp nhà quản trị mạng lọc được gói tin đến và xét quyền truy cập của IP public đến 1 port bất kỳ

- Nhược điểm:
   - CPU tốn thời gian để chuyển đổi địa chỉ IP, làm tăng độ trễ trong quá trình switching, làm ảnh hưởng đến tốc độ đường truyền của mạng internet
   - NAT che giấu địa chỉ IP trong mạng LAN làm kỹ thuật viên khó khăn khi cần kiểm tra nguồn gốc IP hoặc truy vết gói tin
   - 1 vài ứng dụng sử dụng địa chỉ IP không thể hoạt động được khi có NAT


