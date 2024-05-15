# Libvirt - Nova Virtualization Driver

## Overview

Libvirt thường được sử dụng làm driver ảo hóa nhất trong Openstack. Nó sử dụng Libvirt, hỗ trợ bởi QEMU hoặc KVM. Libvirt chạy trong container tên ```nova_libvirt``` hoặc chạy dưới dạng 1 daemon trên host.

## Hard Virtualization

2 giá trị được hỗ trợ bởi ```nova_compute_virt_type``` là ```qemu``` và ```kvm```, trong đó ```kvm``` là mặc định.

Để tối ưu hóa hiệu suất, ```kvm``` được ưu tiên, vì nhiều vấn đề của ảo hóa có thể được giảm tải xuống phần cứng. Nếu không thể bật ảo hóa phần cứng (VT) trong BIOS setting, hãy sử dụng ```qemu``` để cung cấp ảo hóa phần mềm với hiệu năng thấp hơn.

## SASL Authentication

Cấu hình mặc định của Kolla Ansible là chạy libvirt thông qua TCP, xác thực với SASL. Điều này không nên nghĩ là cung cấp 1 kênh mã hóa an toàn, bảo mật, vì phương thức username/password SASL cho TCP đã không còn được coi là an toàn. Tuy nhiên, nó vẫn ít nhất là cung cấp 1 phương pháp để xác thực với libvirt API. Để biết cách cấu hình kênh mã hóa bảo mật hơn, hãy sử dụng ```libvirt TLS```

SASL được enable theo cờ ```libvirt_enable_ssl```, thứ mà mặc định là ```true```.

Username được cấu hình thông qua ```libvirt_sasl_authname```, và mặc định là ```nova```. Password được cấu hình thông qua ```libvirt_sasl_password```, và được khởi tạo cùng với các password khác sử dụng ```kolla-genpwd``` và lưu trữ tại ```passwords.yml```

Danh sách các phương thức xác thực được enable được cấu hình thông qua ```libvirt_sasl_mech_list```, mặc định là ```["SCRAM-SHA-256"]``` nếu libvirt TLS được bật, hoặc ```["DIGEST-MD5"]``` trong trường hợp ngược lại.

## Host vs containerised libvirt

Mặc định, Kolla Ansible triển khai libvirt trong ```nova_libvirt``` container. Trong 1 vài trường hợp thì chạy libvirt như 1 daemon trên compute hosts sẽ hữu dụng hơn.

Kolla Ansible hiện tại không hỗ trợ triển khai và cấu hình libvirt như 1 host daemon. Tùy vậy, từ khi Yoga phát hành, nếu 1 libvirt daemon đã được thiết lập thì Kolla Ansible sẽ có thể cấu hình để sử dụng nó. Điều này có thể đạt được thông qua thiết lập ```enable_nova_lbvirt_container: false```

Khi firewall driver được đặt là ```openvswitch```, libvirt sẽ cắm VMs trực tiếp vào integration bridge ```br-int```. Để làm điều này nó sử dụng công cụ ```ovs-vsctl```. Search path cho binary này được quản lý bởi biến môi trường ```$PATH``` (như đã nhìn thấy bằng libvirt process). Có 1 vài tùy chọn để đảm bảo rằng binary này có thể được tìm thấy:

- Đặt ```openvswitch_ovs_vsctl_wrapper_enabled``` thành ```True```. Điều này sẽ cài đặt 1 wrapper script lên đường dẫn ```/usr/bin/ovs-vsctl``` mà sẽ thực thi ```ovs-vsctl``` trong container ```openvswitch_vswitchd```. Tùy chọn này hữu dụng nếu ta không có openvswitch nào được cài đặt trên host. Nó cũng có lợi thế khi mà ```ovs-vsctl``` sẽ khớp với phiên bản của server
- Cài đặt openvswitch trên hypervisor. Kolla mount ```/run/openvswitch``` từ host vào trong container ```openvswitch_vswitchd```. Điều này có nghĩa là socket sẽ ở vị trí mà ```ovs-vsctl``` mong đợi với các tùy chọn mặc định của nó

### Migration from container to host

Lệnh ```kolla-ansible nova-libvirt-cleanup``` sẽ giúp clean up container ```nova_libvirt``` và các items liên quan trên hosts khi nó bị disabled. Lệnh này nên đượcc chạy sau khi compute service bị tắt, và tất cả VMs active đã chuyển sang host khác.

Mặc định, lệnh này sẽ fail nếu có bất kỳ VM đang chạy trên host. Nếu bạn chắc chắn rằng có thể an toàn clean up container ```nova_libvirt``` với các VM đang chạy, thiết lập ```nova_libvirt_cleanup_running_vms_fatal``` thành ```false``` sẽ cho phép lệnh chạy.

Container ```nova_libvirt``` có vài Docker volumes kèm theo là: ```libvirtd```, ```nova_libvirt_qemu``` và ```nova_libvirt_secrets```. Mặc định, những volumes này sẽ không được clean up. Nếu bạn chắc chắn dữ liệu trong chúng có thể xóa đi 1 cách an toàn, hãy đặt ```nova_libvirt_cleanup_remove_volumes``` thành ```true```, điều này làm những Docker volumes trên được remove.

## Libvirt TLS

Cấu hình mặc định của Kolla Ansible là chạy libvirt thông qua TCP, với SASL authentication. 