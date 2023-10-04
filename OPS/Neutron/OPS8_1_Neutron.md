# Tổng quan về Neutron - OPS Networking

## I. Giới thiệu chung về Neutron

OPS Networking cho phép ta tạo và quản lý các network objects ví dụ như networks, subnets, và ports cho các service khác của OPS sử dụng. Với kiến trúc plugable, các plugin có thể được sử dụng để triển khai các thiết bị phần mềm khác nhau, nó khiến OPS có tính linh hoạt trong kiến trúc và triển khai

Dịch vụ Networking trong OPS (neutron) cũng cấp API cho phép bạn định nghĩa các kết nối mạng và gán địa chỉ ở trong môi trường cloud. Nó cũng cho phép các nhà khai thác vận hành các công nghệ networking khác nhau cho phù hợp với mô hình điện toán đám mây của riêng họ. Neutron cũng cung cấp một API cho việc cấu hình cũng như quản lý các dịch vụ networking khác nhau từ L3 forwarding, NAT cho tới LB, perimeter firewalls và VPN

Openstack là mô hình multitenancy. Tức là mỗi tenant có thể tạo nhiều private networking, router, firewall, LB,... Neutron có khả năng tách biệt các tài nguyên mạng giữa các tenant bằng giải pháp linux namespace. Mỗi network namespace riêng cho phép tạo các route, firewall rule, interface device riêng. Mỗi network hay router do tenant tạo ra đều hiện hữu dưới dạng 1 network namespace, từ đó các tenant có thể tạo các network trùng nhau (overlapping) nhưng vẫn độc lập (isolated) mà ko bị xung đột 

Các thành phần của Neutron có thể kể đến là:

### API server

Bao gồm các thành phần:
- Neutron API hỗ trợ Layer2 networking
- IPAM (quản lý địa chỉ IP)
- Extension để xây dựng router Layer 3 cho phép định tuyến giữa các networks layer 2 và các gateway để ra mạng bên ngoài

OPS networking cung cấp 1 danh sách các plugin cho phép tương tác với nhiều công nghệ mạng mã nguồn mở và cả thương mại, bao gồm các routers, switches, switch ảo và SDN (Software-Defined Networking) controller

### OPS Networking plugin and agents

Các plugin và các agent này cho phép gắn và gỡ các ports, tạo ra network hay subnet, và đánh địa chỉ IP. Lựa chọn plugin và agents nào là tùy thuộc vào nhà cung cấp và công nghệ sử dụng hệ thống cloud nhất định. Điều quan trọng là tại một thời điểm chỉ sử dụng được một plugin

Các Neutron plugin:
- Là giao diện kết nối giữa neutron và các công nghệ backend như SDN, Cisco, VMware, NSX. Nhờ đó, người dùng Neutron có thể tận dụng các tính năng nâng cao của các thiết bị mạng hoặc phần mềm mạng của bên thứ 3. Các plugin bao gồm: Open vSwitch, Cisco UCS/Nexus, Linux Bridge, Nicira Network Virtualization Platform, Ryu OpenFlo Controller, NEC OpenFlow
- Một trong các plugin không trực tiếp liên quan tới công nghệ bên thứ 3 nhưng là 1 plugin quan trọng đó là ML2 (Modular layer 2) plugin. Plugin này cho phép hoạt động đồng thời của nhiều công nghệ mạng hỗn hợp trong Neutron

**DHCP agent**: Cung cấp dịch vụ DHCP-server để cấp IP cho các máy ảo. Neutron-dhcp-agent cần truy cập vào message queue để giao tiếp với neutron server

**L2 agent**: (Ethernet và Switching): Linux Bridge, Open vSwitch

**L3 agent**: Cung cấp chuyển tiếp L3/NAT để cho phép các VMs có thể truy cập ra ngoài mạng

**Network provider service (SDN server/services)**: Cung cấp các service network bổ sung. Có thể tương tác với neutron-server, neutron-plugin, plugin-agents thông qua REST-APIs

### Messaging queue

Tiếp nhận và định tuyến các RPC requests giữa các agents để hoàn thành quá trình vận hành API. Các message queue được sử dụng trong ML2 plugin để thực hiện truyền thông RPC giữa neutron server và các neutron agents chạy trên mỗi hypervisor, cụ thể là các ML2 driver cho Open vSwitch và Linux Bridge

### Sơ đồ kiến trúc OPS Networking

![](./images/OPS8_1.jpg)

## II. Các khái niệm

