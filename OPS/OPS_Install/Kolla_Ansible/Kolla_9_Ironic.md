# Ironic - Bare Metal provisioning

## Overview

Ironic là OpenStack service xử lý baremetal server, ví dụ như máy chủ vật lý. Nó có thể hoạt động độc lập cũng như cùng với các OpenStack service khác (chẳng hạn như Neutron hay Nova)

## Pre-deployment Configuration

Kích hoạt Ironic trong ```/etc/kolla/globals.yml```:

```sh
enable_ironic: "yes"
```

Trong cùng file, định nghĩa 1 network interface làm NIC mặc định cho dnsmasq và định nghĩa 1 network để sử dụng cho Ironic cleaning network:

```sh
ironic_dnsmasq_interface: "eth1"
ironic_cleaning_network: "public1"
```

Cuối cùng, định nghĩa ít nhất 1 DHCP range cho Ironic inspector:

```sh
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.5.100,192.168.5.110"
```

Một ví dụ khác của 1 range với 1 router (nếu có nhiều router thì có thể chỉ định cách nhau bởi dấu phẩy):

```sh
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.5.100,192.168.5.110"
    routers: "192.168.5.1"
```

Để hỗ trợ DHCP relay, ta có thể định nghĩa netmask trong rage. Trong trường hợp đó, hãy cung cấp 1 router để cho phép traffic có thể đi được tới Ironic server

```sh
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.5.100,192.168.5.110,255.255.255.0"
    routers: "192.168.5.1"
```

Nhiều ranges là hoàn toàn có thể, chúng có thể được kết nối trực tiếp với interfaces hoặc replay (nếu có netmask):

```sh
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.5.100,192.168.5.110"
  - range: "192.168.6.100,192.168.6.110,255.255.255.0"
    routers: "192.168.6.1"
```

Lease time mặc định cho mỗi range có thể được cấu hình global thông qua ```ironic_dnsmasq_dhcp_default_lease_time``` variable hoặc theo từng range thông qua ```lease_time``` parameter

Trong cùng file đó, chỉ định PXE bootloader file cho Ironic Inspector. File liên quan đến đường dẫn ```/var/lib/ironic/tftpboot```. Mặc định là ```pxelinux.0```. Đó là với kiến trúc x86, với aarch64 trên Debian sẽ cần ```debian-installer/arm64/bootnetaa64.efi```

```sh
ironic_dnsmasq_boot_file: pxelinux.0
```

Ironic inspector cũng cần 1 kernel và ramdisk được đặt trong ```/etc/kolla/config/ironic/```. Trong ví dụ sau sử dụng coreos (thường được dùng trong các triển khai Ironic), mặc dù vậy, bất kỳ kernel/ramdisk tương thích nào cũng có thể được dùng:

```sh
curl https://tarballs.opendev.org/openstack/ironic-python-agent/dib/files/ipa-centos9-master.kernel -o /etc/kolla/config/ironic/ironic-agent.kernel
curl https://tarballs.opendev.org/openstack/ironic-python-agent/dib/files/ipa-centos9-master.initramfs -o /etc/kolla/config/ironic/ironic-agent.initramfs
```

Để đưa vào các tham số thêm cho kernel, hãy sử dụng:

```sh
ironic_inspector_kernel_cmdline_extras: ['ipa-lldp-timeout=90.0', 'ipa-collect-lldp=1']
```

## Configure conductor's HTTP server port (optional)

Port được sử dụng cho conductor's HTTP server được quản lý thông qua ```ironic_http_port``` trong ```globals.yml```

```sh
ironic_http_port: "8089"
```

