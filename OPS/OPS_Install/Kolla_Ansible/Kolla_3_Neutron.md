# Neutron - Networking Service

## Preparation and deployment

Neutron được enable mặc định trong ```/etc/kolla/globals.yml```:

```sh
#enable_neutron: "{{ enable_openstack_core | bool }}"
```

## Network interfaces

Neutron external interface được sử dụng cho việc giao tiếp với thế giới bên ngoài, ví dụ provider networks, routers và floating IPs. Để cấu hình neutron external interface, chỉnh sửa ```/etc/kolla/globals.yml``` và đặt ```neutron_external_interface``` thành tên interface mong muốn. Interface này được sử dụng bởi hosts trong ```network``` group. Nó cũng được sử dụng bởi host trong ```compute``` group nếu ```enable_neutron_provider_networks``` được thiết lập hoặc DVR được enable

Interface này được gắn vào 1 bridge (Open vSwitch hoặc Linux Bridge, dựa vào driver) đã định nghĩa bởi ```neutron_bridge_name```, thứ mà mặc định là ```br-ex```. Mạng vật lý mặc định của Neutron là ```physnet1```

### Example: single interface

Trong trường hợp mà bạn chỉ có 1 external interface cho Neutron, lúc đó cấu hình rất đơn giản:

```sh
neutron_external_interface: "eth1"
```

### Example: multiple interfaces

Trong một vài trường hợp bạn sẽ cần nhiều external interfaces. Điều này có thể đạt được bằng cách chỉ định 1 danh sách:

```sh
neutron_external_interface: "eth1,eth2"
neutron_bridge_name: "br-ex1,br-ex2"
```

Cấu hình bên trên gắn ```eth1``` với bridge ```br-ex1```, và ```eth2``` gắn với bridge ```br-ex2```. Kolla Ansible ánh xạ những interfaces này với Neutron physical network ```physnet1``` và ```physnet2``` tương ứng

### Example: shared interface

