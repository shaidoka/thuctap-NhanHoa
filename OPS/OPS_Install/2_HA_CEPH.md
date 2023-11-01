# Cài đặt node CEPH AIO (Luminous)

## Phần 1 - Chuẩn bị

**Phân hoạch IP:**
- Đường Management: eth0 - 172.16.10.19 - Sử dụng để truy cập vào quản trị, cài đặt
- Đường CephCOM: eth2 - 172.16.12.19 - Sử dụng để client kết nối đến
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

Các dải IP sử dụng trong bài lab:
- **172.16.10.0/24**: Management - dùng để truy cập vào node để quản trị
- **172.16.11.0/24**: Provider - dùng cho Neutron cung cấp internet cho VM
- **172.16.12.0/24**: CephCOM - dùng để kết nối truyền dữ liệu với CEPH
- **172.16.13.0/24**: DataVM - dùng để đồng bộ dữ liệu giữa các node

## Phần 1 - Thiết lập ban đầu

Set hostname:

```sh
hostnamectl set-hostname ctl1
```

Cấu hình network, tắt selinux, tắt firewalld, cấu hình chronyd, cấu hình file hosts.

Setup keypair:

```sh
ssh-keygen
```

```sh
ssh-copy-id -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa.pub root@ctl2
ssh-copy-id -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa.pub root@ctl3
```

Cấu hình sysctl

```sh
echo 'net.ipv4.conf.all.arp_ignore = 1'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.arp_announce = 2'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.rp_filter = 2'  >> /etc/sysctl.conf
echo 'net.netfilter.nf_conntrack_tcp_be_liberal = 1'  >> /etc/sysctl.conf

cat << EOF >> /etc/sysctl.conf
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.tcp_keepalive_time = 6
net.ipv4.tcp_keepalive_intvl = 3
net.ipv4.tcp_keepalive_probes = 6
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.default.rp_filter = 0
EOF

modprobe ip_conntrack

sysctl -p
```

### Lặp lại các bước tương tự với CTL2 và CTL3 !!!

## Phần 2: Setup Galera Cluster

### Setup repo và cài đặt MariaDB

**Trên tất cả các node CTL**, thực hiện:

```sh
cat << EOF >> /etc/yum.repos.d/MariaDB.repo
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.3/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF

yum -y update

yum install -y mariadb mariadb-server
systemctl stop mariadb
```

### Cấu hình

**Trên node CTL1**, cấu hình:

```sh
cp /etc/my.cnf.d/server.cnf /etc/my.cnf.d/server.cnf.bak

echo '[server]
[mysqld]
bind-address=172.16.10.11

[galera]
wsrep_on=ON
wsrep_provider=/usr/lib64/galera/libgalera_smm.so
wsrep_cluster_address="gcomm://172.16.10.11,172.16.10.12,172.16.10.13"
binlog_format=row
default_storage_engine=InnoDB
innodb_autoinc_lock_mode=2
wsrep_cluster_name="galera_cluster"
bind-address=172.16.10.11
wsrep_node_address="172.16.10.11"
wsrep_node_name="ctl1"
wsrep_sst_method=rsync

skip-name-resolve
max_connections = 10240
innodb_locks_unsafe_for_binlog=1
query_cache_size=0
query_cache_type=0
innodb_log_file_size=100M
innodb_file_per_table
innodb_flush_log_at_trx_commit=2
[embedded]
[mariadb]
[mariadb-10.3]
' > /etc/my.cnf.d/server.cnf
```

**Trên node CTL2**, cấu hình:

```sh
cp /etc/my.cnf.d/server.cnf /etc/my.cnf.d/server.cnf.bak

echo '[server]
[mysqld]
bind-address=172.16.10.12

[galera]
wsrep_on=ON
wsrep_provider=/usr/lib64/galera/libgalera_smm.so
wsrep_cluster_address="gcomm://172.16.10.11,172.16.10.12,172.16.10.13"
binlog_format=row
default_storage_engine=InnoDB
innodb_autoinc_lock_mode=2
wsrep_cluster_name="galera_cluster"
bind-address=172.16.10.12
wsrep_node_address="172.16.10.12"
wsrep_node_name="ctl2"
wsrep_sst_method=rsync

skip-name-resolve
max_connections = 10240
innodb_locks_unsafe_for_binlog=1
query_cache_size=0
query_cache_type=0
innodb_log_file_size=100M
innodb_file_per_table
innodb_flush_log_at_trx_commit=2
[embedded]
[mariadb]
[mariadb-10.3]
' > /etc/my.cnf.d/server.cnf
```

**Trên node CTL3**, cấu hình:

```sh
cp /etc/my.cnf.d/server.cnf /etc/my.cnf.d/server.cnf.bak

echo '[server]
[mysqld]
bind-address=172.16.10.13

[galera]
wsrep_on=ON
wsrep_provider=/usr/lib64/galera/libgalera_smm.so
wsrep_cluster_address="gcomm://172.16.10.11,172.16.10.12,172.16.10.13"
binlog_format=row
default_storage_engine=InnoDB
innodb_autoinc_lock_mode=2
wsrep_cluster_name="galera_cluster"
bind-address=172.16.10.13
wsrep_node_address="172.16.10.13"
wsrep_node_name="ctl3"
wsrep_sst_method=rsync

skip-name-resolve
max_connections = 10240
innodb_locks_unsafe_for_binlog=1
query_cache_size=0
query_cache_type=0
innodb_log_file_size=100M
innodb_file_per_table
innodb_flush_log_at_trx_commit=2
[embedded]
[mariadb]
[mariadb-10.3]
' > /etc/my.cnf.d/server.cnf
```

### Khởi tạo cluster

**Trên node CTL1**, thực hiện:

```sh
galera_new_cluster
systemctl start mariadb
systemctl enable mariadb
```

**Trên node CTL2 và CTL3**, thực hiện:

```sh
systemctl start mariadb
systemctl enable mariadb
```

### Kiểm tra

Trên node CTL bất kỳ, thực hiện:

```sh
mysql -u root -e "SHOW STATUS LIKE 'wsrep_cluster_size'"
```

![](./images/OPS_Install_20.png)

### Đặt mật khẩu và phân quyền cho MariaDB

**Trên CTL1:**

```sh
password_galera_root=Welcome123
cat << EOF | mysql -uroot
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'172.16.10.11' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'172.16.10.12' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'172.16.10.13' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON *.* TO 'root'@'ctl1' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'ctl2' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'ctl3' IDENTIFIED BY '$password_galera_root';FLUSH PRIVILEGES;
EOF
```

### Cấu hình HAProxy check Mysql

**Trên node CTL1**, cài đặt và cấu hình plugin check Mysql

```sh
yum install rsync xinetd crudini git -y
git clone https://github.com/thaonguyenvan/percona-clustercheck
cp percona-clustercheck/clustercheck /usr/local/bin

cat << EOF >> /etc/xinetd.d/mysqlchk
service mysqlchk
{
      disable = no
      flags = REUSE
      socket_type = stream
      port = 9200
      wait = no
      user = nobody
      server = /usr/local/bin/clustercheck
      log_on_failure += USERID
      only_from = 0.0.0.0/0
      per_source = UNLIMITED
}
EOF
```

Tạo service:

```sh
echo 'mysqlchk 9200/tcp # MySQL check' >> /etc/services
```

Tạo tài khoản check mysql

```sh
mysql -uroot -pWelcome123
GRANT PROCESS ON *.* TO 'clustercheckuser'@'localhost' IDENTIFIED BY 'clustercheckpassword!';
FLUSH PRIVILEGES;
EXIT
```

Bật xinetd

```sh
systemctl enable xinetd --now
```

Kiểm tra:

```sh
clustercheck
```

![](./images/OPS_Install_21.png)

**Làm tương tự với 2 node CTL2 và CTL3 !!!**

## Phần 3: Cài đặt RabbitMQ Cluster

### Cài đặt môi trường và RabbitMQ Cluster

**Thực hiện trên cả 3 node CTL:**

```sh
yum -y install epel-release
yum -y install erlang socat wget

wget https://github.com/rabbitmq/rabbitmq-server/releases/download/rabbitmq_v3_6_15/rabbitmq-server-3.6.15-1.el7.noarch.rpm
rpm --import https://www.rabbitmq.com/rabbitmq-release-signing-key.asc
rpm -Uvh rabbitmq-server-3.6.15-1.el7.noarch.rpm

systemctl enable rabbitmq-server --now
systemctl status rabbitmq-server

rabbitmq-plugins enable rabbitmq_management
chown -R rabbitmq:rabbitmq /var/lib/rabbitmq/
```

### Cấu hình Cluster RabbitMQ

**Trên Node CTL1**, khởi tạo RabbitMQ Cluster:

