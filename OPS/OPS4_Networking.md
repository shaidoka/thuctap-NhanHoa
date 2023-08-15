# Tổng quan về Networking

## 1. Giới thiệu Neutron

Trong OpenStack, các dịch vụ mạng được cung cấp bởi 1 project có tên là ```Neutron```. ```Neutron``` là 1 hệ thống dựa trên API để quản lý tài nguyên mạng vật lý và ảo trong OPS.

## 2. Cơ bản về Networking

### 2.1. Ethernet

- Ethernet là 1 giao thức mạng, chuẩn IEEE 802.3. Hầu hết các network interface card (NICs) đều kết nối bằng Ethernet
- Trong mô hình OSI, Ethernet thuộc layer 2 (data link layer)
- Trong Ethernet network, các host kết nối với mạng bằng cách trao đổi các frames. Mỗi host trên mạng Ethernet có 1 địa chỉ MAC duy nhất. Cụ thể, mỗi virtual machine trong OPS có 1 địa chỉ MAC duy nhất

### 2.2. Subnets và ARP

- NICs sử dụng địa chỉ MAC để xác định địa chỉ mạng của host, ứng dụng TCP/IP sử dụng địa chỉ IP. Address Resolution Protocol (ARP) là cầu nối giữa Ethernet và địa chỉ IP bằng cách dịch địa chỉ IP thành địa chỉ MAC
- Địa chỉ IP được chia thành 2 phần: ```network number``` và ```host identifier```. Hai host nằm trên cùng 1 subnet nếu chúng có cùng 1 ```network number```. 2 host chỉ có thể kết nối trực tiếp qua Ethernet nếu chúng ở trên cùng 1 local network. ARP giả định tất cả các PC trong cùng 1 subnet đều nằm trong 1 local network. Người quản trị mạng phải gắn địa chỉ IP và netmask cho host để 2 host cùng trong 1 subnet đều nằm trên 1 local network, nếu không ARP sẽ hoạt động không đúng
- Có 2 cú pháp để thể hiện netmask
   - dotted quad
   - classless inter-domain routing

### 2.3. DHCP

- Host kết nối mạng sử dụng Dynamic Host Configuration Protocol (DHCP) để tự động nhận địa chỉ IP 
- DHCP client xác định vị trí DHCP server bằng cách gửi UDP packet từ port 68 đến địa chỉ ```255.255.255.255``` ở port 67. Địa chỉ ```255.255.255.255``` là địa chỉ broadcast của 1 dải, tất cả các host trên local network nhìn UDP packet gửi đến địa chỉ này. Tuy nhiên, packet này sẽ không được forward đến mạng khác. Do đó DHCP server phải trên cùng local network như client, hoặc server sẽ không nhận được broadcast.
- OpenStack sử dụng chương trình bên thữ 3 là [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html) để làm DHCP server. ```DNSmasq``` ghi vào syslog nên ta có thể quan sát DHCP request và reply, ví dụ:

```sh
Apr 23 15:53:46 c100-1 dhcpd: DHCPDISCOVER from 08:00:27:b9:88:74 via eth2
Apr 23 15:53:46 c100-1 dhcpd: DHCPOFFER on 10.10.0.112 to 08:00:27:b9:88:74 via eth2
Apr 23 15:53:48 c100-1 dhcpd: DHCPREQUEST for 10.10.0.112 (10.10.0.131) from 08:00:27:b9:88:74 via eth2
Apr 23 15:53:48 c100-1 dhcpd: DHCPACK on 10.10.0.112 to 08:00:27:b9:88:74 via eth2
```

### 2.4. IP

- Internet Protocol (IP) xác định cách định tuyến giữa các host được kết nối local network khác nhau.
- Trong mô hình OSI, giao thức IP nằm ở layer 3
- 1 host gửi packet đến địa chỉ IP sẽ tham khảo routing table của nó để xác định máy tính nào trên local network sẽ nhận được packet này. Routing table duy trì danh sách các subnet liên kết với mỗi local network mà host được kết nối trực tiếp, cũng như 1 danh sách của định tuyến nằm trên các network.
- Trên Linux, 1 vài câu lệnh show routing table có thể kể đến là: ```ip route show```, ```route -r```, ```netstat -rn```
- Ví dụ:

```sh
$ ip route show
default via 10.0.2.2 dev eth0
10.0.2.0/24 dev eth0 protocol kernel scope link src 10.0.2.15
```

- Dòng 1 chỉ vị trí đầu ra của tuyến đường đi mặc định. Router liên kết với default route (10.0.2.2) được gọi là default gateway. DHCP server sẽ truyền địa chỉ của default gateway đến DHCP client cùng với địa chỉ IP client và netmask

- Dòng 2 chỉ rằng các IP trong dải 10.0.2.0/24 trên local network thông qua interface eth0

## 3. Overlay (tunnel) protocol

- Là công nghệ cho phép tạo ra các mạng ảo trên hệ thống mạng vật lý bên dưới (underlay network) mà vẫn tránh tác động với hạ tầng mạng bên dưới

- Trong OpenStack, ```neutron``` hỗ trợ 1 số công nghệ overlay network như GRE, VxLAN, NVGRE. Khi cấu hình overlay network cho mạng ảo, ```neutron``` tạo lên các tunnels point-to-point giữa mọi mạng và mọi compute nodes với nhau cũng như các controller nodes sử dụng các physical interface

### 3.1. Generic routing encapsulation (GRE)

Là giao thức để thiết lập các kết nối p2p, tạo ra 1 kết nối riêng, giống như VPN

### 3.2. Virtual extensible local area network (VxLAN)

Khả năng chính là mở rộng VLAN, là 1 công nghệ overlay được thiết kế để cung cấp các dịch vụ kết nối layer 2 và layer 3 thông qua mạng IP. Mạng IP cung cấp khả năng mở rộng, hiệu suất cân bằng và khả năng phục hồi khi có lỗi xảy ra.