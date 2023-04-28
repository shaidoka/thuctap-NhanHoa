# Persistent storage sử dụng iSCSI

iSCSI-targetd provisioner là 1 provisioner (không được cung cấp chính thức bởi K8s) cho iSCSI storage trên K8s (hoặc OpenShift). Provisioner này sẽ sử dụng API cung cấp bởi targetd để tạo và export iSCSI storage trên 1 remote server.

## Prerequisites

iSCSI-targetd provisioner cần những yếu tố sau đây:
- 1 iSCSI server quản lý bởi ```targetd```
- Mọi node trong K8s/Openshift phải giao tiếp được với iSCSI server
- Dung lượng ổ đĩa khả dụng dưới dạng LVM2 volume group

## Cách thức hoạt động

Khi 1 yêu cầu PVC được đưa ra cho iSCSI provisioner controlled storageclass (SC), những việc sau sẽ xảy ra:
- 1 volume mới trong volume group cấu hình từ trước sẽ được tạo ra, kích thước của volume tùy thuộc vào kích thước yêu cầu trong PVC
- Volume này sau đó được export ra LUN (logical unit number) đầu tiên khả dụng và có thể truy cập bởi tất cả initiator được cấu hình.
- Sau đó, PV liên quan sẽ được tự động tạo và bound đến PVC

Mỗi storage class được liên kết với 1 iSCSI target và 1 volume group (vg). Vì 1 target có thể quản lý tối đa 255 LUN, mỗi storage class cũng theo đó quản lý nhiều nhất 255 PVS. iSCSI-targetd provisioner có thể quản lý nhiều storage class

## Cài đặt prerequisites

**Lưu ý:** iSCSI Qualified Names (IQNs) cần được tạo và phải duy nhất. Vì vậy mọi target phải có IQN độc nhất của nó, và mọi client (initiator) cũng vậy.

IQNs có dạng: ```iqn.YEAR-MM.com.example.blah:tag```

### 1. Thiết lập Storage

Trước khi đi vào cấu hình iSCSI server, nó cần phải cấu hình storage trước. ```targetd``` sử dụng LVM để cung cấp storage.

Nếu có thể, ta nên có 1 ổ đĩa riêng biệt hoặc phân vùng mà có thể cấu hình thành 1 volume group. Tuy nhiên, nếu không thể (hoặc trong môi trường lab), 1 loopback device cũng có thể sử dụng để giả lập 1 ổ đĩa tách rời.

**Tạo Volume Group với 1 ổ đĩa rời hoặc 1 phân vùng**

```sh
yum install lvm2
fdisk /dev/vdc
mkfs.ext4 /dev/vdc1
pvcreate /dev/vdc1
```

### 2. Thiết lập iSCSI server

**Cài đặt targetd và targetcli**

Trên thực tế ta chỉ cần cài đặt ```targetd```. Tuy nhiên, ta nên cài thêm ```targetcli``` để có 1 UI đơn giản sử dụng cho việc kiểm tra trạng thái của iSCSI system (iSCSI trong bài này sử dụng CentOS 7)

```sh
yum install -y targetd targetcli
```

Khởi động ```target.service```

```sh
systemctl enable target --now
```

**Thiết lập targetd**

Đầu tiên, chỉnh sửa file ```/etc/target/targetd.yaml```. Ví dụ

```sh
# No default password, please pick a good one.

password: helloworld

# defaults below; uncomment and edit
block_pools: [vg-targetd] # just 1 by default, but can be more
#fs_pools: []  # Path to btrfs FS, eg. /my_btrfs_mount
user: admin
target_name: iqn.2023-04.org.linux.test:targetd

# log level (debug, info, warning, error, critical)
log_level: debug

ssl: false
# if ssl is activated:
#ssl_cert: /etc/target/targetd_cert.pem
#ssl_key: /etc/target/targetd_key.pem
```

Khởi động targetd service

```sh
systemctl enable targetd --now
```

Thiết lập firewall (hoặc tắt đi)

```sh
firewall-cmd --add-service=iscsi-target --permanent
firewall-cmd --add-port=18700/tcp --permanent 
firewall-cmd --reload
```

**Thiết lập iSCSI server**

Cài đặt các gói cần thiết

```sh
yum install iscsi-initiator-utils iscsi-target-utils -y
```

Sửa Initiator name:

```sh
cat << EOF > /etc/iscsi/initiatorname.iscsi
InitiatorName=iqn.2023-04.org.linux.test:targetd
```

Khởi động iscsid và tgtd

```sh
systemctl start iscsid tgtd
systemctl enable iscsid tgtd
```

Tạo target

```sh
targetcli
/iscsi create iqn.2023-04.org.linux.test:targetd
```

Tạo block backstore

```sh
cd /backstores/block
create dev=/dev/vdc1 name=vdc1
```

Tạo LUN kết nối tới VG

```sh
cd /iscsi/iqn.2023-04.org.linux.test:targetd/tpg1/luns
create /backstores/block/vdc1
exit
```

Restart target service

```sh
systemctl restart target
```

Mở firewall (hoặc tắt firewall)

