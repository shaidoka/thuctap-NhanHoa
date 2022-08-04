# NAT

## Giới thiệu chung

NAT (hay Network Address Translation) là một kỹ thuật cho phép chuyển đổi từ một địa chỉ IP này thành 1 địa chỉ IP khác. Thông thường, NAT được dùng phổ biến trong mạng sử dụng địa chỉ cục bộ, cần truy cập đến mạng công cộng (Internet) Vị trí thực hiện NAT là router biên kết nối giữa 2 mạng

## Một số thuật ngữ:

- Địa chỉ inside local: là địa chỉ IP gán cho một thiết bị ở mạng bên trong. Địa chỉ này hầu như không phải địa chỉ được cấp bởi NIC (Network Information Center) hay nhà cung cấp dịch vụ

- Địa chỉ inside global: là địa chỉ đã được đăng ký với NIC, dùng để thay thế 1 hay nhiều địa chỉ IP inside local

- Địa chỉ outside local: là địa chỉ IP của một thiết bị ở mạng bên ngoài khi nó xuất hiện bên trong mạng. Địa chỉ này không nhất thiết là địa chỉ được đăng ký, nó được lấy từ không gian địa chỉ bên trong

- Địa chỉ outside global: là địa chỉ IP gán cho 1 thiết bị ở mạng bên ngoài. Địa chỉ này được lấy ừ địa chỉ có thể dùng để định tuyến toàn cầu hay từ không gian địa chỉ mạng

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