Với Neutron, ta có thể tạo và cấu hình các network, subnet và thông báo tới Compute để gán các thiết bị ảo vào các ports của mạng vừa tạo. OpenStack Compute chính là "khách hàng" của neutron, chúng liên kết với nhau để cung cấp kết nối mạng cho các máy ảo. Cụ thể hơn, OPS Networking hỗ trợ cho phép các project có nhiều private networks và các projects có thể tự chọn danh sách IP cho riêng mình, kể cả những IP được sử dụng bởi một project khác.

Có 2 loại network:
- Provider
- Self-service networks

### 1. Provider networks

![](./images/OPS8_1.png)

![](./images/OPS8_2.png)

Provider networks cung cấp kết nối layer 2 cho các máy ảo với các tùy chọn hỗ trợ dịch vụ DHCP và metadata. Các kết nối này thường sử dụng VLAN (802.1q) để nhận diện và tách biệt nhau. Nhìn chung, Provider networks cũng cấp sự đơn giản, hiệu quả và sự minh bạch, linh hoạt trong chi phí. Mặc định chỉ có duy nhất người quản trị (admin) mới có thể tạo hoặc cập nhật provider networks bởi nó yêu cầu phải cấu hình thiết bị vật lý.

Bên cạnh đó, các provider network chỉ quản lý kết nối ở layer 2 cho máy ảo, vì thế nó thiếu đi một số tính năng như định tuyến và gán floating IP.

Các nhà khai thác đã quen thuộc với kiến trúc mạng ảo dựa trên nền tảng mạng vật lý cho layer2, layer3 và các dịch vụ khác có thể dễ dàng triển khai OPS Networking service

Vì các thành phần chịu trách nhiệm cho việc vận hành kết nối layer 3 sẽ ảnh hưởng tới hiệu năng và tính tin cậy nên provider networks chuyển các kết nối này xuống tầng vật lý. Tức là nếu kết nối mạng có vấn đề thì provider network cũng bị ảnh hưởng

### 2. Routed provider networks

Routed provider networks cung cấp kết nối ở layer 3 cho các máy ảo. Các network này map với những networks layer 3 đã tồn tại. Cụ thể hơn, các layer 2 segments của provider network sẽ được gán các router gateway giúp chúng có thể được định tuyến ra bên ngoài chứ thực chất Networking service không cung cấp khả năng định tuyến. Routed provider networks tất nhiên sẽ có hiệu suất thấp hơn so với provider networks

### 3. Self-service networks

![](./images/OPS8_3.png)

![](./images/OPS8_4.png)

Self-service networks được ưu tiên ở các projects thông thường để quản lý networks mà không cần quản trị viên (quản lý network trong project). Các networks này là ảo và nó yêu cầu các router ảo để giao tiếp với provider và external networks. Self-service networks cũng đồng thời cung cấp dịch vụ DHCP và metadata cho máy ảo.

Trong hầu hết các trường hợp, self-service networks sử dụng các giao thức như VxLAN hoặc GRE bởi chúng hỗ trợ nhiều hơn là VLAN tagging (802.1q). Bên cạnh đó, Vlans cũng thường yêu cầu phải cấu hình thêm ở tầng vật lý

Với IPv4, self-service networks thường sử dụng dải mạng riêng và tương tác với provider networks thông qua cơ chế NAT trên router ảo. Floating IP sẽ cho phép kết nối tới máy ảo thông qua địa chỉ NAT trên router ảo. Trong khi đó, IPv6 self-service networks thì lại sử dụng dải public và tương tác với provider networks bằng giao thức định tuyến tĩnh qua router ảo

Trái ngược lại với provider networks, self-service networks buộc phải đi qua layer 3 agent. Vì thế việc gặp sự cố ở 1 node có thể ảnh hưởng tới rất nhiều các máy ảo sử dụng chúng

Các user có thể tạo các project networks cho các kết nối bên trong project. Mặc định thì các kết nối này là riêng biệt và không được chia sẻ giữa các project. OPS Networking hỗ trợ các công nghệ dưới đây cho project network

#### Flat

Tất cả các instance nằm trong cùng một mạng, có thể chia sẻ với hosts. Không hề sử dụng VLAN tagging hay hình thức tách biệt về network khác

#### VLAN

