# Triển khai HAProxy Pacemaker cho Cluster Galera 3 node trên CentOS 7

## Chuẩn bị

Server có cấu hình và IP như sau:

|Hostname|Hardware|Interface|
|:-|:-|:-|
|node1|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.153 - private: 192.168.60.153|
|node2|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.154 - private: 192.168.60.154|
|node3|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.155 - private: 192.168.60.155|

Mô hình

![](./images/Cluster_model_lab.png)

![](./images/Cluster_model_service.png)

## Thiết lập Galera trên 3 node CentOS 7

### Thiết lập ban đầu

Trên cả 3 node, cấu hình như sau:

Tắt firewall, SELinux, khởi động lại

```sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
systemctl stop firewalld
systemctl disable firewalld
init 6
```

Cấu hình host

```sh
echo "172.16.7.153 node7153" >> /etc/hosts
echo "172.16.7.154 node7154" >> /etc/hosts
echo "172.16.7.155 node7155" >> /etc/hosts
```

### Cài đặt MariaDB 10.10

Các bước sau cũng thực hiện trên tất cả các node

Khai báo repo

```sh
echo '[mariadb]
name = MariaDB
baseurl = http://mirror.mariadb.org/yum/10.10/centos7-amd64/
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1' >> /etc/yum.repos.d/MariaDB.repo
yum install -y epel-release
yum -y update
```

Cài đặt MariaDB

```sh
yum install -y mariadb mariadb-server
```

Cài đặt Galera và các gói hỗ trợ

```sh
yum install -y galera rsync
```

Tắt MariaDB (do liên quan tới cấu hình Galera MariaDB)

```sh
systemctl stop mariadb
```

![](./images/Cluster_Galera_Mariadb.png)

### Cấu hình Galera Cluster

Cấu hình như sau (lưu ý sửa đổi phù hợp với từng node)

```sh
cp /etc/my.cnf.d/server.cnf /etc/my.cnf.d/server.cnf.bak

echo '[server]
[mysqld]
bind-address=172.16.7.153

[galera]
wsrep_on=ON
wsrep_provider=/usr/lib64/galera/libgalera_smm.so
#add your node private ips here
wsrep_cluster_address="gcomm://192.168.60.153,192.168.60.154,192.168.60.155"
binlog_format=row
default_storage_engine=InnoDB
innodb_autoinc_lock_mode=2
#Cluster name
wsrep_cluster_name="portal_cluster"
# Allow server to accept connections on all interfaces.
bind-address=172.16.7.153
# this server private ip, change for each server
wsrep_node_address="192.168.60.153"
# this server name, change for each server
wsrep_node_name="node7153"
wsrep_sst_method=rsync
[embedded]
[mariadb]
[mariadb-10.2]
' > /etc/my.cnf.d/server.cnf
```

Trong đó:
- ```wsrep_cluster_address```: Danh sách các node thuộc Cluster, sử dụng địa chỉ IP Replicate (trong bài lab, dải IP Replicate sẽ là 192.168.60.0/24)
- ```wsrep_cluster_name```: Tên của Cluster
- ```wsrep_node_address```: Địa chỉ IP của node đang thực hiện
- ```wsrep_node_name```: Tên node (giống với hostname)
- **Lưu ý:** Không bật MariaDB !!!

### Khởi động dịch vụ

Tại ```node1``` khởi tạo cluster

```sh
galera_new_cluster
systemctl start mariadb
systemctl enable mariadb
```

**Lưu ý:** Từ bản Mariadb 10.4 trở lên thì phải tạo symlink như sau rồi mới khởi tạo cluster:

```sh
ln -s /usr/lib64/galera-4 /usr/lib64/galera
```

Tại 2 node còn lại chạy dịch vụ mariadb (nếu sử dụng Mariadb 10.4 trở lên thì cũng phải tạo symlink như trên)

```sh
systemctl enable mariadb --now
```

### Kiểm tra tại node1

```sh
mysql -u root -e "SHOW STATUS LIKE 'wsrep_cluster_size'"
```

![](./images/Cluster_check_size.png)

