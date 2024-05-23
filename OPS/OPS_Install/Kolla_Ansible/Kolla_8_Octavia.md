# Octavia

Octavia cung cấp dịch vụ cân bằng tải trong Cloud. Bài này hướng dẫn về 2 providers: Amphora và OVN

## Enabling Octavia

Kích hoạt dịch vụ octavia trong ```globals.yml```:

```sh
enable_octavia: "yes"
```

## Amphora provider

### Option 1: Automatically generating Certificates

Kolla Ansible cung cấp giá trị mặc định cho trường certificate issuer và owner. Bạn có thể customize chúng trong ```globals.yml```, VD:

```sh
octavia_certs_country: US
octavia_certs_state: Oregon
octavia_certs_organization: OpenStack
octavia_certs_organization_unit: Octavia
```

Generate octavia certificate:

```sh
kolla-ansible octavia-certificates
```

Certificates và keys sẽ được sinh ra tại ```/etc/kolla/config/octavia```

### Option 2: Manually generating certificate

Thực hiện các bước sau:

```sh
mkdir ~/work
cd ~/work
git clone https://opendev.org/openstack/octavia.git
cd octavia/bin
./create_dual_intermediate_CA.sh
cp -p ./dual_ca/etc/octavia/certs/server_ca.cert.pem /etc/kolla/config/octavia/server_ca.cert.pem
cp -p ./dual_ca/etc/octavia/certs/server_ca.key.pem /etc/kolla/config/octavia/server_ca.key.pem
cp -p ./dual_ca/etc/octavia/certs/client_ca.cert.pem /etc/kolla/config/octavia/client_ca.cert.pem
cp -p ./dual_ca/etc/octavia/certs/client.cert-and-key.pem /etc/kolla/config/octavia/client.cert-and-key.pem
```

Tùy chọn sau nên được bật trong ```passwords.yml```, khai báo password đã sử dụng để mã hóa CA key:

```sh
octavia_ca_password: <CA key password>
```

### Monitoring certificate expiry

Bạn có thể sử dụng lệnh sau để kiểm tra thời hạn của certificate:

```sh
kolla-ansible octavia-certificates --check-expiry <days>
```

### Networking

Octavia worker và health manager nodes phải truy nhập được vào Octavia management network để giao tiếp được với Amphorae

Nếu sử dụng 1 VLAN cho Octavia management network, bật tùy chọn Neutron provider networks:

```sh
enable_neutron_provider_networks: yes
```

Cấu hình tên của network interface trên các controller được sử dụng để truy cập Octavia management network. Nếu sử dụng VLAN provider network, hãy chắc chắn traffic cũng được bridge đến Open vSwitch trên các controller:

```sh
octavia_network_interface: <network interface on controllers>
```

Interface này nên có 1 IP address cùng dải với Octavia management subnet

### Registering OpenStack resources

Từ bản Victoria, có 2 cách để cấu hình Octavia:

1. Kolla Ansible tự động đăng ký các tài nguyên cho Octavia trong khi triển khai
2. Người vận hành đăng ký tài nguyên cho Octavia sau khi nó được triển khai

Lựa chọn đầu tiên đơn giản hơn, và nó được khuyến khích cho người mới. Trong khi lựa chọn thứ 2 cung cấp sự linh hoạt tốt hơn, nhưng đổi lại là sự phức tạp cho người vận hành.

#### Option 1: Automatic resource registration (default, recommend)

Với tự động đăng ký tài nguyên, Kolla Ansible sẽ đăng ký các tài nguyên sau đây:

- Nova flavor
- Nova SSH keypair
- Neutron network and subnet
- Neutron security groups

Cấu hình cho những tài nguyên này có thể được customize trước khi triển khai

Lưu ý rằng để hoạt động được, Nova và Neutron APIs cần phải có thể truy cập. Lệnh ```kolla-ansible genconfig``` và khi sử dụng Ansible check mode cũng cần chúng.

**Customize Amphora flavor**

Amphora flavor mặc định có tên ```amphora``` với 1 vCPU, 1 GB ram và 5 GB disk, ta có thể customize nó bằng cách thay đổi ```octavia_amp_flavor``` trong ```globals.yml```

Hãy xem ```os_nova_flavor``` Ansible module để biết thông tin chi tiết, các tham số được hỗ trợ bao gồm:

- ```disk```
- ```ephemeral``` (optional)
- ```extra_specs``` (optional)
- ```flavorid``` (optional)
- ```is_public``` (optional)
- ```name```
- ```ram```
- ```swap``` (optional)
- ```vcpus```

Mặc định sẽ là:

```sh
octavia_amp_flavor:
  name: "amphora"
  is_public: no
  vcpus: 1
  ram: 1024
  disk: 5
```

**Customise network and subnet**

Cấu hình Octavia management network và subnet với ```octavia_amp_network``` trong ```globals.yml```. Network này phải là 1 network có thể truy cập được từ các controllers. Thường là VLAN provider.

Các tham số được hỗ trợ với ```os_network```:

- ```external``` (optional)
- ```mtu``` (optional)
- ```name```
- ```provider_network_type``` (optional)
- ```provider_physical_network``` (optional)
- ```provider_segmentation_id``` (optional)
- ```shared``` (optional)
- ```subnet```

Các tham số được hỗ trợ với ```os_subnet```:

- ```allocation_pool_start``` (optional)
- ```allocation_pool_end``` (optional)
- ```cidr```
- ```enable_dhcp``` (optional)
- ```name```
- ```gateway_ip``` (optional)
- ```no_gateway_ip``` (optional)
- ```ip_version``` (optional)
- ```ipv6_address_mode``` (optional)
- ```ipv6_ra_mode``` (optional)

VD:

```sh
octavia_amp_network:
  name: lb-mgmt-net
  provider_network_type: vlan
  provider_segmentation_id: 1000
  provider_physical_network: physnet1
  external: false
  shared: false
  subnet:
    name: lb-mgmt-subnet
    cidr: "10.1.2.0/24"
    allocation_pool_start: "10.1.2.100"
    allocation_pool_end: "10.1.2.200"
    gateway_ip: "10.1.2.1"
    enable_dhcp: yes
```

Cuối cùng, triển khai Octavia với Kolla Ansible:

```sh
kolla-ansible -i <inventory> deploy --tags common,horizon,octavia
```

#### Option 2: Manual resource registration

Trong trường hợp này, Kolla Ansible sẽ không đăng ký tài nguyên với Octavia. Đặt ```octavia_auto_configure``` thành no trong ```globals.yml```

```sh
octavia_auto_configure: no
```

Tất cả resources nên được register trong ```service``` project. Điều này có thể được thực hiện bằng lệnh:

```sh
. /etc/kolla/octavia-openrc.sh
```

**Lưu ý:** Hãy đảm bảo là bạn đã thực hiện ```kolla-ansible post-deploy``` sau khi deploy với ```enable_octavia``` là ```yes``` trong ```globals.yml```

**Amphora flavor**

Register flarvor trong Nova

```sh
openstack flavor create --vcpus 1 --ram 1024 --disk 2 "amphora" --private
```

**Keypair**

Register keypair trong Nova

```sh
openstack keypair create --public-key <path to octavia public key> octavia_ssh_key
```

**Network and subnet**

Register management network và subnet trong Neutron. Điều này phải là 1 network có thể truy cập được từ controller. Thường là 1 VLAN provider network.

```sh
OCTAVIA_MGMT_SUBNET=192.168.43.0/24
OCTAVIA_MGMT_SUBNET_START=192.168.43.10
OCTAVIA_MGMT_SUBNET_END=192.168.43.254

openstack network create lb-mgmt-net --provider-network-type vlan --provider-segment 107  --provider-physical-network physnet1
openstack subnet create --subnet-range $OCTAVIA_MGMT_SUBNET --allocation-pool \
  start=$OCTAVIA_MGMT_SUBNET_START,end=$OCTAVIA_MGMT_SUBNET_END \
  --network lb-mgmt-net lb-mgmt-subnet
```

**Security group**

Register security group trong Neutron

```sh
openstack security group create lb-mgmt-sec-grp
openstack security group rule create --protocol icmp lb-mgmt-sec-grp
openstack security group rule create --protocol tcp --dst-port 22 lb-mgmt-sec-grp
openstack security group rule create --protocol tcp --dst-port 9443 lb-mgmt-sec-grp
```

**Kolla Ansible configuration**

Các tùy chọn sau nên được thêm vào ```globals.yml``` (thiết lập ID theo tài nguyên mà bạn đã tạo trước đó)

```sh
octavia_amp_boot_network_list: <ID of lb-mgmt-net>
octavia_amp_secgroup_list: <ID of lb-mgmt-sec-grp>
octavia_amp_flavor_id: <ID of amphora flavor>
```

Giờ thì deploy Octavia:

```sh
kolla-ansible -i <inventory> deploy --tags common,horizon,octavia
```

### Amphora image

Để sử dụng Octavia, ta cần build 1 Amphora image.

Trên CentOS / Rocky 9, hãy sử dụng:

```sh
sudo dnf -y install epel-release
sudo dnf install -y debootstrap qemu-img git e2fsprogs policycoreutils-python-utils
```

Trên Ubuntu:

```sh
sudo apt -y install debootstrap qemu-utils git kpartx
```

Pull Octavia source code:

```sh
git clone https://opendev.org/openstack/octavia -b <branch>
```

Cài đặt **diskimage-builder**, nên thao tác trong 1 virtual environment

```sh
python3 -m venv dib-venv
source dib-venv/bin/activate
pip install diskimage-builder
```

Tạo Amphora image:

```sh
cd octavia/diskimage-create
./diskimage-create.sh
```

Source octavia user openrc

```sh
. /etc/kolla/octavia-openrc.sh
```

Register image trong Glance

```sh
openstack image create amphora-x64-haproxy.qcow2 --container-format bare --disk-format qcow2 --private --tag amphora --file amphora-x64-haproxy.qcow2 --property hw_architecture='x86_64' --property hw_rng_model=virtio
```

### Debug

Ta có thể SSH vào 1 amphora bằng lệnh

```sh
ssh -i /etc/kolla/octavia-worker/octavia_ssh_key ubuntu@<amphora_ip>
```

### Upgrade

Nếu bạn upgrade từ Ussuri release, bạn phải tắt ```octavia_auto_configure``` trong ```globals.yml``` và giữ các cấu hình octavia khác như trước đó

## OVN provider

Để bật OVN provider, đặt tham số sau trong ```globals.yml```

```sh
octavia_provider_drivers: "ovn:OVN provider"
octavia_provider_agents: "ovn"
```