Loại này cho phép các users tạo nhiều provider hoặc project network sử dụng VLAN IDs (chuẩn 802.1q tagged) tương ứng với VLANs trong mạng vật lý. Điều này cho phép các instance giao tiếp với nhau trong môi trường cloud. Chúng có thể giao tiếp với servers, firewalls, LB vật lý và các hạ tầng network khác trên cùng một VLAN layer2

#### GRE và VXLAN

VXLAN và GRE là các giao thức đóng gói tạo nên overlay networks để kích hoạt và kiểm soát việc truyền thông giữa các máy ảo (instances). Một router được yêu cầu để cho phép lưu lượng đi ra luồng bên ngoài tenant network GRE hoặc VXLAN. Router cũng có thể yêu cầu để kết nối một tenant network với mạng bên ngoài (VD Internet). Router cung cấp khả năng kết nối tới instances trực tiếp từ mạng bên ngoài sử dụng các địa chỉ floating IP

![](./images/OPS8_5.png)

#### Subnet 

Là một khối tập hợp các địa chỉ IP và đã được cấu hình. Quản lý các địa chỉ IP của subnet do IPAM driver thực hiện. Subnet được dùng để cấp phát các địa chỉ IP khi ports mới được tạo trên network

#### Subnet pools

Người dùng cuối thông thường có thể tạo các subnet với bất kỳ địa chỉ IP hợp lệ nào mà không bị hạn chế. Tuy nhiên, trong 1 vài trường hợp, sẽ là ổn hơn nếu như admin hoặc tenant định nghĩa trước 1 pool các địa chỉ để từ đó tạo ra các subnets được cấp phát tự động. Sử dụng subnet pools sẽ ràng buộc những địa chỉ nào có thể được sử dụng bằng cách định nghĩa rằng mỗi subnet phải nằm trong 1 pool được định nghĩa trước. Điều đó ngăn chặn việc tái sử dụng địa chỉ hoặc bị chồng lấn 2 subnets trong cùng 1 pool

#### Ports

Là điểm kết nối attach một thiết bị như card mạng của máy ảo tới mạng ảo. Port cũng được cấu hình các thông tin như địa chỉ MAC, địa chỉ IP để sử dụng port đó

#### Router

Cung cấp các dịch vụ layer 3 ví dụ như định tuyến, NAT giữa các self service và provider network hoặc giữa các self service với nhau trong cùng 1 project

#### Security group

Một security group được coi như là một firewall ảo cho các máy ảo để kiểm soát lưu lượng bên trong và bên ngoài router. Do đó, mỗi port trên một subnet có thể gán được với một tập hợp các security group riêng

Nếu không chỉ định group cụ thể nào khi vận hành, máy ảo sẽ được gán tự động với default security group của project. Mặc định, group này sẽ hủy tất cả các lưu lượng vào và cho phép lưu lượng ra ngoài. Các rule có thể được bổ sung để thay đổi các hành vi đó. Security group và các security có thể được bổ sung để thay đổi các hành vi đó. Security group và các security group rule cho phép người quản trị và các tenant chỉ định loại traffic và hướng (ingress/egress) được phép đi qua port. Một security group là một container của các security group rules.

Mặc định, mọi security groups chứa các rules thực hiện ở một số hành động sau:
- Cho phép traffic ra bên ngoài chỉ khi nó sử dụng MAC và IP của port máy ảo, cả 2 địa chỉ này được kết hợp tại ```allowed-address-pairs```
- Cho phép tín hiệu tìm kiếm DHCP và gửi message request sử dụng MAC của port cho máy ảo và địa chỉ IP chưa xác định
- Cho phép trả lời các tín hiệu DHCP và DHCPv6 từ DHCP server để các máy ảo có thể lấy IP
- Từ chối việc trả lời các tín hiệu DHCP request từ bên ngoài để tránh việc máy ảo trở thành DHCP server
- Cho phép các tín hiệu ```inbound/outbound``` ICMPv6 MLD, tìm kiếm neighbors, các máy ảo nhờ vậy có thể tìm kiếm và gia nhập các multicast group
- Từ chối các tín hiệu outbound ICMPv6 để ngăn việc máy ảo trở thành IPV6 router và forward các tín hiệu cho máy ảo khác
- Cho phép tín hiệu outbound non-IP từ địa chỉ MAC của các port trên máy ảo

Mặc dù cho phép non-IP traffic nhưng security groups không cho phép các ARP traffic. Có một số rules để lọc các tín hiệu ARP nhằm ngăn chặn việc sử dụng nó để chặn tín hiệu tới máy ảo khác. Ta không thể xóa hoặc vô hiệu hóa những rule này. Ta có thể hủy security groups bằng cách sửa giá trị dòng ```port_security_enabled``` thành ```False```

