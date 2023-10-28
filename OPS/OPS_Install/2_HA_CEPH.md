# Cài đặt node CEPH AIO (Luminous)

## Phần 1 - Chuẩn bị

**Phân hoạch IP:**
- Đường Management: eth0 - 172.16.10.19 - Sử dụng để truy cập vào quản trị, cài đặt
- Đường CephCOM: eth2 - 172.16.12.19 - Sử dụng để client kết nối đến, tương ứng đường storage trong OPS cluster
- Đường CephREP: eth1 - 172.16.11.19 - Sử dụng để cụm CEPH đồng bộ dữ liệu với nhau

**Setup node:**

```sh
hostnamectl set-hostname cephaio

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
systemctl stop firewalld
systemctl disable firewalld
```

Thêm IP đường CEPH-COM vào file hosts:

```sh
echo "172.16.12.19 cephaio" >> /etc/hosts
```

Cấu hình chrony

```sh
yum -y install chrony
VIP_MGNT_IP='172.16.10.10'
sed -i '/server/d' /etc/chrony.conf
echo "server $VIP_MGNT_IP iburst" >> /etc/chrony.conf
systemctl enable chronyd.service
systemctl restart chronyd.service
chronyc sources
```

## Phần 2 - Cài đặt CEPH

Thêm user ```cephuser```, pass ```Welcome123```

```sh
useradd -d /home/cephuser -m cephuser
passwd cephuser

echo "cephuser ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephuser
chmod 0440 /etc/sudoers.d/cephuser
```

Bổ sung repo cài đặt CEPH

```sh
cat <<EOF> /etc/yum.repos.d/ceph.repo
[ceph]
name=Ceph packages for $basearch
baseurl=https://download.ceph.com/rpm-luminous/el7/x86_64/
enabled=1
priority=2
gpgcheck=1
gpgkey=https://download.ceph.com/keys/release.asc

[ceph-noarch]
name=Ceph noarch packages
baseurl=https://download.ceph.com/rpm-luminous/el7/noarch
enabled=1
priority=2
gpgcheck=1
gpgkey=https://download.ceph.com/keys/release.asc

[ceph-source]
name=Ceph source packages
baseurl=https://download.ceph.com/rpm-luminous/el7/SRPMS
enabled=0
priority=2
gpgcheck=1
gpgkey=https://download.ceph.com/keys/release.asc
EOF

yum update -y
```

Cài đặt python-setuptools và ceph-deploy

```sh
yum install python-setuptools ceph-deploy -y
```

Cấu hình SSH-key

```sh
ssh-keygen

cat <<EOF> /root/.ssh/config
Host cephaio
    Hostname cephaio
    User cephuser
EOF

ssh-copy-id cephaio
```

### Cấu hình CEPH

Tạo thư mục ```ceph-deploy``` để thao tác và cài đặt vận hành Cluster

```sh
mkdir /home/ceph-deploy && cd /home/ceph-deploy
```

Khởi tạo file cấu hình cho cụm với node quản lý là ```cephaio```

```sh
ceph-deploy new cephaio
```

Cấu hình file ```ceph.conf```

```sh
cat << EOF >> ceph.conf
osd pool default size = 2
osd pool default min size = 1
osd pool default pg num = 128
osd pool default pgp num = 128

osd crush chooseleaf type = 0

public network = 172.16.12.19/24
cluster network = 172.16.11.19/24
EOF
```

Trong đó:
- ```public network```: là đường CephCOM
- ```cluster network```: là đường CephRep

### Cài đặt Ceph qua Ceph deploy

Cài đặt

```sh
ceph-deploy install --release luminous cephaio
```

Kiểm tra

```sh
ceph -v
```

![](/images/OPS_Install_14.png)

Khởi tạo cluster với các node mon dựa trên file ```ceph.conf```

```sh
ceph-deploy mon create-initial
```

![](./images/OPS_Install_15.png)

Để node ```cephaio``` có thể thao tác với cluster, chúng ta cần gán cho node ```cephaio``` với quyền admin bằng cách bổ sung cho node này ```admin.keyring```

```sh
ceph-deploy admin cephaio
```

Kiểm tra:

```sh
ceph -s
```

![](./images/OPS_Install_16.png)

### Khởi tạo MGR

Ceph-mgr là thành phần cài đặt yêu cầu cần khởi tạo từ bản Luminous, có thể cài đặt trên nhiều node hoạt động theo cơ chế Active-Passive

Cài đặt ceph-mgr trên cephaio

```sh
ceph-deploy mgr create cephaio
```

Ceph-mgr hỗ trợ dashboard để quan sát trạng thái của cluster, enable mgr dashboard trên host cephaio

```sh
ceph mgr module enable dashboard
ceph mgr services
```

Truy cập

```sh
http://<ip-cephaio>:7000
```

### Tạo OSD

```sh
ceph-deploy disk zap cephaio /dev/sdb

ceph-deploy osd create --data /dev/sdb cephaio
```

![](./images/OPS_Install_17.png)

Điều chỉnh Crush để có thể Replicate trên OSD thay vì trên HOST

```sh
cd /home/ceph-deploy
ceph osd getcrushmap -o crushmap
crushtool -d crushmap -o crushmap.decom
sed -i 's|step choose firstn 0 type osd|step chooseleaf firstn 0 type osd|g' crushmap.decom
crushtool -c crushmap.decom -o crushmap.new
ceph osd setcrushmap -i crushmap.new
```

### Kiểm tra lại trạng thái và OSD

Trạng thái

```sh
ceph -s
```

![](./images/OPS_Install_18.png)

OSD

```sh
ceph osd df tree
```

![](./images/OPS_Install_19.png)

# Cài đặt các node Controller

## Phần 1 - Thiết lập ban đầu

