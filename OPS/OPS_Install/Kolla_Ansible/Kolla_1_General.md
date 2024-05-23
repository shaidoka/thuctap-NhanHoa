# Kolla Ansible - Quick start

## Khuyến nghị

Trước khi tìm hiểu về Kolla Ansible, hãy chắc chắn là bạn đã nắm được cơ bản về **Ansible** và **Docker**.

## Yêu cầu phần cứng

Máy chủ cài đặt cần đáp ứng yêu cầu tối thiểu sau về phần cứng:

- 2 network interfaces
- 8GB main memory
- 40GB disk space

Đường dẫn sau đây cập nhật về các bản phân phối được hỗ trợ bởi Kolla Ansible: [Support matrix](https://docs.openstack.org/kolla-ansible/latest/user/support-matrix)

## Cài đặt các phụ thuộc

Các câu lệnh ở phần dưới đây nên được chạy bởi quyền root

1. Update OS

```sh
apt update -y && apt upgrade -y
```

2. Cài đặt các phụ thuộc Python

Với CentOS, Rocky, AlmaLinux:

```sh
sudo dnf install git python3-devel libffi-devel gcc openssl-devel python3-libselinux -y
```

Với Debian và Ubuntu:

```sh
sudo apt install git python3-dev python-pip libffi-dev gcc libssl-dev -y
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible
```

## Cài đặt Kolla-Ansible

1. Cài đặt kolla-ansible và phụ thuộc của nó với pip:

```sh
pip install git+https://opendev.org/openstack/kolla-ansible@master
```

2. Tạo đường dẫn ```/etc/kolla```

```sh
mkdir -p /etc/kolla
chown $USER:$USER /etc/kolla
```

3. Copy ```globals.yml``` và ```passswords.yml``` vào ```/etc/kolla```:

```sh
cp -r /usr/local/share/kolla-ansible/etc_examples/kolla/* /etc/kolla
```

4. Copy ```all-in-one``` inventory file vào đường dẫn hiện tại

```sh
cp /usr/local/share/kolla-ansible/ansible/inventory/all-in-one .
```

## Cài đặt phụ thuộc của Ansible Galaxy 

```sh
kolla-ansible install-deps
```

*Nếu gặp lỗi ```CollectionDependencyProvider.find_matches() got an unexpected keyword argument 'identifier'``` thì chạy lệnh sau:*

```sh
sudo -H pip install -Iv 'resolvelib<0.6.0'
```

### Bước chuẩn bị

#### Inventory

Đầu tiên là phải chuẩn bị file inventory. 1 inventory là 1 Ansible file, nơi mà chúng ta chỉ định các hosts và các groups mà chúng thuộc về. Chúng ta có thể sử dụng file này để định nghĩa vai trò của các node, cũng như access credentials

Kolla Ansible đi cùng với ```all-in-one``` và ```multinode``` example inventory file. Trong bài này sẽ hướng dẫn cách cài đặt ```all-in-one```

#### Kolla passwords

Passwords được sử dụng trong triển khai của chúng ta được lưu trữ trong ```/etc/kolla/passwords.yml```. Tất cả passwords đều để trống trong file này và cần phải được điền đầy đủ trước khi cài đặt, hoặc chạy lệnh sau để tạo password random:

```sh
kolla-genpwd
```

#### Kolla globals.yml

```globals.yml``` là tệp cấu hình chính cho Kolla Ansible. Có một vài tùy chọn mà bạn sẽ cần để triển khai Kolla Ansible:

- **Image options**: Người dùng cần phải chỉ định images mà sẽ được sử dụng cho quá trình triển khai. Trong hướng dẫn này, chúng ta sẽ dùng images được cung cấp bởi Quay.io. Để tìm hiểu thêm về cách thức buld image, bạn có thể xem ở đây [Building Container Images](https://docs.openstack.org/kolla/latest/admin/image-building.html)

Kolla cung cấp một vài lựa chọn bản phân phối linux trong containers như sau:

- CentOS Stream (centos)
- Debian (debian)
- Rocky (rocky)
- Ubuntu (ubuntu)

Chúng tôi khuyên là nên sử dụng Rocky Linux 9 hoặc Ubuntu 22.04

```sh
kolla_base_distro: "rocky"
```

- **AArch64 options**: Kolla cung cấp images cho cả kiến trúc x84_64 và aarch64. Chúng không phải là "multiarch" nên người sử dụng aarch64 phải định nghĩa cấu hình ```openstack_tag_suffix```:

```sh
openstack_tag_suffix: "-aarch64"
```

Bằng cách này, image được xây dựng cho aarch64 sẽ được sử dụng

- **Networking**: Kolla Ansible yêu cầu 1 vài tùy chọn network cần phải được thiết lập. Chúng ta cần phải thiết lập interfaces sử dụng bởi OpenStack. Interface đầu tiên cần phải thiết lập là ```network_interface```. Đây là interface mặc định cho nhiều loại management network

```sh
network_interface: "eth0"
```

Interface thứ 2 cần thiết là 1 interface dedicated sử dụng cho Neutron external (public) network, có thể là vlan hoặc flat, phụ thuộc vào network được tạo ra như thế nào. Interface này nên được active nhưng không có IP address. Nếu không, interfaces sẽ không thể truy cập vào mạng bên ngoài

```sh
neutron_external_interface: "eth1"
```

Bạn có thể tìm hiểu thêm các cấu hình khác tại [Network overview](https://docs.openstack.org/kolla-ansible/latest/admin/production-architecture-guide.html#network-configuration)

Tiếp theo, chúng ta sẽ cung cấp floating IP cho các traffic management. IP này sẽ được quản lý bởi keepalived để cung cấp HA, và nên được thiết lập để sẽ không bị sử dụng trong management network mà chúng ta đã kết nối ở ```network_interface```. Nếu bạn sử dụng 1 triển khai Openstack đã có sẵn, hãy chắc chắn rằng IP này được allow trong cấu hình của VM

```sh
kolla_internal_vip_address: "10.1.0.250"
```

- **Enable addtional services**

Mặc định Kolla Ansible cung cấp bare compute kit, tùy nhiên nó cũng hỗ trợ rất nhiều tùy chọn về các dịch vụ thêm. Để làm điều này, hãy đơn giản là đặt ```enable_*``` thành ```yes```

Kolla giờ hỗ trợ rất nhiều OpenStack services, hãy kiểm tra danh sách các service hỗ trợ tại đây: [Service list](https://github.com/openstack/kolla-ansible/blob/master/README.rst#openstack-services)

Để hiểu thêm về cấu hình của từng dịch vụ, hãy xem tại đây: [Service Reference Guide](https://docs.openstack.org/kolla-ansible/latest/reference/index.html)

- **Multiple globals files**

Để quản lý tách biệt, enable bất kỳ option nào trong file ```globals.yml``` cũng có thể được thực hiện thông qua nhiều yml files. Đơn giản là tạo 1 folder gọi là ```globals.d``` bên dưới ```/etc/kolla``` và đặt vào đó tất cả các ```*.yaml``` files. Script của kolla-ansible sẽ tự động thêm tất cả các đối số này vào lệnh ```ansible-playbook```

Một ví dụ điển hình cho kiểu cấu hình này là người quản trị muốn enable cinder và các tùy chọn của nó ở 1 thời điểm khác, không phải là khi khởi tạo. Điều đó có thể đạt được bằng cách tách ```cinder.yml``` file, đặt chúng ở dưới ```/etc/kolla/globals.d/``` directory và thêm tất cả các tùy chọn liên quan vào

- **Virtual environment**

Chúng tôi khuyên nên sử dụng VE để thực thi các tác vụ trên remote hosts. Đọc thêm tại [Virtual Environments](https://docs.openstack.org/kolla-ansible/latest/user/virtual-environments.html)

## Triển khai

Sau khi cấu hình được thiết lập, chúng ta có thể tiếp tục bước triển khai. Đầu tiên, hãy cài đặt những phụ thuộc căn bản của host, như docker chẳng hạn

Kolla Ansible cung cấp 1 playbook mà sẽ install tất cả các service yêu cầu với phiên bản phù hợp

Các lệnh sau đây giả định bạn sử dụng ```all-in-one``` trong inventory. Nếu sử dụng 1 inventory với cấu hình khác, chẳng hạn như ```multinode```, hãy thay thế đối số ```-i```

1. Boostrap servers với kolla deploy dependencies

```sh
kolla-ansible -i ./all-in-one bootstrap-servers
```

2. Thực hiện pre-deployment check

```sh
kolla-ansible -i ./all-in-one prechecks
```

3. Cuối cùng, thực hiện deployment

```sh
kolla-ansible -i ./all-in-one deploy
```

Khi playbook hoàn thành, Openstack sẽ hoạt động, nếu có lỗi xảy ra, hãy tham khảo tại [trouble shooting guide](https://docs.openstack.org/kolla-ansible/latest/user/troubleshooting.html)

## Sử dụng OpenStack

1. Cài đặt OpenStack CLI client

```sh
pip install python-openstackclient -c https://releases.openstack.org/constraints/upper/master
```

2. OpenStack cần tệp ```clouds.yaml``` lưu trữ credentials cho admin user. Để khởi tạo file này, hãy sử dụng lệnh:

```sh
kolla-ansible post-deploy
```

Lệnh này sẽ khởi tạo file ở ```/etc/kolla/clouds.yaml```, bạn có thể sử dụng nó bằng cách copy vào ```/etc/openstack``` hoặc ```~/.config/openstack``` hoặc bằng cách thiết lập biến môi trường ```OS_CLIENT_CONFIG_FILE```

3. Tùy thuộc vào bạn cài đặt Kolla Ansible, có 1 script mà sẽ tạo network, images, và 1 vài thứ nữa, bạn có thể sử dụng nó với mục đích demo

```sh
kolla-ansible/init-runonce
```