#### Extensions

OPS Networking service có khả năng mở rộng. Có 2 mục đích chính cho việc này: cho phép thực thi các tính năng mới trên API mà không cần phải đợi đến khi ra bản tiếp theo và cho phép các nhà phân phối bổ sung những chức năng phù hợp. OPS Networking service có khả năng mở rộng. Có 2 mục đích chính cho việc này: cho phép thực thi các tính năng mới trên API mà không cần phải đợi đến khi ra bản tiếp theo và cho phép các nhà phân phối bổ sung những chức năng phù hợp

#### DHCP

Dịch vụ tùy chọn DHCP quản lý địa chỉ IP trên provider và self-service networks. Networking service triển khai DHCP service sử dụng agent quản lý qdhcp namespaces và dnsmasq service

#### Metadata

Dịch vụ tùy chọn cung cấp API cho máy ảo để lấy metadata như SSH keys

#### Open vSwitch

Open vSwitch (OVS) là công nghệ switch ảo hỗ trợ SDN (Software-Defined Network) thay thế Linux bridge. OVS cung cấp chuyển mạch trong mạng ảo hỗ trợ các tiêu chuẩn Netflow, Openflow, sFlow, Open vSwitch cũng được tích hợp với các switch vật lý sử dụng các tính năng lớp 2 như STP, LACP, 802.1q VLAN tagging. OVS tunneling cũng được hỗ trợ để triển khai các mô hình overlay như VXLAN, GRE

#### L3 agent

L3 agent là một phần của package OPS neutron. Nó được xem như router layer 3 chuyển hướng lưu lượng và cung cấp dịch vụ gateway cho network lớp 2. Các nodes chạy L3 agent không được cấu hình IP trực tiếp trên một card mạng mà được kết nối với mạng ngoài. Thay vì thế, sẽ có một dải địa chỉ IP từ mạng ngoài được sử dụng cho OPS networking. Các địa chỉ này được gán cho các routers mà cung cấp liên kết giữa mạng trong và mạng ngoài. Miền địa chỉ được lựa chọn phải đủ lớn để cung cấp địa chỉ IP duy nhất cho mỗi router khi triển khai cũng như mỗi floating IP gán cho các máy ảo.
- **DHCP Agent**: OPS Networking DHCP agent chịu trách nhiệm cấp phát các địa chỉ IP cho các máy ảo chạy trên network. Nếu agent được kích hoạt và đang hoạt động khi một subnet được tạo, subnet đó mặc định sẽ được kích hoạt DHCP
- **Plugin Agent**: Nhiều networking plug-ins được sử dụng cho agent của chúng, bao gồm OVS và Linux bridge. Các plug-in chỉ định agent chạy trên các node đang quản lý lưu lượng mạng, bao gồm các compute node, cũng như các node chạy các agent

## III. Cấu trúc thành phần và dịch vụ

![](./images/OPS8_6.png)

### Server (```neutron-server``` là ```neutron-*-plugin```):

Dịch vụ này chạy trên các network node để phục vụ Networking API và các mở rộng của nó. Nó cũng tạo ra network model và đánh địa chỉ IP cho mỗi port. neutron-server và các plugin agent yêu cầu truy cập vào database để lưu trữ thông tin lâu dài và truy cập vào message queue (RabbitMQ) để giao tiếp nội bộ (giữa các tiến trình và với các tiến trình của các project khác)
- Cung cấp API, quản lý DB

### Plugin

- Quản lý agent

### Agent

- Cung cấp kết nối layer 2, layer 3 tới máy ảo
- Xử lý truyền thông giữa mạng ảo và mạng vật lý
- Xử lý metadata

**Layer 2 (Ethernet và Switching)**

- Linux Bridge
- OVS

**Layer 3 (IP và Routing)**

Cung cấp kết nối ra mạng ngoài (internet) cho các VM trên các tenant networks nhờ L3/NAT forwarding
- L3
- DHCP

**Misscellaneous**
- Metadata

### Services

Các dịch vụ routing:
- VPNaaS: VPN as a Service, extension của neutron cho VPN
- LBaaS: LB as a Service, API quy định và cấu hình nên các LB, được triển khai dựa trên HAProxy software load balancer
- FWaas: Firewall as a Service, API thử nghiệm cho phép các nhà cung cấp kiểm thử trên networking của họ

