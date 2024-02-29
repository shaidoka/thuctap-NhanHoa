# Launch an instance

Trong môi trường có bao gồm Container Infrastructure Management service, bạn có thể provision những cụm container tạo nên bởi VM hoặc baremetal server. Container Infrastructure Management service sử dụng Cluster Templates để mô tả cách Cluster được xây dựng. Với mỗi ví dụ dưới đây, chúng ta sẽ tạo 1 Cluster Template cho 1 COE cụ thể và sau đó ta sẽ provision 1 Cluster sử dụng Cluster Template tương ứng. Sau đó, ta có thể sử dụng COE client hoặc endpoint để tạo containers.

## Create an external network (Optional)

Để tạo 1 magnum cluster, ta cần 1 external network. Nếu chưa có, hãy tạo bằng các thao tác dưới đây:

Tạo 1 external network với 1 provider phù hợp (tùy thuộc vào môi trường của bạn):

```sh
openstack network create public --provider-network-type vxlan \
                                  --external \
                                  --project service

openstack subnet create public-subnet --network public \
                                  --subnet-range 192.168.1.0/24 \
                                  --gateway 192.168.1.1 \
                                  --ip-version 4
```

## Create a keypair (Optional)

Để tạo 1 magnum cluster, ta cần 1 keypair để đưa vào các compute instance của cluster. Nếu chưa có sẵn trong project, hãy tạo 1 cái:

```sh
openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey
```

## Upload the images required for your clusters to the Image service

Kubernetes driver yêu cầu 1 Fedora CoreOS image. Hãy tìm trong phần 'Supported versions' để biết thêm thông tin với mỗi bản phát hành của Magnum.

1. Download image

```sh
export FCOS_VERSION="35.20220116.3.0"
wget https://builds.coreos.fedoraproject.org/prod/streams/stable/builds/${FCOS_VERSION}/x86_64/fedora-coreos-${FCOS_VERSION}-openstack.x86_64.qcow2.xz
unxz fedora-coreos-${FCOS_VERSION}-openstack.x86_64.qcow2.xz
```

2. Register image với Image service và đặt thuộc tính ```os_distro``` thành ```fedora-coreos```

```sh
openstack image create \
                      --disk-format=qcow2 \
                      --container-format=bare \
                      --file=fedora-coreos-${FCOS_VERSION}-openstack.x86_64.qcow2 \
                      --property os_distro='fedora-coreos' \
                      fedora-coreos-latest
```

## Provision a K8s cluster and create a deployment

Ví dụ dưới đây sẽ provision 1 K8s cluster với 1 master và 1 node. Sau đó, sử dụng K8s native client là ```kubectl``` để tạo 1 deployment.

1. Tạo 1 cluster template cho 1 k8s cluster sử dụng ```fedora-coreos-latest``` image, flavor là ```m1.small```, ```public``` external network và ```8.8.8.8``` cho DNS server:

```sh
openstack coe cluster template create kubernetes-cluster-template \
                     --image fedora-coreos-latest \
                     --external-network public \
                     --dns-nameserver 8.8.8.8 \
                     --master-flavor m1.small \
                     --flavor m1.small \
                     --coe kubernetes
```

2. Tạo 1 cluster với 1 node và 1 master sử dụng **mykey** là keypair:

```sh
openstack coe cluster create kubernetes-cluster \
                        --cluster-template kubernetes-cluster-template \
                        --master-count 1 \
                        --node-count 1 \
                        --keypair mykey
```

Thời gian cluster tạo dựng có thể kéo dài, phụ thuộc vào hiệu suất hạ tầng của bạn. Để kiểm tra trạng thái của cluster, bạn có thể sử dụng lệnh ```openstack coe cluster list``` hoặc ```openstack coe cluster show kubernetes-cluster```

3. Thêm những credentials của cluster bên trên vào môi trường của bạn

```sh
mkdir -p ~/clusters/kubernetes-cluster
cd ~/clusters/kubernetes-cluster
openstack coe cluster config kubernetes-cluster
```

Lệnh bên trên sẽ lưu authentication artifacts vào trong đường dẫn ```~/clusters/kubernetes-cluster```. Nó sẽ đưa ra 1 lệnh để thiết lập biến môi trường ```KUBECONFIG```, ví dụ:

```sh
export KUBECONFIG=/home/user/clusters/kubernetes-cluster/config
```

4. Ta có thể liệt kê các thành phần controller của K8s bằng lệnh:

```sh
kubectl -n kube-system get po
```

5. Tạo 1 nginx deployment:

```sh
kubectl run nginx --image=nginx --replicas=5
kubectl get po
```

6. Để xóa cluster, ta có thể sử dụng lệnh

```sh
openstack coe cluster delete kubernetes-cluster
```