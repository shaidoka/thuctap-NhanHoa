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

Để hỗ trợ DHCP relay, ta có thể định nghĩa netmask trong range. Trong trường hợp đó, hãy cung cấp 1 router để cho phép traffic có thể đi được tới Ironic server

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

## Revert to plain PXE (not recommended)

Bất đầu từ Yoga, Ironic đã chuyển PXE mặc định từ plain PXE sang iPXE. Kolla Ansible do đó cũng quyết định chonjn iPXE làm mặc định cho Ironic Inspector nhưng cho phép người dùng có thể quay trở về bản PXE mặc định trước đó là plain PXE. Hãy cấu hình ```globals.yml``` với tham số sau:

```sh
ironic_dnsmasq_serve_ipxe: "no"
```

Để revert Ironic về phiên bản default trước đó, hãy thiết lập ```pxe``` thành ```default_boot_interface``` trong ```/etc/kolla/config/ironic.conf```:

```sh
[DEFAULT]
default_boot_interface = pxe
```

## Attach ironic to external keystone (optional)

Trong 1 triển khai có nhiều region, keystone có thể được cài đặt ở trong 1 region (gọi là region 1 đi) và ironic trong 1 region khác (gọi là region 2). Trong trường hợp này, chúng ta khoogn muốn cài đặt keystone cùng với ironic trong region 2, nhưng phải cấu hình để ironic có thể kết nối đến keystone ở region 1. Để triển khai ironic theo hướng như vậy, hãy đặt tham số ```enable_keystone``` thành ```no```

```sh
enable_keystone: "no"
```

Nó sẽ ngăn keystone cài đặt ở region 2.

Để thêm keystone-related sections trong ironic.conf, ta cũng cần đặt biến ```ironic_enable_keystone_integration``` thành ```yes```:

```sh
ironic_enable_keystone_integration: "yes"
```

## Deployment

Như thường lệ:

```sh
kolla-ansible deploy
```

## Post-deployment configuration

[Ironic Documentation](https://docs.openstack.org/ironic/latest/install/configure-glance-images) đã mô tả cách thức để tạo kernel và ramdisk và đăng ký chúng vào Glance. Trong ví dụ này chúng ta đang sử dụng các images tương tự nhau mà được tải về từ Inspector:

```sh
openstack image create --disk-format aki --container-format aki --public \
  --file /etc/kolla/config/ironic/ironic-agent.kernel deploy-vmlinuz

openstack image create --disk-format ari --container-format ari --public \
  --file /etc/kolla/config/ironic/ironic-agent.initramfs deploy-initrd
```

[Ironic Documentation](https://docs.openstack.org/ironic/latest/install/configure-nova-flavors) cũng đã mô tả cách tạo Nova flavors cho bare metal. Ví dụ:

```sh
openstack flavor create my-baremetal-flavor \
  --ram 512 --disk 1 --vcpus 1 \
  --property resources:CUSTOM_BAREMETAL_RESOURCE_CLASS=1 \
  --property resources:VCPU=0 \
  --property resources:MEMORY_MB=0 \
  --property resources:DISK_GB=0
```

Phần [này](https://docs.openstack.org/ironic/latest/install/enrollment) của tài liệu Ironic thì mô tả cách để enroll baremetal nodes và ports. Trong ví dụ dưới đây, hãy chắc chắn là thay thế chính xác giá trị cho kernel, ramdisk, và địa chỉ MAC của baremetal node của bạn.

```sh
openstack baremetal node create --driver ipmi --name baremetal-node \
  --driver-info ipmi_port=6230 --driver-info ipmi_username=admin \
  --driver-info ipmi_password=password \
  --driver-info ipmi_address=192.168.5.1 \
  --resource-class baremetal-resource-class --property cpus=1 \
  --property memory_mb=512 --property local_gb=1 \
  --property cpu_arch=x86_64 \
  --driver-info deploy_kernel=15f3c95f-d778-43ad-8e3e-9357be09ca3d \
  --driver-info deploy_ramdisk=9b1e1ced-d84d-440a-b681-39c216f24121

openstack baremetal port create 52:54:00:ff:15:55 \
  --node 57aa574a-5fea-4468-afcf-e2551d464412 \
  --physical-network physnet1
```

Khiến baremetal node khả dụng trong nova:

```sh
openstack baremetal node manage 57aa574a-5fea-4468-afcf-e2551d464412
openstack baremetal node provide 57aa574a-5fea-4468-afcf-e2551d464412
```

Sẽ tốn một chút thời gian cho node để có thể hoàn toàn sẵn sàng. Sử dụng lệnh sau đây để kiểm tra:

```sh
openstack hypervisor stats show
openstack hypervisor show 57aa574a-5fea-4468-afcf-e2551d464412
```

## Booting the baremetal

Lệnh sau đây cho thấy 1 ví dụ về cách tạo resource sử dụng baremetal server:

```sh
openstack server create --image cirros --flavor my-baremetal-flavor \
  --key-name mykey --network public1 demo1
```