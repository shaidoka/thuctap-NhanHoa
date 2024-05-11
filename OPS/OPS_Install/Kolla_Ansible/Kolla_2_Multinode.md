# Multinode Deployment of Kolla

## Deploy a registry

1 Docker registry là 1 locally-hosted registry mà thay thế sự cần thiết của việc pull images từ public registry. Kolla có thể hoạt động với hoặc không với 1 local registry, tuy nhiên trong mô hình multinode deployment thì điều này lại được khuyến khích. Mặc dù chỉ cần 1 registry được triển khai, các tính năng HA vẫn được thiết lập cho dịch vụ này.

1 registry có thể được triển khai vô cùng đơn giản bằng lệnh:

```sh
docker run -d \
 --network host \
 --name registry \
 --restart=always \
 -e REGISTRY_HTTP_ADDR=0.0.0.0:4000 \
 -v registry:/var/lib/registry \
 registry:2
```

Ở đây chúng ta sử dụng port 4000 để tránh conflict với Keystone. Nếu registry không chạy trên cùng host với Keystone, bạn có thể bỏ đối số ```-e``` đi.

Chỉnh sửa file ```globals.yml``` và thêm đoạn cấu hình sau (trong đó ```192.168.1.100:4000``` là địa chỉ IP và port mà registry lắng nghe)

```sh
docker_registry: 192.168.1.100:4000
docker_registry_insecure: yes
```

## Chỉnh sửa Inventory File

Ansible inventory file bao gồm tất cả thông tin cần thiết để xác định service nào sẽ đặt ở host nào. Chỉnh sửa inventory file trong Kolla Ansible directory ```ansible/inventory/multinode```. Nếu Kolla Ansible đã được cài đặt với pip, bạn có thể tìm nó ở ```/usr/local/share/kolla-ansible/ansible/inventory/multinode```

Thêm địa chỉ IP hoặc hostname vào 1 group và các dịch vụ liên quan đến group đó sẽ được đặt vào host đó. Các địa chỉ IP hoặc hostname phải được thêm vào group ```control```, ```network```, ```compute```, ```monitoring```, hoặc ```storage```. Ngoài ra, định nghĩa thêm tham số trong inventory như ```ansible_ssh_user```, ```ansible_become``` và ```ansible_private_key_file/ansible_ssh_pass``` nếu cần thiết

Ví dụ:

```sh
# These initial groups are the only groups required to be modified. The
# additional groups are for more control of the environment.
[control]
# These hostname must be resolvable from your deployment host
ctl1           ansible_ssh_user=<ssh-username> ansible_become=True ansible_private_key_file=<path/to/private-key-file>
192.168.122.24 ansible_ssh_user=<ssh-username> ansible_become=True ansible_private_key_file=<path/to/private-key-file>
```

Với các roles nâng cao hơn, người vận hành có thể chỉnh sửa services nào sẽ được liên quan đến group nào. Ghi nhớ rằng một vài service cần phải chung 1 group và thay đổi điều này có thể làm deployment không hoạt động. Ví dụ:

```sh
[kibana:children]
control

[elasticsearch:children]
control

[loadbalancer:children]
network
```

## Các biến Host và Group

Thông thường, cấu hình của Kolla Ansible được lưu trữ trong file ```globals.yml```. Các biến trong file này áp dụng lên tất cả các hosts. Trong 1 môi trường với nhiều hosts, các hosts khác nhau sẽ có những giá trị khác nhau cho biến. 1 ví dụ thường thấy là network interface, ```api_interface``` chẳng hạn

Biến host và group của ansible có thể được cấp bằng nhiều cách. Trong đó dễ nhất là chỉ định thẳng trong file inventory

```sh
# Host with a host variable
[control]
ctl1 api_interface=eth3

# Group with a group variable
[control:vars]
api_interface=eth4
```

Tuy vậy, trong những môi trường cloud lớn với sự tham gia của nhiều node với các vai trò khác nhau. Cách cấu hình kể trên có thể dẫn đến những khó khăn không nhỏ trong quá trình vận hành và bảo trì, vì vậy chúng tôi khuyên rằng bạn nên sử dụng đường dẫn ```host_vars``` và ```group_vars``` chứa các YAML files với các biến được định nghĩa trong đó. Như thế này:

```sh
inventory/
|__group_vars/
|  |__control
|__host_vars/
|  |__ctl1
|__multinode
```

Ansible's variable precedence rules khá phức tạp, sử dụng host và group variables sẽ giúp bạn làm quen với nó. Playbook group variables trong ```ansible/group_vars/all.yml``` định nghĩa mặc định cho global, và những biến này sẽ đươc ưu tiên hơn những biến định nghĩa trong 1 inventory file và inventory ```group_vars/all```, nhưng không hơn inventory ```group_var/*```. Biến trong các file extra như ```globals.yml``` có độ ưu tiên cao nhất, vì vậy bất kỳ biến mà phải khác nhau giữa các host thì không được định nghĩa trong ```globals.yml```

## Deploying Kolla

Đầu tiên, kiểm tra rằng tất cả các host đã sẵn sàng để triển khai:

```sh
kolla-ansible prechecks -i <path/to/multinode/inventory/file>
```

Deploy:

```sh
kolla-ansible deploy -i <path/to/multinode/inventory/file>
```