```sh
rabbitmqctl add_user openstack Welcome123
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
rabbitmqctl set_user_tags openstack administrator
rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'

scp -p /var/lib/rabbitmq/.erlang.cookie ctl2:/var/lib/rabbitmq/.erlang.cookie
scp -p /var/lib/rabbitmq/.erlang.cookie ctl3:/var/lib/rabbitmq/.erlang.cookie

rabbitmqctl start_app
rabbitmqctl cluster_status
```

**Trên node CTL2 và CTL3**, thực hiện join cluster:

```sh
chown rabbitmq:rabbitmq /var/lib/rabbitmq/.erlang.cookie
chmod 400 /var/lib/rabbitmq/.erlang.cookie

systemctl restart rabbitmq-server.service

rabbitmqctl stop_app
rabbitmqctl join_cluster rabbit@ctl1
rabbitmqctl start_app
```

![](./images/OPS_Install_23.png)

## Phần 4: Triển khai PCS

### Chuẩn bị

**Trên tất cả các node CTL, cài đặt pacemaker corosync:**

```sh
yum install pacemaker corosync haproxy pcs fence-agents-all resource-agents psmisc policycoreutils-python -y

echo Welcome123 | passwd --stdin hacluster

systemctl enable pcsd pacemaker corosync haproxy

systemctl start pcsd
```

### Cấu hình Cluster

**Trên node CTL1:**

```sh
pcs cluster auth ctl1 ctl2 ctl3 -u hacluster -p Welcome123
pcs cluster setup --name ha_cluster ctl1 ctl2 ctl3

pcs cluster enable --all
pcs cluster start --all

pcs property set stonith-enabled=false
pcs property set no-quorum-policy=ignore
pcs property set default-resource-stickiness="INFINITY"

pcs resource create vip_public ocf:heartbeat:IPaddr2 ip=172.16.10.20 cidr_netmask=20 nic=eth0 \
meta migration-threshold=3 failure-timeout=60 resource-stickiness=1 \
op monitor interval=5 timeout=20 \
op start interval=0 timeout=30 \
op stop interval=0 timeout=30

pcs resource create p_haproxy systemd:haproxy \
meta migration-threshold=3 failure-timeout=120 target-role=Started \
op monitor interval=30 timeout=60 \
op start interval=0 timeout=60 \
op stop interval=0 timeout=60

pcs constraint colocation add vip_public with p_haproxy score=INFINITY
pcs constraint order start vip_public then start p_haproxy
```

![](./images/OPS_Install_24.png)

### Cấu hình HAProxy

**Thực hiện trên cả 3 node CTL1, CTL2, CTL3:**

```sh
cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.org 
rm -rf /etc/haproxy/haproxy.cfg

cat >> /etc/haproxy/haproxy.cfg << EOF
global
    daemon
    group  haproxy
    log  /dev/log local0
    log /dev/log    local1 notice
    maxconn  16000
    pidfile  /var/run/haproxy.pid
    stats  socket /var/lib/haproxy/stats
    tune.bufsize  32768
    tune.maxrewrite  1024
    user  haproxy


defaults
    log  global
    maxconn  8000
    mode  http
    option  redispatch
    option  http-server-close
    option  splice-auto
    retries  3
    timeout  http-request 20s
    timeout  queue 1m
    timeout  connect 10s
    timeout  client 1m
    timeout  server 1m
    timeout  check 10s

listen stats
    bind 172.16.10.20:8080
    mode http
    stats enable
    stats uri /stats
    stats realm HAProxy\ Statistics

listen mysqld 
    bind 172.16.10.20:3306
    balance  leastconn
    mode  tcp
    option  httpchk
    option  tcplog
    option  clitcpka
    option  srvtcpka
    timeout client  28801s
    timeout server  28801s    
    server ctl1 172.16.10.11:3306 check port 9200 inter 5s fastinter 2s rise 3 fall 3 
    server ctl2 172.16.10.12:3306 check port 9200 inter 5s fastinter 2s rise 3 fall 3 backup
    server ctl3 172.16.10.13:3306 check port 9200 inter 5s fastinter 2s rise 3 fall 3 backup


listen keystone-5000
    bind 172.16.10.20:5000 
    option  httpchk
    option  httplog
    option  httpclose
    balance source
    server ctl1 172.16.10.11:5000  check inter 5s fastinter 2s downinter 2s rise 3 fall 3
    server ctl2 172.16.10.12:5000  check inter 5s fastinter 2s downinter 2s rise 3 fall 3
    server ctl3 172.16.10.13:5000  check inter 5s fastinter 2s downinter 2s rise 3 fall 3

listen keystone-35357
    bind 172.16.10.20:35357
    option  httpchk
    option  httplog
    option  httpclose
    balance source
    server ctl1 172.16.10.11:35357  check inter 5s fastinter 2s downinter 2s rise 3 fall 3
    server ctl2 172.16.10.12:35357  check inter 5s fastinter 2s downinter 2s rise 3 fall 3
    server ctl3 172.16.10.13:35357  check inter 5s fastinter 2s downinter 2s rise 3 fall 3


listen nova-api-8774
    bind 172.16.10.20:8774 
    option  httpchk
    option  httplog
    option  httpclose
    timeout server  600s
    server ctl1 172.16.10.11:8774  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl2 172.16.10.12:8774  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl3 172.16.10.13:8774  check inter 5s fastinter 2s downinter 3s rise 3 fall 3

listen nova-metadata-api
    bind 172.16.10.20:8775 
    option  httpchk
    option  httplog
    option  httpclose
    server ctl1 172.16.10.11:8775  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl2 172.16.10.12:8775  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl3 172.16.10.13:8775  check inter 5s fastinter 2s downinter 3s rise 3 fall 3

listen nova-novncproxy
	bind 172.16.10.20:6080
    balance  source
    option  httplog
    server ctl1 172.16.10.11:6080  check
    server ctl2 172.16.10.12:6080  check
    server ctl3 172.16.10.13:6080  check
    
listen nova_placement_api
    bind 172.16.10.20:8778
    balance source
    option tcpka
    option tcplog
    http-request del-header X-Forwarded-Proto
    server ctl1 172.16.10.11:8778 check inter 2000 rise 2 fall 5
    server ctl2 172.16.10.12:8778 check inter 2000 rise 2 fall 5
    server ctl3 172.16.10.13:8778 check inter 2000 rise 2 fall 5    
    
listen glance-api
    bind 172.16.10.20:9292
    option  httpchk /versions
    option  httplog
    option  httpclose
    timeout server  11m
    server ctl1 172.16.10.11:9292  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl2 172.16.10.12:9292  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl3 172.16.10.13:9292  check inter 5s fastinter 2s downinter 3s rise 3 fall 3

listen glance-registry
    bind 172.16.10.20:9191 
    timeout server  11m
    server ctl1 172.16.10.11:9191  check
    server ctl2 172.16.10.12:9191  check
    server ctl3 172.16.10.13:9191  check

listen neutron
    bind 172.16.10.20:9696 
    option  httpchk
    option  httplog
    option  httpclose
    balance source
    server ctl1 172.16.10.11:9696  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl2 172.16.10.12:9696  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl3 172.16.10.13:9696  check inter 5s fastinter 2s downinter 3s rise 3 fall 3

listen cinder-api
    bind 172.16.10.20:8776 
    option  httpchk
    option  httplog
    option  httpclose
    server ctl1 172.16.10.11:8776  check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl2 172.16.10.12:8776 backup check inter 5s fastinter 2s downinter 3s rise 3 fall 3
    server ctl3 172.16.10.13:8776 backup check inter 5s fastinter 2s downinter 3s rise 3 fall 3

  
listen horizon
    bind 172.16.10.20:80
    balance  source
    mode  http
    option  forwardfor
    option  httpchk
    option  httpclose
    option  httplog
    stick  on src
    stick-table  type ip size 200k expire 30m
    timeout  client 3h
    timeout  server 3h
    server ctl1 172.16.10.11:80  weight 1 check
    server ctl2 172.16.10.12:80  weight 1 check
    server ctl3 172.16.10.13:80  weight 1 check
EOF
```

### Restart service

**Thực hiện trên CTL1:**

```sh
pcs resource restart p_haproxy
pcs resource cleanup
```

Kiểm tra:

```sh
pcs status
```

![](./images/OPS_Install_25.png)

## Phần 5: Cài đặt các gói cần thiết cho OPS

**Thực hiện trên tất cả các node CTL**

```sh
yum -y install centos-release-openstack-queens
yum -y install crudini wget vim
yum -y install python-openstackclient openstack-selinux python2-PyMySQL
```

## Phần 6: Cấu hình memcache

