# Neutron - Networking Service

## Preparation and deployment

Neutron được enable mặc định trong ```/etc/kolla/globals.yml```:

```sh
#enable_neutron: "{{ enable_openstack_core | bool }}"
```

## Network interfaces

Neutron external interface được sử dụng cho việc giao tiếp với thế giới bên ngoài, ví dụ provider networks, routers và floating IPs. Để cấu hình neutron external interface, chỉnh sửa ```/etc/kolla/globals.yml``` và đặt ```neutron_external_interface``` thành tên interface mong muốn. Interface này được sử dụng bởi hosts trong ```network``` group. Nó cũng được sử dụng bởi host trong ```compute``` group nếu ```enable_neutron_provider_networks``` được thiết lập hoặc DVR được enable

Interface này được gắn vào 1 bridge (Open vSwitch hoặc Linux Bridge, dựa vào driver) đã định nghĩa bởi ```neutron_bridge_name```, thứ mà mặc định là ```br-ex```. Mạng vật lý mặc định của Neutron là ```physnet1```

## Example: single interface

Trong trường hợp mà bạn chỉ có 1 external interface cho Neutron, lúc đó cấu hình rất đơn giản:

```sh
neutron_external_interface: "eth1"
```

## Example: multiple interfaces

Trong một vài trường hợp bạn sẽ cần nhiều external interfaces. Điều này có thể đạt được bằng cách chỉ định 1 danh sách:

```sh
neutron_external_interface: "eth1,eth2"
neutron_bridge_name: "br-ex1,br-ex2"
```

Cấu hình bên trên gắn ```eth1``` với bridge ```br-ex1```, và ```eth2``` gắn với bridge ```br-ex2```. Kolla Ansible ánh xạ những interfaces này với Neutron physical network ```physnet1``` và ```physnet2``` tương ứng

## Example: shared interface

Đôi khi 1 interface đã sử dụng cho Neutron external network có thể cũng được sử dụng cho traffic khác. Gắn 1 interface trực tiếp vào 1 bridge có thể ngăn chúng ta 