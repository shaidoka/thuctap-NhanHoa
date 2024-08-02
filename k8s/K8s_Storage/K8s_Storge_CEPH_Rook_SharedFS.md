# Create shared file systems with Ceph Rook

## Create the filesystem

Tạo filesystem bằng cách chỉ định cấu hình mong muốn cho metadata pool, data pool, và metadata server trong ```CephFilesystem``` CRD. Trong ví dụ này, chúng ta tạo metadata pool với 3 replication và 1 data pool cũng với 3 replication.

Lưu định nghĩa shared filesystem sau vào ```filesystem.yaml```

```sh
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: myfs
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 3
  dataPools:
    - name: replicated
      replicated:
        size: 3
  preserveFilesystemOnDelete: true
  metadataServer:
    activeCount: 1
    activeStandby: true
```

Áp dụng file trên và rook operator sẽ tạo tất cả các pools và các tài nguyên cần thiết khác để khởi động dịch vụ. Điều này sẽ mất vài phút để hoàn thành.

```sh
kubectl apply -f filesystem.yaml
```

Bạn có thể kiểm tra lại với lệnh sau:

```sh
kubectl -n rook-ceph get pod -l app=rook-ceph-mds
```

Để xem chi tiết trạng thái của filesystem, khởi động và kết nối đến Rook toolbox. Sau đó sử dụng lệnh ```ceph status``` và tìm kiếm dòng ```mds``` service. Như ở ví dụ dưới đây, chúng ta có 1 MDS đang active và 1 MDS đang standby-replay trong trường hợp cần failover

## Provision Storage

Trước khi Rook có thể bắt đầu cung cấp storage, 1 StorageClass cần được tạo dựa trên filesystem. Điều này là cần thiết cho K8s để tương tác với CSI driver để tạo PV.

Lưu storage class này vào ```storageclass.yaml```

```sh
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
# Change "rook-ceph" provisioner prefix to match the operator namespace if needed
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  # clusterID is the namespace where the rook cluster is running
  # If you change this namespace, also change the namespace below where the secret namespaces are defined
  clusterID: rook-ceph

  # CephFS filesystem name into which the volume shall be created
  fsName: myfs

  # Ceph pool into which the volume shall be created
  # Required for provisionVolume: "true"
  pool: myfs-replicated

  # The secrets contain Ceph admin credentials. These are generated automatically by the operator
  # in the same namespace as the cluster.
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph

reclaimPolicy: Delete
```

Nếu bạn đã triển khai Rook operator trong 1 namespace khác với ```rook-ceph```, hãy thay đổi tham số ```provisioner``` để phù hợp với triển khai của bạn.

Áp dụng storage class này:

```sh
kubectl apply -f csi/cephfs/storageclass.yaml
```

## Quotas

*Lưu ý rằng Cephfs CSI driver sử dụng quotas để đảm bảo PVC size đã yêu cầu*

