# Namespace trong Neutron

## I. Overlapping network trong OPS

- Overlapping được hiểu là một mạng máy tính được xây dựng trên một nền tảng network mạng sẵn
- Openstack cung cấp môi trường multi tenant. Mỗi tenant cung cấp một mạng private, router, firewall, LB riêng. Nhờ namespace cung cấp khả năng tách biệt các tài nguyên mạng giữa các tenant - network namespace để xem được namespace có thể sử dụng

```sh
ip netns list
```

Nếu bạn chưa thêm bất kỳ namespace nào, output sẽ trống. Namespace mặc định thì không được tính vào output của lệnh ```ip netns list```

- Các namespace hiển thị dưới dạng
   - ```qdhcp-*```
   - ```qrouter-*```
   - ```qlbaas-*```

## II. Linux network namespaces

Trong network namespace, scoped ```identifiers``` là các thiết bị mạng, ví dụ như: ```eth0```, tồn tại trong một namespace cụ thể

Linux khởi động với namespace mặc định, vì vậy nếu hđh của bạn không hoạt động gì đặc biệt, thì đó là vị trí của các thiết bị mạng (network devices). Nhưng cũng có thể tạo thêm các namespaces khác với namespace mặc định và tạo các thiết bị mạng mới trong namespace đó, hoặc move thiết bị hiện có từ namespace này sang namespace khác

Mỗi namespace đều có routing table (bảng định tuyến) và thực tế đây là lý do chính để namespace tồn tại. Bảng định tuyến được khóa bởi IP đích. Vì vậy, network namespace là những gì cần thiết nếu muốn cùng 1 IP đích có ý nghĩa khác nhau vào những thời điểm khác nhau

Mỗi namespace đều có bộ iptables riêng (cho cả IPv4 và IPv6). Vì vậy, có thể áp dụng các security khác nhau cho các luồng có cùng IP trong các namespace khác nhau, cũng như định tuyến khác nhau

Bất kỳ process của Linux nào đều chạy trong một network namespace cụ thể. Theo mặc định, process này được kế thừa từ parent process nhưng một process với các khả năng phù hợp có thể tự chuyển đổi sang một namespace khác. Trong thực tế, điều này chủ yếu được thực hiện bằng cách sử dụng lệnh ```ip netns exec NETNS COMMAND...```, bắt đầu chạy lệnh trong ns ```NETNS```. Giả sử một process như vậy gửi 1 message tới địa chỉ ```a.b.c.d```, ảnh hưởng của ns a.b.c.d sẽ được tra cứu trong bảng định tuyến của ns đó và sẽ xác định thiết bị mạng mà message được truyền qua