**Lưu ý:** Thực hiện xong từng node mới chuyển node thực hiện

### Trên node CTL1

```sh
yum install memcached -y

sed -i "s/-l 127.0.0.1,::1/-l 172.16.10.11/g" /etc/sysconfig/memcached

systemctl enable memcached
systemctl restart memcached
```

### Trên node CTL2

```sh
yum install memcached -y

sed -i "s/-l 127.0.0.1,::1/-l 172.16.10.12/g" /etc/sysconfig/memcached

systemctl enable memcached
systemctl restart memcached
```

### Trên node CTL3

```sh
yum install -y memcached

sed -i "s/-l 127.0.0.1,::1/-l 172.16.10.13/g" /etc/sysconfig/memcached

systemctl enable memcached
systemctl restart memcached
```

## Phần 7: Cài đặt Keystone

### Tạo Database

**Trên node CTL1**, thực hiện:

```sh
mysql -u root -pWelcome123
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \
IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \
IDENTIFIED BY 'Welcome123';

GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
exit
```

### Cài đặt các gói cần thiết

**Thực hiện trên tất cả các node CTL1, 2, 3**

```sh
yum install qpid-proton-c-0.22.0-1.el7.x86_64 -y
yum install openstack-keystone httpd mod_wsgi -y
```

### Cấu hình bind port

**Trên node CTL1**, cấu hình port keystone như sau:

```sh
cp /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.11/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 5000/Listen 172.16.10.11:5000/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 35357/Listen 172.16.10.11:35357/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/^Listen.*/Listen 172.16.10.11:80/g' /etc/httpd/conf/httpd.conf
```

**Trên node CTL2**, cấu hình port keystone như sau:

```sh
cp /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.12/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 5000/Listen 172.16.10.12:5000/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 35357/Listen 172.16.10.12:35357/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/^Listen.*/Listen 172.16.10.12:80/g' /etc/httpd/conf/httpd.conf
```

**Trên node CTL3**, cấu hình port keystone như sau:

```sh
cp /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.13/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 5000/Listen 172.16.10.13:5000/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/Listen 35357/Listen 172.16.10.13:35357/g' /etc/httpd/conf.d/wsgi-keystone.conf
sed -i -e 's/^Listen.*/Listen 172.16.10.13:80/g' /etc/httpd/conf/httpd.conf
```

### Cấu hình Keystone

**Trên node CTL1**, chỉnh sửa cấu hình Keystone như sau:

```sh
cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.org
rm -rf /etc/keystone/keystone.conf

cat << EOF >> /etc/keystone/keystone.conf
[DEFAULT]
[assignment]
[auth]
[cache]
[catalog]
[cors]
[credential]
[database]
connection = mysql+pymysql://keystone:Welcome123@172.16.10.20/keystone
[domain_config]
[endpoint_filter]
[endpoint_policy]
[eventlet_server]
[federation]
[fernet_tokens]
[healthcheck]
[identity]
[identity_mapping]
[ldap]
[matchmaker_redis]
[memcache]
[oauth1]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
[policy]
[profiler]
[resource]
[revoke]
[role]
[saml]
[security_compliance]
[shadow_users]
[signing]
[token]
provider = fernet
[tokenless_auth]
[trust]
EOF
```

Phân quyền

```sh
chown root:keystone /etc/keystone/keystone.conf
```

Sync DB

```sh
su -s /bin/sh -c "keystone-manage db_sync" keystone
```

Setup fernet key

```sh
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
```

Chuyển 2 thư mục này sang 2 CTL còn lại

```sh
scp -r /etc/keystone/credential-keys /etc/keystone/fernet-keys root@ctl2:/etc/keystone/
scp -r /etc/keystone/credential-keys /etc/keystone/fernet-keys root@ctl3:/etc/keystone/
```

Bootstrap Keystone

```sh
keystone-manage bootstrap --bootstrap-password Welcome123 \
  --bootstrap-admin-url http://172.16.10.20:5000/v3/ \
  --bootstrap-internal-url http://172.16.10.20:5000/v3/ \
  --bootstrap-public-url http://172.16.10.20:5000/v3/ \
  --bootstrap-region-id RegionOne
```

Enable và start httpd

```sh
systemctl enable httpd --now
```

Export biến môi trường:

```sh
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://172.16.10.20:35357/v3
export OS_IDENTITY_API_VERSION=3
```

Tạo domain, user

```sh
openstack domain create --description "An Example Domain" example
openstack project create --domain default --description "Service Project" service

openstack project create --domain default --description "Demo Project" demo

openstack user create --domain default --password Welcome123 demo

openstack role create user
openstack role add --project demo --user demo user

unset OS_AUTH_URL OS_PASSWORD

openstack --os-auth-url http://172.16.10.20:35357/v3 \
  --os-project-domain-name Default --os-user-domain-name Default \
  --os-project-name admin --os-username admin token issue
```

Tạo file xác thực

```sh
cat << EOF >> admin-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.20:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF

cat << EOF >> demo-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.20:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF
```

**Trên noe CTL2 và CTL3**, thực hiện các việc sau:

```sh
cat << EOF >> admin-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.20:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF

cat << EOF >> demo-openrc
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=Welcome123
export OS_AUTH_URL=http://172.16.10.20:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF
```

```sh
cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.org
rm -rf /etc/keystone/keystone.conf

cat << EOF >> /etc/keystone/keystone.conf
[DEFAULT]
[assignment]
[auth]
[cache]
[catalog]
[cors]
[credential]
[database]
connection = mysql+pymysql://keystone:Welcome123@172.16.10.20/keystone
[domain_config]
[endpoint_filter]
[endpoint_policy]
[eventlet_server]
[federation]
[fernet_tokens]
[healthcheck]
[identity]
[identity_mapping]
[ldap]
[matchmaker_redis]
[memcache]
[oauth1]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
[policy]
[profiler]
[resource]
[revoke]
[role]
[saml]
[security_compliance]
[shadow_users]
[signing]
[token]
provider = fernet
[tokenless_auth]
[trust]
EOF

chown root:keystone /etc/keystone/keystone.conf
chown -R keystone:keystone /etc/keystone/credential-keys /etc/keystone/fernet-keys

systemctl enable httpd --now
```

### Kiểm tra

- Bật httpd tại CTL1, tắt tại CTL2 và CTL3:

![](./images/OPS_Install_26.png)

- Bật httpd tại CTL2, tắt tại CTL1 và CTL3:

![](./images/OPS_Install_27.png)

- Bật httpd tại CTL3, tắt tại CTL1 và CTL2:

![](./images/OPS_Install_28.png)

## Phần 8: Cài đặt Glance

### Tạo Database, User, Endpoint

**Trên node CTL1:**, tạo database như sau:

```sh
mysql -u root -pWelcome123

CREATE DATABASE glance;

GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' \
  IDENTIFIED BY 'Welcome123';

GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' \
  IDENTIFIED BY 'Welcome123';

GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
exit
```

Tạo user

```sh
openstack user create --domain default --password Welcome123 glance

openstack role add --project service --user glance admin

openstack service create --name glance --description "OpenStack Image" image
```

Tạo endpoint

```sh
openstack endpoint create --region RegionOne \
  image public http://172.16.10.20:9292

openstack endpoint create --region RegionOne \
  image admin http://172.16.10.20:9292

openstack endpoint create --region RegionOne \
  image internal http://172.16.10.20:9292
```

### Cài đặt package Glance

**Thực hiện trên tất cả các node CTL1, CTL2, CTL3**

```sh
yum install -y openstack-glance
```

### Cấu hình glance-api và glance-registry

**Trên node CTL1**, cấu hình ```glance-api```

```sh
cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org 
rm -rf /etc/glance/glance-api.conf

cat << EOF >> /etc/glance/glance-api.conf
[DEFAULT]
bind_host = 172.16.10.11
registry_host = 172.16.10.20
[cors]
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
[image_format]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_concurrency]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
[store_type_location_strategy]
[task]
[taskflow_executor]
EOF
```

Cấu hình ```glance-registry```

```sh
cp /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org
rm -rf /etc/glance/glance-registry.conf

cat << EOF >> /etc/glance/glance-registry.conf
[DEFAULT]
bind_host = 172.16.10.11
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
EOF
```

Phân quyền

```sh
chown root:glance /etc/glance/glance-api.conf
chown root:glance /etc/glance/glance-registry.conf
```

Sync DB

```sh
su -s /bin/sh -c "glance-manage db_sync" glance
```

Enable và start dịch vụ

```sh
systemctl enable openstack-glance-api openstack-glance-registry --now
```

Download và tạo image demo

```sh
wget http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
openstack image create "cirros" \
  --file cirros-0.3.5-x86_64-disk.img \
  --disk-format qcow2 --container-format bare \
  --public
```