Đôi khi 1 interface đã sử dụng cho Neutron external network có thể cũng được sử dụng cho traffic khác. Gắn 1 interface trực tiếp vào 1 bridge có thể giúng chúng ta khỏi phải cấp 1 IP cho interface đó. 1 giải pháp cho vấn đề này là sử dụng 1 Linux bridge trung gian và 1 cặp Ethernet ảo, sau đó cấp các địa chỉ IP trên Linux bridge. Cách cấu hình này được hỗ trợ bởi [Kayobe](https://docs.openstack.org/kayobe/latest//). 

## Provider networks

Provider network cho phép kết nối compute instances trực tiếp đến mạng vật lý mà không phải qua tunnels. Điều này cần thiết trong trường hợp ứng dụng cần yêu cầu về hiệu suất cao. Chỉ adminsitrator của Openstack có thể tạo những network dạng này.

Để sử dụng provider networks trong instances, bạn cần chỉnh sửa tham số sau trong file ```globals.yml```:

```sh
enable_neutron_provider_networks: yes
```

Với provider networks, compute hosts phải có 1 external bridge được tạo và cấu hình bởi Ansible (thực ra thì điều này cũng tương tự nếu sử dụng mode Neutron Distributed Virtual Routing - DVR). Trong trường hợp này, đảm bảo là ```neutron_external_interface``` được cấu hình chính xác cho mọi host trong ```compute``` group

## Internal DNS resolution

Networking service cho phép người dùng quản lý tên gọi được cấp cho các ports sử dụng 2 thuộc tính đi liền với ports, networks, và floating IPs. Bảng sau thể hiện các thuộc tính khả dụng với mỗi loại tài nguyên:

|Resource|dns_name|dns_domain|
|:-|:-|:-|
|Ports|Yes|Yes|
|Networks|No|Yes|
|Floating IPs|Yes|Yes|

Để kích hoạt tính năng này ta cần đặt các tham số sau trong ```globals.yml```:

```sh
neutron_dns_integration: "yes"
neutron_dns_domain: "example.org."
```

## OpenvSwitch (ml2/ovs)

Mặc định ```kolla-ansible``` sử dụng ```openvswitch``` làm phương thức underlying network, ta có thể thay thế nó bằng cách sử dụng ```neutron_plugin_agent``` trong file ```globals.yml```

```sh
neutron_plugin_agent: "openvswitch"
```

Khi sử dụng Open vSwitch trên 1 kernel tương thích (4.3+), bạn có thể chuyển sang sử dụng native OVS firewall driver bằng cách bằng cách ghi đè cấu hình. Thiết lập cấu hình sau trong file ```/etc/kolla/config/neutron/openvswitch_agent.ini```:

```sh
[securitygroup]
firewall_driver = openvswitch
```

## L3 agent high availability

L3 và DHCP agents có thể được tạo với HA bằng cách thiết lập:

```sh
enable_neutron_agent_ha: "yes"
```

Điều này cho phép networking có thể failover giữa các controllers nếu có agent nào bị stop. Nếu tùy chọn này được enable, sẽ có ích nếu cùng lúc thiết lập:

```sh
neutron_l3_agent_failover_delay:
```

Agents đôi khi sẽ cần restart. Cấu hình độ trễ trên sẽ được gọi giữa các hiệu lệnh restart của mỗi agent. Khi được cấu hình chính xác, nó sẽ ngăn network outages nếu tất cả agents cùng restart vào 1 thời điểm. Thời gian chính xác mà agent cần để restart tùy thuộc vào cấu hình phần cứng và số router hiện có trong OPS. Có 1 quy tắc nên nhớ là thiết lập giá trị bằng ```40 + 3n```, trong đó ```n``` là số router. VD như bạn có 5 routers thì con số nên thiết lập là ```40 + 5*3``` tức là ```55```. Giá trị mặc định là ```0```. 1 giá trị khởi động non-zero sẽ chỉ làm cho network bị outages nếu thời gian failover lớn hơn thời gian delay, thứ mà sẽ khó để tìm nguyên nhân hơn hành vi bình thường.

## OVN (ml2/ovn)

Để sử dụng ```ovn``` mechanism driver cho ```neutron```, ta cần thiết lập tham số sau:

```sh
neutron_plugin_agent: "ovn"
```

Khi sử dụng OVN - Kolla Ansible sẽ không enable tính năng distributed floating IP (không enable external bridges trên các computes) theo mặc định. Để thay đổi điều này, hãy thiết lập:

```sh
neutron_ovn_distributed_fip: "yes"
```

Tương tự, để có Neutron DHCP agents deploy trong môi trường OVN networking, sử dụng:

```sh
neutron_ovn_dhcp_agent: "yes"
```

Điều này có thể hữu ích trong trường hợp sử dụng Ironic baremetal nodes làm compute service. Hiện tại OVN không hỗ trợ trả lời truy vấn DHCP trên port type external, đây là lúc cần đến sự trợ giúp của Neutron agent.

Để triển khai Neutron OVN Agent ta cần thiết lập

```sh
neutron_enable_ovn_agent: "yes"
```

Hiện tại agent chỉ cần thiết để tăng QoS bằng cách giảm tải cho phần cứng.

## Mellanox Infiniband (ml2/mlnx)

Để thêm ```mlnx_infiniband``` vào danh sách machanism driver cho ```neutron``` để hỗ trợ Infiniband virtual funtions, ta cần thiết lập tham số sau: (ở đây giả sử neutron SR-IOV agent cũng được enable sử dụng cờ ```enable_neutron_sriov```)

```sh
enable_neutron_mlnx: "yes"
```

Thêm vào đó, ta cũng cần cung cấp ánh xạ physnet:interface thông qua ```neutron_mlnx_physnet_mappings```, thích mà đại diện cho ```neutron_mlnx_agent``` container thông qua ```mlnx_agent.ini``` và ```neutron_eswitchd``` container thông qua ```eswitchd.conf```

```sh
neutron_mlnx_physnetmappings:
  ibphysnet: "ib0"
```

## SSH authentication in external systems (switches)

Kolla, mặc định sẽ khởi tạo và copies 1 ssh key vào ```neutron_server``` container (đặt tại ```/var/lib/neutron/.ssh/id_rsa```), thứ mà sẽ được dùng để xác thực với external systems (VD trong ```networking-generic-switch``` hoặc ```networking-ansible``` managed switches).

Ta có thể thiết lập biến ```neutron_ssh_key``` trong ```passwords.yml``` để quản lý key đã sử dụng

## Custom Kernel Module Configuration for Neutron

Neutron có thể yêu cầu modules kernel cụ thể cho các từng tính năng. Trong khi có nhiều predefined default modules trong Ansible role, người dùng vẫn có khả năng linh hoạt trong việc thêm các modules custom nếu cần thiết.

Để thêm các custom kernel modules cho Neutron, chỉnh sửa cấu hình trong ```/etc/kolla/globals.yml```

```sh
neutron_modules_extra:
  - name: 'nf_conntrack_tftp'
    params: 'hashsize=4096'
```

Trong VD trên, ```neutron_modules_extra``` cho phép người dùng chỉ định các modules thêm và các tham số liên quan đến nó. Cấu hình bên trên thay đổi tham số ```hashsize``` cho module ```nf_conntrack_tftp```