```sh
firewall-cmd --add-port=3260/tcp --permanent
firewall-cmd --reload

### 3. Thiết lập các node (iscsi clients)

**Cài đặt iscsi-initiator-utils package**

Lệnh ```iscsiadm``` là cần thiết ở tất cả client. Lệnh này được cung cấp trong gói ```iscsi-initiator-utils``` và có thể là 1 phần của hệ thống RHEL/CentOS/Fedora ngay từ khi cài đặt.

```sh
# CentOS
yum install -y iscsi-initiator-utils
# Ubuntu
apt-get install -y open-iscsi
```

**Thiết lập Initiator Name**

Mỗi node cần 1 tên initiator độc nhất. Sử dụng tên trùng lặp có thể dẫn đến vấn đề về hiệu suất và mất mát dữ liệu

Mặc định, 1 tên initiator ngẫu nhiên sẽ được sinh ra khi ```iscsi-initiator-utils``` được cài đặt. Tên này thông thường đã độc nhất rồi, nhưng để chắc chắn thì ta nên kiểm tra lại. Để thiết lập 1 tên initiator mặc định, sửa file ```/etc/iscsi/initiatorname.iscsi```

```sh
InitiatorName=iqn.2023-04.org.debian:01:master1
```

Sau khi thay đổi, ta restart ```iscsid.service```

```sh
systemctl restart iscsid
```

Discovery và login vào target

```sh
iscsiadm -m discovery -t st -p 103.124.93.116
iscsiadm --mode node --targetname iqn.2023-04.org.linux.test:targetd --login
```

### 4. Cài đặt iscsi provisioner pod trong Kubernetes

Chạy lệnh sau. Secret liên quan đến username và password là thông tin ta sử dụng cho targetd đã khai báo bên trên. Những lệnh ở sau sẽ cài đặt iSCSI-targetd provisioner trong Default namespace

```sh
kubectl create secret generic targetd-account --from-literal=username=admin --from-literal=password=helloworld
kubectl apply -f https://raw.githubusercontent.com/kubernetes-incubator/external-storage/master/iscsi/targetd/kubernetes/iscsi-provisioner-d.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-incubator/external-storage/master/iscsi/targetd/kubernetes/iscsi-provisioner-pvc.yaml
```

Tuy nhiên có thể các file trên đã được tác giả viết từ lâu và nó có thể outdate với phiên bản hiện tại, nội dung của 2 file đó nên là như sau:

iscsi-provisioner-d.yaml

```sh
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: iscsi-provisioner-runner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "create", "update", "patch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-iscsi-provisioner
subjects:
  - kind: ServiceAccount
    name: iscsi-provisioner
    namespace: default
roleRef:
  kind: ClusterRole
  name: iscsi-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: iscsi-provisioner
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: iscsi-provisioner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: iscsi-provisioner
  template:
    metadata:
      labels:
        app: iscsi-provisioner
    spec:
      containers:
        - name: iscsi-provisioner
          imagePullPolicy: Always
          image: quay.io/external_storage/iscsi-controller:latest
          args:
            - "start"
          env:
            - name: PROVISIONER_NAME
              value: iscsi-targetd
            - name: LOG_LEVEL
              value: debug
            - name: TARGETD_USERNAME
              valueFrom:
                secretKeyRef:
                  name: targetd-account
                  key: username
            - name: TARGETD_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: targetd-account
                  key: password
            - name: TARGETD_ADDRESS
              value: 103.124.93.116
      serviceAccount: iscsi-provisioner
```

iscsi-provisioner-pvc.yaml

```sh
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: iscsi-pvc-test
  annotations:
    volume.beta.kubernetes.io/storage-class: "iscsi-targetd-vg-targetd"
spec:
  storageClassName: iscsi-targetd-vg-targetd
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
```

*Tùy chọn:* Hoặc ta cũng có thể start 1 provisioner như là 1 container bằng lệnh sau

```sh
docker run -it -v /root/.kube:/kube -v /var/run/kubernetes:/var/run/kubernetes --privileged --net=host quay.io/external_storage/iscsi-controller:latest start --kubeconfig=/kube/config --master=http://127.0.0.1:8080 --log-level=debug --targetd-address=103.124.92.116 --target-password=helloworld --targetd-username=admin
```

### 5. Tạo 1 storage class

File cấu hình storage class có thể như sau:

```sh
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: iscsi-targetd-vg-targetd
provisioner: iscsi-targetd
parameters:
  targetPortal: 103.124.93.116:3260
  # Nếu có nhiều hơn 1 iscsi server thì khai báo ở dưới đây
  # portals: 103.124.93.117:3260, 103.124.93.118:3260
  iqn : iqn.2023-04.org.linux.test:targetd
  volumeGroup: vg-targetd
  initiators: iqn.2023-04.org.debian:01:worker1, iqn.2023-04.org.debian:01:worker2, iqn.2023-04.org.debian:01:worker3
  chapAuthDiscovery: "true"
  chapAuthSession: "true"
  fsType: ext4
  readonly: false
```

```sh
kubectl apply -f iscsi-provisioner-storage-class.yaml
```

Tạo pod để test

```sh
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: iscsi-pvc-pod
  name: iscsi-pv-pod1
spec:
  containers:
  - name: iscsi-pv-busybox
    image: busybox
    command: ["sleep", "60000"]
    volumeMounts:
    - name: iscsi-vol1
      mountPath: /var/lib/busybox
      readOnly: false
  volumes:
  - name: iscsi-vol1
    persistentVolumeClaim:
      claimName: iscsi-pvc-test
```