**Trên node CTL2**, thực hiện các bước sau:

```sh
cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org 
rm -rf /etc/glance/glance-api.conf

cat << EOF >> /etc/glance/glance-api.conf
[DEFAULT]
bind_host = 172.16.10.12
registry_host = 172.16.10.20
[cors]
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
[image_format]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_concurrency]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
[store_type_location_strategy]
[task]
[taskflow_executor]
EOF
```

```sh
cp /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org
rm -rf /etc/glance/glance-registry.conf

cat << EOF >> /etc/glance/glance-registry.conf
[DEFAULT]
bind_host = 172.16.10.12
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
EOF
```

```sh
chown root:glance /etc/glance/glance-api.conf
chown root:glance /etc/glance/glance-registry.conf
```

```sh
systemctl enable openstack-glance-api openstack-glance-registry --now
```

**Tương tự, ở Node CTL3**, thực hiện các việc sau:

```sh
cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org 
rm -rf /etc/glance/glance-api.conf

cat << EOF >> /etc/glance/glance-api.conf
[DEFAULT]
bind_host = 172.16.10.13
registry_host = 172.16.10.20
[cors]
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
[image_format]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_concurrency]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
[store_type_location_strategy]
[task]
[taskflow_executor]
EOF
```

```sh
cp /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org
rm -rf /etc/glance/glance-registry.conf

cat << EOF >> /etc/glance/glance-registry.conf
[DEFAULT]
bind_host = 172.16.10.13
[database]
connection = mysql+pymysql://glance:Welcome123@172.16.10.20/glance
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:5000
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = glance
password = Welcome123
[matchmaker_redis]
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
[oslo_messaging_zmq]
[oslo_policy]
[paste_deploy]
flavor = keystone
[profiler]
EOF
```

```sh
chown root:glance /etc/glance/glance-api.conf
chown root:glance /etc/glance/glance-registry.conf
```

```sh
systemctl enable openstack-glance-api openstack-glance-registry --now
```

### Copy image từ CTL1 sang CTL2 và CTL3

**Trên CTL1:**

```sh
cd /var/lib/glance/images/
scp 27dd7cae-ca56-41ac-87a2-2ae1b6359620 root@ctl2:/var/lib/glance/images/
scp 27dd7cae-ca56-41ac-87a2-2ae1b6359620 root@ctl3:/var/lib/glance/images/
```

**Trên CTL2 và CTL3:**

```sh
chown -R glance:glance /var/lib/glance/images
```

### Kiểm tra

- Bật Glance services tại CTL 1, tắt Glance services trên CTL 2 3, get list image

![](./images/OPS_Install_29.png)

- Bật Glance services tại CTL 2, tắt Glance services trên CTL 1 3, get list image

![](./images/OPS_Install_30.png)

- Bật Glance services tại CTL 3, tắt Glance services trên CTL 1 2, get list image

![](./images/OPS_Install_31.png)

## Phần 9: Cài đặt Nova

### Cài đặt các gói cần thiết

**Thực hiện trên tất cả các node CTL:**

```sh
yum install -y openstack-nova-api openstack-nova-conductor \
  openstack-nova-console openstack-nova-novncproxy \
  openstack-nova-scheduler openstack-nova-placement-api
```

### Tạo DB, User, Endpoint

**Thực hiện trên node CTL1**, tạo database như sau:

```sh
mysql -u root -pWelcome123

CREATE DATABASE nova_api;
CREATE DATABASE nova;
CREATE DATABASE nova_cell0;

GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;


GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;


GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'%' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
exit
```

Tạo user và endpoint

```sh
openstack user create --domain default --password Welcome123 nova
openstack role add --project service --user nova admin
openstack service create --name nova \
  --description "OpenStack Compute" compute

openstack endpoint create --region RegionOne \
  compute public http://172.16.10.20:8774/v2.1
openstack endpoint create --region RegionOne \
  compute admin http://172.16.10.20:8774/v2.1
openstack endpoint create --region RegionOne \
  compute internal http://172.16.10.20:8774/v2.1

openstack user create --domain default --password Welcome123 placement
openstack role add --project service --user placement admin
openstack service create --name placement --description "Placement API" placement
  
openstack endpoint create --region RegionOne placement public http://172.16.10.20:8778
openstack endpoint create --region RegionOne placement admin http://172.16.10.20:8778
openstack endpoint create --region RegionOne placement internal http://172.16.10.20:8778
```

### Cấu hình Nova

**Trên node CTL1**, cấu hình file ```nova.conf``` như sau:

```sh
cp /etc/nova/nova.conf /etc/nova/nova.conf.org 
rm -rf /etc/nova/nova.conf

cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
my_ip = 172.16.10.11
enabled_apis = osapi_compute,metadata
use_neutron = True
osapi_compute_listen=172.16.10.11
metadata_host=172.16.10.11
metadata_listen=172.16.10.11
metadata_listen_port=8775
firewall_driver = nova.virt.firewall.NoopFirewallDriver
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
[api]
auth_strategy = keystone
[api_database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova_api
[barbican]
[cache]
backend = oslo_cache.memcache_pool
enabled = true
memcache_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.20:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.20:5000/v3
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
[matchmaker_redis]
[metrics]
[mks]
[neutron]
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.20:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
discover_hosts_in_cells_interval = 300
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
novncproxy_host=172.16.10.11
enabled = true
#vncserver_listen = 172.16.10.11
#vncserver_proxyclient_address = 172.16.10.11
novncproxy_base_url = http://172.16.10.20:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Thêm vào file ```00-nova-placement-api.conf```

```sh
cat << 'EOF' >> /etc/httpd/conf.d/00-nova-placement-api.conf

<Directory /usr/bin>
   <IfVersion >= 2.4>
      Require all granted
   </IfVersion>
   <IfVersion < 2.4>
      Order allow,deny
      Allow from all
   </IfVersion>
</Directory>
EOF
```

Cấu hình bind port cho nova-placement

```sh
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.11/g' /etc/httpd/conf.d/00-nova-placement-api.conf
sed -i -e 's/Listen 8778/Listen 172.16.10.11:8778/g' /etc/httpd/conf.d/00-nova-placement-api.conf
systemctl restart httpd
```

Sync db

```sh
su -s /bin/sh -c "nova-manage api_db sync" nova
su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova
su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova
su -s /bin/sh -c "nova-manage db sync" nova
```

Enable và start service

```sh
systemctl enable openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy

systemctl restart openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy

openstack compute service list
```

**Trên node CTL2**, cấu hình ```nova.conf```:

```sh
cp /etc/nova/nova.conf /etc/nova/nova.conf.org 
rm -rf /etc/nova/nova.conf

cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
my_ip = 172.16.10.12
enabled_apis = osapi_compute,metadata
use_neutron = True
osapi_compute_listen=172.16.10.12
metadata_host=172.16.10.12
metadata_listen=172.16.10.12
metadata_listen_port=8775
firewall_driver = nova.virt.firewall.NoopFirewallDriver
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
[api]
auth_strategy = keystone
[api_database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova_api
[barbican]
[cache]
backend = oslo_cache.memcache_pool
enabled = true
memcache_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.20:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.20:5000/v3
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
[matchmaker_redis]
[metrics]
[mks]
[neutron]
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.20:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
discover_hosts_in_cells_interval = 300
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
novncproxy_host=172.16.10.12
enabled = true
#vncserver_listen = 172.16.10.12
#vncserver_proxyclient_address = 172.16.10.12
novncproxy_base_url = http://172.16.10.20:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Thêm vào file ```00-nova-placement-api.conf```

```sh
cat << 'EOF' >> /etc/httpd/conf.d/00-nova-placement-api.conf

<Directory /usr/bin>
   <IfVersion >= 2.4>
      Require all granted
   </IfVersion>
   <IfVersion < 2.4>
      Order allow,deny
      Allow from all
   </IfVersion>
</Directory>
EOF
```

Cấu hình bind port cho nova-placement

```sh
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.12/g' /etc/httpd/conf.d/00-nova-placement-api.conf
sed -i -e 's/Listen 8778/Listen 172.16.10.12:8778/g' /etc/httpd/conf.d/00-nova-placement-api.conf

systemctl restart httpd
```

Enable và start service

```sh
systemctl enable openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy

systemctl start openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy
```

**Trên node CTL3**, cấu hình nova:

```sh
cp /etc/nova/nova.conf /etc/nova/nova.conf.org 
rm -rf /etc/nova/nova.conf

cat << EOF >> /etc/nova/nova.conf
[DEFAULT]
my_ip = 172.16.10.13
enabled_apis = osapi_compute,metadata
use_neutron = True
osapi_compute_listen=172.16.10.13
metadata_host=172.16.10.13
metadata_listen=172.16.10.13
metadata_listen_port=8775
firewall_driver = nova.virt.firewall.NoopFirewallDriver
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
[api]
auth_strategy = keystone
[api_database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova_api
[barbican]
[cache]
backend = oslo_cache.memcache_pool
enabled = true
memcache_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
connection = mysql+pymysql://nova:Welcome123@172.16.10.20/nova
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.20:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.20:5000/v3
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
[matchmaker_redis]
[metrics]
[mks]
[neutron]
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.20:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
discover_hosts_in_cells_interval = 300
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
novncproxy_host=172.16.10.13
enabled = true
#vncserver_listen = 172.16.10.13
#vncserver_proxyclient_address = 172.16.10.13
novncproxy_base_url = http://172.16.10.20:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Thêm vào file ```00-nova-placement-api.conf```:

```sh
cat << 'EOF' >> /etc/httpd/conf.d/00-nova-placement-api.conf

<Directory /usr/bin>
   <IfVersion >= 2.4>
      Require all granted
   </IfVersion>
   <IfVersion < 2.4>
      Order allow,deny
      Allow from all
   </IfVersion>
</Directory>
EOF
```

Cấu hình port cho nova-placement

```sh
sed -i -e 's/VirtualHost \*/VirtualHost 172.16.10.13/g' /etc/httpd/conf.d/00-nova-placement-api.conf
sed -i -e 's/Listen 8778/Listen 172.16.10.13:8778/g' /etc/httpd/conf.d/00-nova-placement-api.conf
systemctl restart httpd
```

Enable và start service

```sh
systemctl enable openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy

systemctl start openstack-nova-api \
  openstack-nova-scheduler openstack-nova-consoleauth \
  openstack-nova-conductor openstack-nova-novncproxy
```

### Kiểm tra

- Bật Nova services tại CTL 1, tắt Nova services trên CTL 2 3, list nova services

![](./images/OPS_Install_32.png)

- Bật Nova services tại CTL 2, tắt Nova services trên CTL 1 3, list nova services

![](./images/OPS_Install_33.png)

- Bật Nova services tại CTL 3, tắt Nova services trên CTL 1 2, list nova services

![](./images/OPS_Install_34.png)

## Phần 10: Cài đặt Neutron

### Cài đặt các package cần thiết

**Thực hiện trên tất cả các node**

```sh
yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y
```

### Tạo Database, User, Endpoint

**Thực hiện trên node CTL1**

Tạo DB:

```sh
mysql -u root -pWelcome123
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
exit
```

Tạo user, endpoint:

```sh
openstack user create --domain default --password Welcome123 neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron \
  --description "OpenStack Networking" network
  
openstack endpoint create --region RegionOne \
    network public http://172.16.10.20:9696
openstack endpoint create --region RegionOne \
  network internal http://172.16.10.20:9696
openstack endpoint create --region RegionOne \
  network admin http://172.16.10.20:9696
```

### Cấu hình Neutron

**Trên node CTL1**, cấu hình ```neutron.conf```:

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org
rm -rf /etc/neutron/neutron.conf

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
bind_host = 172.16.10.11
core_plugin = ml2
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
notify_nova_on_port_status_changes = true
notify_nova_on_port_data_changes = true
allow_overlapping_ips = True
dhcp_agents_per_network = 2
service_plugins = neutron.services.qos.qos_plugin.QoSPlugin

[agent]
[cors]
[database]
connection = mysql+pymysql://neutron:Welcome123@172.16.10.20/neutron
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = Welcome123
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình file ml2

```sh
cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.org
rm -rf /etc/neutron/plugins/ml2/ml2_conf.ini

cat << EOF >> /etc/neutron/plugins/ml2/ml2_conf.ini
[DEFAULT]
[l2pop]
[ml2]
type_drivers = flat,vlan,vxlan
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security,qos
[ml2_type_flat]
flat_networks = provider
[ml2_type_geneve]
[ml2_type_gre]
[ml2_type_vlan]
#network_vlan_ranges = provider
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True
EOF
```

Cấu hình LB agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.org 
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini

cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
extensions = qos
[linux_bridge]
physical_interface_mappings = provider:eth1
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.13.11
l2_population = true
EOF
```

Cấu hình L3 agent

```sh
cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.org
rm -rf /etc/neutron/l3_agent.ini

cat << EOF >> /etc/neutron/l3_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
[agent]
[ovs]
EOF
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[neutron]
url = http://172.16.10.20:9696
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
service_metadata_proxy = true
metadata_proxy_shared_secret = Welcome123
```

Restart Nova

```sh
systemctl restart openstack-nova-api openstack-nova-scheduler \
    openstack-nova-consoleauth openstack-nova-conductor \
    openstack-nova-novncproxy
```

Phân quyền

```sh
chown -R root:neutron /etc/neutron/
```

Tạo symlink

```sh
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
```

Sync database

```sh
su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
```

Enable và start dịch vụ

```sh
systemctl enable neutron-server neutron-linuxbridge-agent neutron-l3-agent
systemctl restart neutron-server neutron-linuxbridge-agent neutron-l3-agent

openstack network agent list
```

**Trên node CTL2**, cấu hình ```neutron.conf```

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org
rm -rf /etc/neutron/neutron.conf

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
bind_host = 172.16.10.12
core_plugin = ml2
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
notify_nova_on_port_status_changes = true
notify_nova_on_port_data_changes = true
allow_overlapping_ips = True
dhcp_agents_per_network = 2
service_plugins = neutron.services.qos.qos_plugin.QoSPlugin

[agent]
[cors]
[database]
connection = mysql+pymysql://neutron:Welcome123@172.16.10.20/neutron
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = Welcome123
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình file ml2

```sh
cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.org
rm -rf /etc/neutron/plugins/ml2/ml2_conf.ini

cat << EOF >> /etc/neutron/plugins/ml2/ml2_conf.ini
[DEFAULT]
[l2pop]
[ml2]
type_drivers = flat,vlan,vxlan
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security,qos
[ml2_type_flat]
flat_networks = provider
[ml2_type_geneve]
[ml2_type_gre]
[ml2_type_vlan]
#network_vlan_ranges = provider
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True
EOF
```

Cấu hình file LB agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.org 
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini

cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
extensions = qos
[linux_bridge]
physical_interface_mappings = provider:eth1 
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.13.12
l2_population = true
EOF
```

Cấu hình L3 agent

```sh
cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.org
rm -rf /etc/neutron/l3_agent.ini

cat << EOF >> /etc/neutron/l3_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
[agent]
[ovs]
EOF
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[neutron]
url = http://172.16.10.20:9696
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
service_metadata_proxy = true
metadata_proxy_shared_secret = Welcome123
```

Restart lại service nova

```sh
systemctl restart openstack-nova-api \
openstack-nova-scheduler \
openstack-nova-consoleauth \
openstack-nova-conductor \
openstack-nova-novncproxy
```

Phân quyền

```sh
chown -R root:neutron /etc/neutron/
```

Tạo liên kết

```sh
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
```

Enable và start dịch vụ

```sh
systemctl enable neutron-server neutron-linuxbridge-agent neutron-l3-agent
systemctl restart neutron-server neutron-linuxbridge-agent neutron-l3-agent
```

**Trên node CTL3**, cấu hình ```neutron.conf```

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org
rm -rf /etc/neutron/neutron.conf

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
bind_host = 172.16.10.13
core_plugin = ml2
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
notify_nova_on_port_status_changes = true
notify_nova_on_port_data_changes = true
allow_overlapping_ips = True
dhcp_agents_per_network = 2
service_plugins = neutron.services.qos.qos_plugin.QoSPlugin

[agent]
[cors]
[database]
connection = mysql+pymysql://neutron:Welcome123@172.16.10.20/neutron
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = Welcome123
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình file ml2

```sh
cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.org
rm -rf /etc/neutron/plugins/ml2/ml2_conf.ini

cat << EOF >> /etc/neutron/plugins/ml2/ml2_conf.ini
[DEFAULT]
[l2pop]
[ml2]
type_drivers = flat,vlan,vxlan
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security,qos
[ml2_type_flat]
flat_networks = provider
[ml2_type_geneve]
[ml2_type_gre]
[ml2_type_vlan]
#network_vlan_ranges = provider
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True
EOF
```

Cấu hình file LB agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.org 
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini

cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
extensions = qos
[linux_bridge]
physical_interface_mappings = provider:eth1 
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.13.13
l2_population = true
EOF
```

Cấu hình L3 agent

```sh
cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.org
rm -rf /etc/neutron/l3_agent.ini

cat << EOF >> /etc/neutron/l3_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
[agent]
[ovs]
EOF
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[neutron]
url = http://172.16.10.20:9696
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
service_metadata_proxy = true
metadata_proxy_shared_secret = Welcome123
```

Restart lại service nova

```sh
systemctl restart openstack-nova-api \
openstack-nova-scheduler \
openstack-nova-consoleauth \
openstack-nova-conductor \
openstack-nova-novncproxy
```

Phân quyền

```sh
chown -R root:neutron /etc/neutron/
```

Tạo liên kết

```sh
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
```

Enable và start dịch vụ

```sh
systemctl enable neutron-server neutron-linuxbridge-agent neutron-l3-agent
systemctl restart neutron-server neutron-linuxbridge-agent neutron-l3-agent
```

### Kiểm tra

- Bật Neutron service tại CTL 1, tắt Neutron service trên CTL 2 3, list Neutron service

![](./images/OPS_Install_35.png)

- Bật Neutron service tại CTL 2, tắt Neutron service trên CTL 1 3, list Neutron service

![](./images/OPS_Install_36.png)

- Bật Neutron service tại CTL 3, tắt Neutron service trên CTL 1 2, list Neutron service

![](./images/OPS_Install_37.png)

## Phần 11: Cấu hình Horizon

### Tải package và tạo file redirect

**Thực hiện trên tất cả các node**, tải về các package sau:

```sh
yum install openstack-dashboard -y
```

Tạo file redirect

```sh
filehtml=/var/www/html/index.html
touch $filehtml
cat << EOF >> $filehtml
<html>
<head>
<META HTTP-EQUIV="Refresh" Content="0.5; URL=http://172.16.10.20/dashboard">
</head>
<body>
<center> <h1>Redirecting to OpenStack Dashboard</h1> </center>
</body>
</html>
EOF
```

Phân quyền

```sh
chown root:apache /var/www/html/index.html
```

### Cấu hình Horizon

**Trên node CTL1**, thực hiện:

```sh
cp /etc/openstack-dashboard/local_settings /etc/openstack-dashboard/local_settings.org
```

Tìm và thay đổi các thông số sau trong file ```/etc/openstack-dashboard/local_settings```

```sh
ALLOWED_HOSTS = ['*',]
OPENSTACK_API_VERSIONS = {
    "identity": 3,
    "image": 2,
    "volume": 2,
}
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

### Lưu ý thêm SESSION_ENGINE vào trên dòng CACHE như bên dưới
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
         'LOCATION': ['172.16.10.11:11211','172.16.10.12:11211','172.16.10.13:11211',]
    }
}
OPENSTACK_HOST = "172.16.10.20"
OPENSTACK_KEYSTONE_URL = "http://172.16.10.20:5000/v3"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"

### Lưu ý: Nếu chỉ sử dụng provider, chỉnh sửa các thông số sau
OPENSTACK_NEUTRON_NETWORK = {
    'enable_router': False,
    'enable_quotas': False,
    'enable_ipv6': False,
    'enable_distributed_router': False,
    'enable_ha_router': False,
    'enable_fip_topology_check': False,
}

TIME_ZONE = "Asia/Ho_Chi_Minh"
```

Scp sang 2 node còn lại. Nên backup lại 2 file cấu hình trên 2 node còn lại trước

```sh
scp /etc/openstack-dashboard/local_settings root@ctl2:/etc/openstack-dashboard/
scp /etc/openstack-dashboard/local_settings root@ctl3:/etc/openstack-dashboard/
```

Chỉnh sửa file ```/etc/httpd/conf.d/openstack-dashboard.conf```

```sh
echo "WSGIApplicationGroup %{GLOBAL}" >> /etc/httpd/conf.d/openstack-dashboard.conf
```

Restart dịch vụ

```sh
systemctl restart httpd memcached
```

**Trên node CTL2 và CTL3:**

Kiểm tra các file cấu hình ```/etc/openstack-dashboard/local_settings```, đảm bảo nội dung tương tự như trên CTL1

Phân quyền

```sh
chown root:apache /etc/openstack-dashboard/local_settings
```

Chỉnh sửa file ```/etc/httpd/conf.d/openstack-dashboard.conf```

```sh
echo "WSGIApplicationGroup %{GLOBAL}" >> /etc/httpd/conf.d/openstack-dashboard.conf
```

Restart dịch vụ

```sh
systemctl restart httpd memcached
```

### Kiểm tra

![](./images/OPS_Install_38.png)

## Phần 12: Cấu hình Cinder

### Cài đặt các gói cần thiết

**Trên tất cả các node CTL**, thực hiện:

```sh
yum install openstack-cinder -y
```

### Tạo Database, Endpoint

**Thực hiện trên node CTL1:**

Tạo databases

```sh
mysql -u root -pWelcome123
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'Welcome123';  
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'ctl1' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'ctl2' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'ctl3' IDENTIFIED BY 'Welcome123';FLUSH PRIVILEGES;
exit
```

Tạo endpoint

```sh
openstack user create --domain default --password Welcome123 cinder
openstack role add --project service --user cinder admin
openstack service create --name cinderv2 \
  --description "OpenStack Block Storage" volumev2
  
openstack service create --name cinderv3 \
  --description "OpenStack Block Storage" volumev3
  
openstack endpoint create --region RegionOne \
  volumev2 public http://172.16.10.20:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne \
  volumev2 internal http://172.16.10.20:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne \
  volumev2 admin http://172.16.10.20:8776/v2/%\(project_id\)s
openstack endpoint create --region RegionOne \
  volumev3 public http://172.16.10.20:8776/v3/%\(project_id\)s
openstack endpoint create --region RegionOne \
  volumev3 internal http://172.16.10.20:8776/v3/%\(project_id\)s
openstack endpoint create --region RegionOne \
  volumev3 admin http://172.16.10.20:8776/v3/%\(project_id\)s
```

### Cấu hình Cinder

**Trên node CTL1:**

```sh
cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak 
rm -rf /etc/cinder/cinder.conf

cat << EOF >> /etc/cinder/cinder.conf
[DEFAULT]
my_ip = 172.16.10.11
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
osapi_volume_listen = 172.16.10.11
[backend]
[backend_defaults]
[barbican]
[brcd_fabric_example]
[cisco_fabric_example]
[coordination]
[cors]
[database]
connection = mysql+pymysql://cinder:Welcome123@172.16.10.20/cinder
[fc-zone-manager]
[healthcheck]
[key_manager]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_id = default
user_domain_id = default
project_name = service
username = cinder
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[oslo_reports]
[oslo_versionedobjects]
[profiler]
[service_user]
[ssl]
[vault]
EOF
```

Phân quyền

```sh
chown root:cinder /etc/cinder/cinder.conf
```

Sync db

```sh
su -s /bin/sh -c "cinder-manage db sync" cinder
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[cinder]
os_region_name = RegionOne
```

Restart lại dịch vụ nova API

```sh
systemctl restart openstack-nova-api
```

Enable và Start dịch vụ

```sh
systemctl enable openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler --now
```

Kiểm tra:

```sh
openstack volume service list
```

![](./images/OPS_Install_39.png)

**Trên node CTL2:**

```sh
cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak 
rm -rf /etc/cinder/cinder.conf

cat << EOF >> /etc/cinder/cinder.conf
[DEFAULT]
my_ip = 172.16.10.12
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
osapi_volume_listen = 172.16.10.12
[backend]
[backend_defaults]
[barbican]
[brcd_fabric_example]
[cisco_fabric_example]
[coordination]
[cors]
[database]
connection = mysql+pymysql://cinder:Welcome123@172.16.10.20/cinder
[fc-zone-manager]
[healthcheck]
[key_manager]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_id = default
user_domain_id = default
project_name = service
username = cinder
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[oslo_reports]
[oslo_versionedobjects]
[profiler]
[service_user]
[ssl]
[vault]
EOF
```

Phân quyền

```sh
chown root:cinder /etc/cinder/cinder.conf
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[cinder]
os_region_name = RegionOne
```

Restart lại dịch vụ nova api

```sh
systemctl restart openstack-nova-api
```

Enable và start dịch vụ

```sh
systemctl enable openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler --now
```

**Trên node CTL3:**

```sh
cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak 
rm -rf /etc/cinder/cinder.conf

cat << EOF >> /etc/cinder/cinder.conf
[DEFAULT]
my_ip = 172.16.10.13
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
osapi_volume_listen = 172.16.10.13
[backend]
[backend_defaults]
[barbican]
[brcd_fabric_example]
[cisco_fabric_example]
[coordination]
[cors]
[database]
connection = mysql+pymysql://cinder:Welcome123@172.16.10.20/cinder
[fc-zone-manager]
[healthcheck]
[key_manager]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_id = default
user_domain_id = default
project_name = service
username = cinder
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/cinder/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues = true
rabbit_ha_queues = true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[oslo_reports]
[oslo_versionedobjects]
[profiler]
[service_user]
[ssl]
[vault]
EOF
```

Phân quyền

```sh
chown root:cinder /etc/cinder/cinder.conf
```

Chỉnh sửa file ```/etc/nova/nova.conf```

```sh
[cinder]
os_region_name = RegionOne
```

Restart lại dịch vụ nova api

```sh
systemctl restart openstack-nova-api
```

Enable và start dịch vụ

```sh
systemctl enable openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler --now
```

Kiểm tra

![](./images/OPS_Install_40.png)

## Phần 13: Cài đặt node COM

**Phần này chỉ làm demo trên 1 node COM, nếu cần nhiều hơn thì thay đổi cho phù hợp**

### Chuẩn bị

Set hostname, network, tắt selinux, firewall.

Đồng bộ thời gian:

```sh
yum -y install chrony
VIP_MGNT_IP='172.16.10.10'
sed -i '/server/d' /etc/chrony.conf
echo "server $VIP_MGNT_IP iburst" >> /etc/chrony.conf
systemctl enable chronyd.service
systemctl restart chronyd.service
chronyc sources
```

Chuẩn bị sysctl

```sh
echo 'net.ipv4.conf.all.arp_ignore = 1'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.arp_announce = 2'  >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.rp_filter = 2'  >> /etc/sysctl.conf
echo 'net.netfilter.nf_conntrack_tcp_be_liberal = 1'  >> /etc/sysctl.conf

cat << EOF >> /etc/sysctl.conf
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.tcp_keepalive_time = 6
net.ipv4.tcp_keepalive_intvl = 3
net.ipv4.tcp_keepalive_probes = 6
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.default.rp_filter = 0
EOF

modprobe ip_conntrack

sysctl -p
```

Chỉnh sửa file hosts (tất cả file hosts của tất cả node trong cụm):

```sh
172.16.10.11 ctl1
172.16.10.12 ctl2
172.16.10.13 ctl3
172.16.10.14 com1
172.16.10.15 com2
172.16.12.19 cephaio
```

### Cài đặt các gói cần thiết

```sh
yum -y install centos-release-openstack-queens
yum -y install crudini wget vim
yum -y install python-openstackclient openstack-selinux python2-PyMySQL
```

### Cài đặt Nova

Cài đặt các gói cần thiết

```sh
yum install openstack-nova-compute libvirt-client -y
```

Cấu hình Nova

```sh
cp /etc/nova/nova.conf  /etc/nova/nova.conf.org
rm -rf /etc/nova/nova.conf

cat << EOF >> /etc/nova/nova.conf 
[DEFAULT]
enabled_apis = osapi_compute,metadata
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
my_ip = 172.16.10.15
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
[api]
auth_strategy = keystone
[api_database]
[barbican]
[cache]
[cells]
[cinder]
[compute]
[conductor]
[console]
[consoleauth]
[cors]
[crypto]
[database]
[devices]
[ephemeral_storage_encryption]
[filter_scheduler]
[glance]
api_servers = http://172.16.10.20:9292
[guestfs]
[healthcheck]
[hyperv]
[ironic]
[key_manager]
[keystone]
[keystone_authtoken]
auth_url = http://172.16.10.20:5000/v3
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = Welcome123
[libvirt]
virt_type = qemu
[matchmaker_redis]
[metrics]
[mks]
[neutron]
[notifications]
[osapi_v21]
[oslo_concurrency]
lock_path = /var/lib/nova/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[pci]
[placement]
os_region_name = RegionOne
project_domain_name = Default
project_name = service
auth_type = password
user_domain_name = Default
auth_url = http://172.16.10.20:5000/v3
username = placement
password = Welcome123
[quota]
[rdp]
[remote_debug]
[scheduler]
[serial_console]
[service_user]
[spice]
[upgrade_levels]
[vault]
[vendordata_dynamic_auth]
[vmware]
[vnc]
enabled = True
server_listen = 0.0.0.0
server_proxyclient_address = 172.16.10.15
novncproxy_base_url = http://172.16.10.20:6080/vnc_auto.html
[workarounds]
[wsgi]
[xenserver]
[xvp]
EOF
```

Phần quyền

```sh
chown root:nova /etc/nova/nova.conf
```

Khởi động dịch vụ

```sh
systemctl enable libvirtd openstack-nova-compute
systemctl restart libvirtd openstack-nova-compute
```

Kiểm tra (trên node CTL)

```sh
openstack compute service list
```

![](./images/OPS_Install_41.png)

### Cài đặt Neutron

Cài đặt gói

```sh
yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y
```

Cấu hình Neutron

```sh
cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org 
rm -rf /etc/neutron/neutron.conf

cat << EOF >> /etc/neutron/neutron.conf
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@172.16.10.11:5672,openstack:Welcome123@172.16.10.12:5672,openstack:Welcome123@172.16.10.13:5672
auth_strategy = keystone
[agent]
[cors]
[database]
[keystone_authtoken]
auth_uri = http://172.16.10.20:5000
auth_url = http://172.16.10.20:35357
memcached_servers = 172.16.10.11:11211,172.16.10.12:11211,172.16.10.13:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = Welcome123
[matchmaker_redis]
[nova]
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[oslo_messaging_amqp]
[oslo_messaging_kafka]
[oslo_messaging_notifications]
[oslo_messaging_rabbit]
rabbit_ha_queues = true
rabbit_retry_interval = 1
rabbit_retry_backoff = 2
amqp_durable_queues= true
[oslo_messaging_zmq]
[oslo_middleware]
[oslo_policy]
[quotas]
[ssl]
EOF
```

Cấu hình LB Agent

```sh
cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.org 
rm -rf /etc/neutron/plugins/ml2/linuxbridge_agent.ini

cat << EOF >> /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[DEFAULT]
[agent]
extensions = qos
[linux_bridge]
physical_interface_mappings = provider:eth1 
[network_log]
[securitygroup]
enable_security_group = true
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
[vxlan]
enable_vxlan = true
local_ip = 172.16.13.14
l2_population = true
EOF
```

Cấu hình DHCP Agent

```sh
cp /etc/neutron/dhcp_agent.ini /etc/neutron/dhcp_agent.ini.org
rm -rf /etc/neutron/dhcp_agent.ini

cat << EOF >> /etc/neutron/dhcp_agent.ini
[DEFAULT]
interface_driver = linuxbridge
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = true
force_metadata = True
[agent]
[ovs]
EOF
```

Cấu hình metadata agennt

```sh
cp /etc/neutron/metadata_agent.ini /etc/neutron/metadata_agent.ini.org 
rm -rf /etc/neutron/metadata_agent.ini

cat << EOF >> /etc/neutron/metadata_agent.ini
[DEFAULT]
nova_metadata_host = 172.16.10.20
metadata_proxy_shared_secret = Welcome123
[agent]
[cache]
EOF
```

Thêm vào file ```/etc/nova/nova.conf```

```sh
[neutron]
url = http://172.16.10.20:9696
auth_url = http://172.16.10.20:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = Welcome123
```

Phân quyền

```sh
chown root:neutron /etc/neutron/metadata_agent.ini /etc/neutron/neutron.conf /etc/neutron/dhcp_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini
```

Khởi động lại dịch vụ

```sh
systemctl restart libvirtd openstack-nova-compute
systemctl enable neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent
systemctl restart neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent
```

Kiểm tra:

```sh
openstack network agent list
```

![](./images/OPS_Install_42.png)

## Phần 14: Tích hợp OPS HA với CEPH

### Chuẩn bị

Cài đặt các gói bổ sung trên **toàn bộ node CTL và COM**

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

```sh
yum install epel-release -y 
yum install python-rbd -y
yum install ceph-common -y
```

### Tạo pool trên CEPH

**Thực hiện trên node cephaio**

```sh
ceph osd pool create volumes 64 64
ceph osd pool create vms 16 16
ceph osd pool create images 8 8
ceph osd pool create backups 32 32

rbd pool init volumes
rbd pool init vms
rbd pool init images
rbd pool init backups
```

Copy cấu hình sang các node CTL và COM

```sh
ssh ctl1 sudo tee /etc/ceph/ceph.conf < /etc/ceph/ceph.conf
ssh ctl2 sudo tee /etc/ceph/ceph.conf < /etc/ceph/ceph.conf
ssh ctl3 sudo tee /etc/ceph/ceph.conf < /etc/ceph/ceph.conf

ssh com1 sudo tee /etc/ceph/ceph.conf < /etc/ceph/ceph.conf
ssh com2 sudo tee /etc/ceph/ceph.conf < /etc/ceph/ceph.conf
```

### Cấu hình CEPH làm backend cho Glance-images

**Trên node CEPH**, tiến hành tạo key Glance

```sh
cd /ceph-deploy

ceph auth get-or-create client.glance mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=images' > ceph.client.glance.keyring
```

Chuyển key sang 3 node CTL

```sh
ceph auth get-or-create client.glance | ssh ctl1 sudo tee /etc/ceph/ceph.client.glance.keyring
ceph auth get-or-create client.glance | ssh ctl2 sudo tee /etc/ceph/ceph.client.glance.keyring
ceph auth get-or-create client.glance | ssh ctl3 sudo tee /etc/ceph/ceph.client.glance.keyring
```

**Trên cả 3 node CTL**, thực hiện:

```sh
systemctl stop openstack-glance-api openstack-glance-registry
```

Phân quyền

```sh
chown glance:glance /etc/ceph/ceph.client.glance.keyring
chmod 0640 /etc/ceph/ceph.client.glance.keyring
```

Thêm cấu hình ```/etc/glance/glance-api.conf```

```sh
[DEFAULT]
show_image_direct_url = True
...

[glance_store]
#stores = file,http
#default_store = file
#filesystem_store_datadir = /var/lib/glance/images/
default_store = rbd
stores = file,http,rbd
rbd_store_pool = images
rbd_store_user = glance
rbd_store_ceph_conf = /etc/ceph/ceph.conf
rbd_store_chunk_size = 8
```

Start lại dịch vụ Glance

```sh
systemctl start openstack-glance-api openstack-glance-registry
```

Tạo thử image:

```sh
openstack image create "cirros-ceph-ctl1" \
  --file cirros-0.3.5-x86_64-disk.img \
  --disk-format qcow2 --container-format bare \
  --public
```

![](./images/OPS_Install_43.png)

Kiểm tra trên node CEPH

```sh
rbd -p images ls
```

![](./images/OPS_Install_44.png)

### Cấu hình CEPH làm backend cho Cinder-volume, Cinder-backup

**Thực hiện trên node cephaio**, tạo key cinder và cinder-backup

```sh
cd /home/ceph-deploy
ceph auth get-or-create client.cinder mon 'allow r, allow command "osd blacklist", allow command "blacklistop"' osd 'allow class-read object_prefix rbd_children, allow rwx pool=volumes, allow rwx pool=images' > ceph.client.cinder.keyring
ceph auth get-or-create client.cinder-backup mon 'profile rbd' osd 'profile rbd pool=backups' > ceph.client.cinder-backup.keyring
```

Chuyển key cinder và key cinder-backup sang các node CTL

```sh
ceph auth get-or-create client.cinder | ssh ctl1 sudo tee /etc/ceph/ceph.client.cinder.keyring
ceph auth get-or-create client.cinder-backup | ssh ctl1 sudo tee /etc/ceph/ceph.client.cinder-backup.keyring

ceph auth get-or-create client.cinder | ssh ctl2 sudo tee /etc/ceph/ceph.client.cinder.keyring
ceph auth get-or-create client.cinder-backup | ssh ctl2 sudo tee /etc/ceph/ceph.client.cinder-backup.keyring

ceph auth get-or-create client.cinder | ssh ctl3 sudo tee /etc/ceph/ceph.client.cinder.keyring
ceph auth get-or-create client.cinder-backup | ssh ctl3 sudo tee /etc/ceph/ceph.client.cinder-backup.keyring
```

Chuyển key cinder tới các node COM

```sh
ceph auth get-or-create client.cinder | ssh com1 sudo tee /etc/ceph/ceph.client.cinder.keyring
ceph auth get-key client.cinder | ssh com1 tee /root/client.cinder

ceph auth get-or-create client.cinder | ssh com2 sudo tee /etc/ceph/ceph.client.cinder.keyring
ceph auth get-key client.cinder | ssh com2 tee /root/client.cinder
```

**Trên cả 3 node CTL**, dừng dịch vụ Cinder

```sh
systemctl stop openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler
```

Khởi tạo 1 UUID mới cho Cinder

```sh
uuidgen

45e31181-6723-419b-8eb1-68e619e301d9
```

**Lưu ý:** UUID sử dụng cho tất cả các node COM nên chỉ tạo 1 lần đầu tiên

Phân quyền

```sh
sudo chown cinder:cinder /etc/ceph/ceph.client.cinder*
sudo chmod 0640 /etc/ceph/ceph.client.cinder*
```

Bổ sung thêm cấu hình ```/etc/cinder/cinder.conf``` trên node controller

```sh
[DEFAULT]
....
## Thêm các giá trị này
notification_driver = messagingv2
enabled_backends = ceph
glance_api_version = 2
backup_driver = cinder.backup.drivers.ceph
backup_ceph_conf = /etc/ceph/ceph.conf
backup_ceph_user = cinder-backup
backup_ceph_chunk_size = 134217728
backup_ceph_pool = backups
backup_ceph_stripe_unit = 0
backup_ceph_stripe_count = 0
restore_discard_excess_bytes = true
host=ceph

## Bổ sung section ceph
[ceph]
volume_driver = cinder.volume.drivers.rbd.RBDDriver
volume_backend_name = ceph
rbd_pool = volumes
rbd_ceph_conf = /etc/ceph/ceph.conf
rbd_flatten_volume_from_snapshot = false
rbd_max_clone_depth = 5
rbd_store_chunk_size = 4
rados_connect_timeout = -1
rbd_user = cinder
rbd_secret_uuid = 45e31181-6723-419b-8eb1-68e619e301d9
report_discard_supported = true
```

Restart lại dịch vụ

```sh
systemctl restart openstack-cinder-api openstack-cinder-volume openstack-cinder-scheduler
```

Kiểm tra

```sh
openstack volume service list
```

![](./images/OPS_Install_45.png)

**Chỉ thực hiện trên 1 node CTL bất kỳ:**

Tạo mới cinder type ceph

```sh
cinder type-create ceph
cinder type-key ceph set volume_backend_name=ceph
```

**Thực hiện trên các node COM**

Tạo file XML cho phép CEPH RBD xác thực với libvirt thông qua UUID vừa tạo

```sh
cat > ceph-secret.xml <<EOF
<secret ephemeral='no' private='no'>
<uuid>45e31181-6723-419b-8eb1-68e619e301d9</uuid>
<usage type='ceph'>
	<name>client.cinder secret</name>
</usage>
</secret>
EOF

sudo virsh secret-define --file ceph-secret.xml
```

![](./images/OPS_Install_46.png)

Gán giá trị của ```client.cinder``` cho ```uuid```

```sh
virsh secret-set-value --secret 45e31181-6723-419b-8eb1-68e619e301d9 --base64 $(cat /root/client.cinder)
```

Khởi động lại dịch vụ

```sh
systemctl restart openstack-nova-compute
```

### Cấu hình CEPH làm backend cho Nova-compute

**Trên node cephaio**

Tạo key cho nova:

```sh
cd /home/ceph-deploy

ceph auth get-or-create client.nova mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=vms, allow rx pool=images' -o /etc/ceph/ceph.client.nova.keyring
```

Copy sang các node COM

```sh
ceph auth get-or-create client.nova | ssh com1 sudo tee /etc/ceph/ceph.client.nova.keyring
ceph auth get-key client.nova | ssh com1 tee /root/client.nova

ceph auth get-or-create client.nova | ssh com2 sudo tee /etc/ceph/ceph.client.nova.keyring
ceph auth get-key client.nova | ssh com2 tee /root/client.nova
```

**Thực hiện trên các node COM**

Phân quyền

```sh
chgrp nova /etc/ceph/ceph.client.nova.keyring
chmod 0640 /etc/ceph/ceph.client.nova.keyring
```

Tạo file XML cho CEPH kết nối Compute

```sh
cat << EOF > nova-ceph.xml
<secret ephemeral="no" private="no">
<uuid>4c4b43c6-e895-4e6e-95dc-06155834ee03</uuid>
<usage type="ceph">
<name>client.nova secret</name>
</usage>
</secret>
EOF

virsh secret-define --file nova-ceph.xml

virsh secret-set-value --secret 4c4b43c6-e895-4e6e-95dc-06155834ee03 --base64 $(cat /root/client.nova)
```

Chỉnh sửa file ```/etc/nova/nova.conf``` tại COM

```sh
[libvirt]
...
images_rbd_pool=vms
images_type=rbd
rbd_secret_uuid=4c4b43c6-e895-4e6e-95dc-06155834ee03
rbd_user=nova
images_rbd_ceph_conf = /etc/ceph/ceph.conf
```

Restart service

```sh
systemctl restart openstack-nova-compute 
```