Chỉ các phiên bản kernel từ 4.17 trở đi mới hỗ trợ Cephfs quotas. Nếu bạn cần quotas để đảm bảo PVC size nhưng kernel lại không hỗ trợ nó, bạn có thể disable kernel driver và sử dụng FUSE client. Điều này có thể được thực hiện qua cấu hình ```CSI_FORCE_CEPHFS_KERNEL_CLIENT: false``` trong operator deployment (```operator.yaml```). Tuy vậy, hãy nhớ rằng khi FUSE client được bật, có 1 known issue là khi thực hiện upgrade thì các pods sử dụng storage sẽ bị mất kết nối mount và sẽ cần restart. Điều này được đề cập chi tiết ở [upgrade guide](https://github.com/rook/rook/blob/master/Documentation/Upgrade/rook-upgrade.md)

## Consume the Shared Filesystem: K8s registry sample

Để ví dụ, chúng ta sẽ khởi động kube-registry pod với shared filesystem. Lưu cấu hình sau vào ```kube-registry.yaml```

```sh
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cephfs-pvc
  namespace: kube-system
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
  storageClassName: rook-cephfs
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kube-registry
  namespace: kube-system
  labels:
    k8s-app: kube-registry
    kubernetes.io/cluster-service: "true"
spec:
  replicas: 3
  selector:
    matchLabels:
      k8s-app: kube-registry
  template:
    metadata:
      labels:
        k8s-app: kube-registry
        kubernetes.io/cluster-service: "true"
    spec:
      containers:
      - name: registry
        image: registry:2
        imagePullPolicy: Always
        resources:
          limits:
            memory: 100Mi
        env:
        # Configuration reference: https://docs.docker.com/registry/configuration/
        - name: REGISTRY_HTTP_ADDR
          value: :5000
        - name: REGISTRY_HTTP_SECRET
          value: "Ple4seCh4ngeThisN0tAVerySecretV4lue"
        - name: REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY
          value: /var/lib/registry
        volumeMounts:
        - name: image-store
          mountPath: /var/lib/registry
        ports:
        - containerPort: 5000
          name: registry
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /
            port: registry
        readinessProbe:
          httpGet:
            path: /
            port: registry
      volumes:
      - name: image-store
        persistentVolumeClaim:
          claimName: cephfs-pvc
          readOnly: false
```

Tạo Kube registry deployment:

```sh
kubectl create -f csi/cephfs/kube-registry.yaml
```

## Consume the Shared Filesystem acroess namespaces

1 PVC mà bạn tạo sử dụng ```rook-cephfs``` StorageClass có thể được chia sẻ giữa nhiều Pods cùng 1 lúc, bao gồm cả read-write hay read-only, nhưng nó bị hạn chế bởi chỉ nằm trong 1 namespace (1 PVC là 1 tài nguyên nằm trong phạm vi namespace).

Dù vậy, có 1 số trường hợp mà bạn sẽ cần chia sẻ nội dung từ Cephfs PVC giữa các namespace khác nhau, để chia sẻ thư viện chẳng hạn, hoặc cho sự phối hợp của các ứng dụng chạy trong nhiều namespaces khác nhau.

Các bước dưới đây sẽ mô tả cách thức giải quyết vấn đề trên.

### Shared volume creation

Trong ```rook``` namespace, tạo 1 copy của secret ```rook-csi-cephfs-node```, đật tên nó là ```rook-csi-cephfs-node-user```

Chỉnh sửa secret mới vừa tạo, thay đổi tên của key (giữ nguyên phần value):

- Thay từ ```adminID``` => ```userID```
- Thay từ ```adminKey``` => ```userKey```

Tạo PVC mà bạn muốn chia sẻ, ví dụ:

```sh
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: base-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
  storageClassName: rook-cephfs
  volumeMode: Filesystem
```

PV tương ứng được tạo với PVC trên sẽ có tất cả thông tin cần thiết để kết nối đến CephFS volume:

```sh
kind: PersistentVolume
apiVersion: v1
metadata:
  name: pvc-a02dd277-cb26-4c1e-9434-478ebc321e22
  annotations:
    pv.kubernetes.io/provisioned-by: rook.cephfs.csi.ceph.com
  finalizers:
    - kubernetes.io/pv-protection
spec:
  capacity:
    storage: 100Gi
  csi:
    driver: rook.cephfs.csi.ceph.com
    volumeHandle: >-
      0001-0011-rook-0000000000000001-8a528de0-e274-11ec-b069-0a580a800213
    volumeAttributes:
      clusterID: rook
      fsName: rook-cephfilesystem
      storage.kubernetes.io/csiProvisionerIdentity: 1654174264855-8081-rook.cephfs.csi.ceph.com
      subvolumeName: csi-vol-8a528de0-e274-11ec-b069-0a580a800213
      subvolumePath: >-
        /volumes/csi/csi-vol-8a528de0-e274-11ec-b069-0a580a800213/da98fb83-fff3-485a-a0a9-57c227cb67ec
    nodeStageSecretRef:
      name: rook-csi-cephfs-node
      namespace: rook
    controllerExpandSecretRef:
      name: rook-csi-cephfs-provisioner
      namespace: rook
  accessModes:
    - ReadWriteMany
  claimRef:
    kind: PersistentVolumeClaim
    namespace: first-namespace
    name: base-pvc
    apiVersion: v1
    resourceVersion: '49728'
  persistentVolumeReclaimPolicy: Retain
  storageClassName: rook-cephfs
  volumeMode: Filesystem
```

Trên PV này, thay đổi ```persistentVolumeReclaimPolicy``` thành ```Retain``` để tránh nó bị xóa khi bạn xóa các PVCs.

Copy nội dung file YAML của PV, và tạo 1 PV tĩnh với các thông tin tương tự, nhưng thay đổi 1 số điểm sau:

- Thay tên (```name```): để tiện theo dõi, hãy thêm tên của namespace mà bạn muốn đặt PV vào cuối tên của PV
- Thay đổi ```volumeHandle```: tương tự, hãy thêm namespace vào
- Thêm dòng ```staticVolume: "true"``` vào ```volumeAttributes```
- Thêm dòng ```rootPath``` vào ```volumeAttributes```, với nội dung là ```subvolumePath```
- Trong ```nodeStageSecretRef```, thay đổi tên để trỏ đến secret mà bạn đã tạo trước đó (```rook-csi-cephfs-node-user```)
- Xóa thông tin không cần thiết trước khi áp dụng YAML (claimRef, managedFields,...)

File YAML cuối cùng sẽ có định dạng như sau:

```sh
kind: PersistentVolume
apiVersion: v1
metadata:
  name: pvc-a02dd277-cb26-4c1e-9434-478ebc321e22-newnamespace
spec:
  capacity:
    storage: 5Gi
  csi:
    driver: rook.cephfs.csi.ceph.com
    volumeHandle: >-
      0001-0011-rook-0000000000000001-8a528de0-e274-11ec-b069-0a580a800213-newnamespace
    volumeAttributes:
      clusterID: rook
      fsName: rook-cephfilesystem
      storage.kubernetes.io/csiProvisionerIdentity: 1654174264855-8081-rook.cephfs.csi.ceph.com
      subvolumeName: csi-vol-8a528de0-e274-11ec-b069-0a580a800213
      subvolumePath: >-
        /volumes/csi/csi-vol-8a528de0-e274-11ec-b069-0a580a800213/da98fb83-fff3-485a-a0a9-57c227cb67ec
      rootPath: >-
        /volumes/csi/csi-vol-8a528de0-e274-11ec-b069-0a580a800213/da98fb83-fff3-485a-a0a9-57c227cb67ec
      staticVolume: "true"
    nodeStageSecretRef:
      name: rook-csi-cephfs-node
      namespace: rook
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: rook-cephfs
  volumeMode: Filesystem
```

Trong namespace khác, tạo 1 PVC mà sẽ sử dụng PV mới này. Bạn chỉ cần đơn gỉn là trỏ tham số ```volumeName```. Hãy chắc chắn bạn chỉ định ```size``` tương đồng với PVC gốc:

```sh
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: second-pvc
  namespace: newnamespace
  finalizers:
    - kubernetes.io/pvc-protection
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
  volumeName: pvc-a02dd277-cb26-4c1e-9434-478ebc321e22-newnamespace
  storageClassName: rook-cephfs
  volumeMode: Filesystem
```

Giờ bạn đã có thể truy nhập vào cùng 1 CephFS subvolume từ nhiều PVCs trong nhiều namespaces khác nhau. Làm lại các bước trên (copy PV với các tên khác, tạo 1 PVC trỏ đến nó) ở mỗi namespace mà bạn muốn sử dụng subvolume này.

**Lưu ý:** PVCs/PVs mới chúng ta đã tạo là static. Do đó CephCSI không hỗ trợ các thao tác snapshots, clones, resizing hoặc delete chúng. Nếu bạn cần phải thực hiện các thao tác đó, bạn phải làm trên PVC gốc.

#### Shared volume removal

Vì cùng 1 Cephfs volume được dùng bởi nhiều PVCs/PVs, bạn phải thực hiện tuần tự như sau:

- Xóa các PVCs tính ở các namespaces đã tạo, nhưng giữ lại bản gốc
- Xóa PVs static tương ứng, các PVs này sẽ được đánh dấu là ```Released``` nếu bạn đã xóa PVCs trỏ đến nó. Giống bên trên, nhớ giữ lại bản gốc
- Chỉnh sửa PV gốc, thay đổi phần ```persistentVolumeReclaimPolicy``` từ ```Retain``` thành ```Delete```
- Xóa PVC gốc, nó sẽ xóa original PV, cũng như subvolume trong CephFS