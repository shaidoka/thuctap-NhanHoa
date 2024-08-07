# Object Storage by Ceph Rook

Object storage expose 1 S3 API đến storage cluster để ứng dụng có thể lưu hoặc lấy dữ liệu

## Prerequisites

- 1 Ceph Rook cluster đã được khởi tạo và hoạt động ổn định

## 1. Configure an Object Store

Rook có thể cấu hình Ceph Object Store cho một vài hoàn cảnh khác nhau. Hãy xem mỗi link ở phần bên dưới để biết cách cấu hình chi tiết:

- Tạo 1 **local object store** với dedicated Ceph pools. Lựa chọn này được khuyên dùng nếu bạn chỉ cần 1 object store, đây là phương thức dễ nhất, rất phù hợp để kiểm thử

- Tạo **1 hoặc nhiều object stores với shared Ceph pools**. Lựa chọn này được khuyến khích khi nhiều object stores được yêu cầu

- Kết nối đến 1 **RGW service trong 1 external Ceph cluster**, nâng cao của tạo 1 local object store

- Cấu hình **RGW Multisite** để đồng bộ bucket giữa object store trong nhiều cluster khác nhau

### 1.1. Create a Local Object Store

File mẫu dưới đây sẽ tạo 1 ```CephObjectStore``` mà khởi chạy RGW service trong cluster với 1 S3 API.

**Lưu ý:** Ví dụ này yêu cầu ít nhất 3 OSDs, với mỗi OSD đều nằm ở node khác nhau

OSDs phải nằm ở các nodes khác nhau do ```failureDomain``` được đặt thành ```host```, và ```erasureCoded``` chunk settings yêu cầu ít nhất 3 OSDs khác nhau (2 ```dataChunks``` và 1 ```codingChunks```)

Xem ```Object Store CRD```, để biết thêm thông tin chi tiết về thiết lập khả dụng cho ```CephObjectStore```

```sh
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: my-store
  namespace: rook-ceph
spec:
  metadataPool:
    failureDomain: host
    replicated:
      size: 3
  dataPool:
    failureDomain: host
    # For production it is recommended to use more chunks, such as 4+2 or 8+4
    erasureCoded:
      dataChunks: 2
      codingChunks: 1
  preservePoolsOnDelete: true
  gateway:
    # sslCertificateRef:
    port: 80
    # securePort: 443
    instances: 1
```

Sau khi ```CephObjectStore``` được tạo, Rook operator sẽ tạo tất cả các pools và tài nguyên cần thiết để khởi chạy dịch vụ. Quá trình này có thể mất vài phút.

Tạo object store với:

```sh
kubectl create -f object.yaml
```
Để đảm bảo object store có thể được thiết lập, hãy chờ RGW pod khởi động:

```sh
kubectl -n rook-ceph get pod -l app=rook-ceph-rgw
```

Để sử dụng object store, bước tiếp theo là tạo 1 bucket.

### 1.2. Create Local Object Store(s) with Shared Pools

Mẫu dưới đây sẽ tạo 1 hoặc nhiều object stores, Shared Ceph pools sẽ được tạo, điều này sẽ giúp giảm chi phí phát sinh do phải tạo thêm Ceph pools cho mỗi object store.

Data isolation (sự cô lập dữ liệu) được đảm bảo giữa các object store với việc sử dụng Ceph RADOS namespaces. Namespaces riêng biệt RADOS không cho phép truy cập dữ liệu giữa các object stores.

OSDs phải nằm ở các nodes khác nhau do ```failureDomain``` được đặt thành ```host```, và ```erasureCoded``` chunk settings yêu cầu ít nhất 3 OSDs khác nhau (2 ```dataChunks``` và 1 ```codingChunks```)

#### Shared Pools

Tạo shared pools mà sẽ được sử dụng bởi mỗi object stores:

**Lưu ý:** Nếu object store được tạo trước đó rồi, pool đầu tiên bên dưới (```.rgw.root```) không cần thiết phải định nghĩa nữa vì nó đã được tạo chung với object store đang tồn tại rồi. Chỉ cần có duy nhất 1 ```.rgw.root``` pool tồn tại để lưu trữ metadata cho tất cả object stores.

```sh
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: rgw-root
  namespace: rook-ceph # namespace:cluster
spec:
  name: .rgw.root
  failureDomain: host
  replicated:
    size: 3
    requireSafeReplicaSize: false
  parameters:
    pg_num: "8"
  application: rgw
---
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: rgw-meta-pool
  namespace: rook-ceph # namespace:cluster
spec:
  failureDomain: host
  replicated:
    size: 3
    requireSafeReplicaSize: false
  parameters:
    pg_num: "8"
  application: rgw
---
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: rgw-data-pool
  namespace: rook-ceph # namespace:cluster
spec:
  failureDomain: osd
  erasureCoded:
    # For production it is recommended to use more chunks, such as 4+2 or 8+4
    dataChunks: 2
    codingChunks: 1
  application: rgw
```

Tạo shared pool:

```sh
kubectl create -f object-shared-pools.yaml
```

#### Create Each Object Store

Sau khi các pools đã được tạo, chúng ta cần phải tạo object store tương ứng để tiêu thụ shared pools đó.

```sh
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: store-a
  namespace: rook-ceph # namespace:cluster
spec:
  sharedPools:
    metadataPoolName: rgw-meta-pool
    dataPoolName: rgw-data-pool
    preserveRadosNamespaceDataOnDelete: true
  gateway:
    # sslCertificateRef:
    port: 80
    instances: 1
```

Tạo object store:

```sh
kubectl create -f object-a.yaml
```

Để đảm bảo là object store được khởi tạo, chờ RGW pod khởi động:

```sh
kubectl -n rook-ceph get pod -l rgw=store-a
```

Các object stores có thể được tạo thêm dựa trên cùng shared pools bằng cách thay đổi tham số ```name``` của CephObjectStore. Trong folder tên "example" có 2 file manifest ví dụ cho ```object-a.yaml``` và ```object-b.yaml```

Để tiêu thụ object store, điều tiếp theo cần phải làm là tạo 1 bucket. Thay đổi default example object store name từ ```my-store``` để thay đổi tên của object store (như ```store-a```) trong ví dụ này.

### 1.3. Connect to an External Object Store

Rook có thể kết nối đến RGW gateways đã tồn tại để làm việc với external mode của ```CephCluster``` CRD. Đầu tiên, hãy tạo 1 ```rgw-admin-ops-user``` user trong Ceph cluster với các caps cần thiết:

```sh
radosgw-admin user create --uid=rgw-admin-ops-user --display-name="RGW Admin Ops User" --caps="buckets=*;users=*;usage=read;metadata=read;zone=read" --rgw-realm=<realm-name> --rgw-zonegroup=<zonegroup-name> --rgw-zone=<zone-name>
```

User ```rgw-admin-ops-user``` là cần thiết bởi Rook operator để quản lý buckets và users thông qua admin ops và s3 api. Cấu hình multisite cho RGW.

Sau đó tạo 1 secret với user credentials:

```sh
kubectl -n rook-ceph create secret generic --type="kubernetes.io/rook" rgw-admin-ops-user --from-literal=accessKey=<access key of the user> --from-literal=secretKey=<secret key of the user>
```

Nếu bạn có 1 ```CephCluster``` CRD bên ngoài, bạn cần hướng dẫn Rook tiêu thụ external gateways như sau:

```sh
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: external-store
  namespace: rook-ceph
spec:
  gateway:
    port: 8080
    externalRgwEndpoints:
      - ip: 192.168.39.182
        # hostname: example.com
```

Sử dụng tệp ```object-external.yaml``` có sẵn. Mặc dù multiple endpoints có thể được chỉ định, mình vẫn khuyên rằng tốt nhất nên sử dụng 1 endpoint thôi. Endpoint được thêm ngẫu nhiên vào ```configmap``` của OBC và secret của ```cephobjectstoreuser```. Rook sẽ không bao giờ đảm bảo endpoint được chọn ngẫu nhiên này có hoạt động hay không. Nếu có nhiều endpoints, hãy thêm load balancer vào trước chúng và sử dụng load balancer endpoint trong danh sách ```enternalRgwEndpoints```

Khi sẵn sàng, ta sẽ thấy trạng thái của cephobjectstore như sau:

```sh
kubectl -n rook-ceph get cephobjectstore external-store
NAME                                 PHASE
external-store                       Ready
```

Lúc này, hãy đảm bảo tất cả pod từ cluster của bạn có thể truy nhập vào endpoint:

```sh
$ curl 192.168.39.182:8080
<?xml version="1.0" encoding="UTF-8"?><ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>anonymous</ID><DisplayName></DisplayName></Owner><Buckets></Buckets></ListAllMyBucketsResult>
```

## 2. Object store endpoint

CephObjectStore resource ```status.info``` bao gồm các trường ```endpoint``` (và ```secureEndpoint```), thứ mà cho biết về endpoint có thể được sử dụng để truy cập object store dưới góc nhìn của client.

Mỗi object store cũng tạo 1 K8s service mà có thể được sử dụng bởi 1 client endpoint từ bên trong K8s cluster. DNS name của service là ```rook-ceph-rgw-<objectStoreName>.<objectStoreNamespace>.svc```. Service DNS name này là ```endpoint``` (hoặc ```secureEndpoint```) mặc định.

Với external clusters, các endpoint mặc định chứa ```spec.gateway.externalRgwEndpoint``` đầu tiên thay vì service DNS name.

Rook luôn sử dụng endpoint mặc định để thực hiện quản lý object store. Khi TLS được bật, TLS certificate phải luôn chỉ định endpoint DNS name mặc định để cho phép các thao tác quản lý được bảo mật. Chỉ định thiết lập TLS có thể được tìm thấy ở [gateway securePort documentation](https://github.com/rook/rook/blob/master/Documentation/CRDs/Object-Storage/ceph-object-store-crd.md#gateway-settings)

## 3. Create a Bucket

*Lưu ý: Tài liệu này chỉ là 1 guide cho việc tạo bucket sử dụng 1 Object Bucket Claim (OBC). Để tạo bucket sử dụng COSI Driver thử nghiệm, hãy xem qua [COSI Documentation](https://github.com/rook/rook/blob/master/Documentation/Storage-Configuration/Object-Storage-RGW/cosi.md)*

Giờ thì object store đã được thiết lập, điều tiếp theo chúng ta cần phải làm là tạo 1 bucket nơi mà 1 client có thể đọc và ghi objects. 1 bucket có thể được tạo bởi cách định nghĩa 1 storage class, tương tự như cách mà chúng ta đã sử dụng cho block và file storage. Đầu tiên, định nghĩa storage class mà sẽ cho phép object clients tạo 1 bucket. Storage class này định nghĩa object storage system, bucket retention policy, và các thông tin cần thiết bởi administrator. Lưu file ```storageclass-bucket-delete.yaml``` (ví dụ này được đặt tên như vậy vì ```Delete``` reclaim policy).

```sh
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: rook-ceph-bucket
# Change "rook-ceph" provisioner prefix to match the operator namespace if needed
provisioner: rook-ceph.ceph.rook.io/bucket
reclaimPolicy: Delete
parameters:
  objectStoreName: my-store
  objectStoreNamespace: rook-ceph
```

Nếu bạn đã triển khai Rook operator trong 1 namespace khác với ```rook-ceph```, thay đổi prefix (```rook-ceph```) trong ```provisioner``` để khớp với namespace bạn sử dụng.

```sh
kubectl create -f storageclass-bucket-delete.yaml
```

Dựa trên storage class này, 1 object client có thể yêu cầu 1 bucket bằng cách tạo 1 Object Bucket Claim (OBC). Khi OBC được tạo, Rook bucket provisioner sẽ tạo 1 bucket mới. Lưu ý rằng OBC tham chiếu đến storage class mà đã tạo ở trên. Lưu cấu hình này vào file ```object-bucket-claim-delete.yaml```

```sh
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: ceph-bucket
spec:
  generateBucketName: ceph-bkt
  storageClassName: rook-ceph-bucket
```

```sh
kubectl create -f object-bucket-claim-delete.yaml
```

Giờ thì claim đã được tạo, operator sẽ tạo bucket cũng như khởi tạo các tài nguyên khác để cho phép truy nhập vào bucket. 1 secret và ConfigMap được tạo với tên giống OBC và trong cùng namespace. Secret này chứa credentials sử dụng bởi application pod để truy cập vào bucket. ConfigMap chứa thông tin bucket endpoint và cũng sử dụng bởi pod. Xem thêm tài liệu về [OBC Documetation](https://github.com/rook/rook/blob/master/Documentation/Storage-Configuration/Object-Storage-RGW/ceph-object-bucket-claim.md) để hiểu rõ hơn về ```CephObjectBucketClaims```.

### Client Connections

Lệnh sau trích xuất thông tin trong secret và configmap:

```sh
export AWS_HOST=$(kubectl -n default get cm ceph-bucket -o jsonpath='{.data.BUCKET_HOST}')
export PORT=$(kubectl -n default get cm ceph-bucket -o jsonpath='{.data.BUCKET_PORT}')
export BUCKET_NAME=$(kubectl -n default get cm ceph-bucket -o jsonpath='{.data.BUCKET_NAME}')
export AWS_ACCESS_KEY_ID=$(kubectl -n default get secret ceph-bucket -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 --decode)
export AWS_SECRET_ACCESS_KEY=$(kubectl -n default get secret ceph-bucket -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 --decode)
```

Nếu có bất kỳ ```hosting.dnsNames``` được thiết lập trong ```CephObjectStore``` CRD, S3 clients có thể truy cập buckets trong ```virtual-host-style```. Nếu không, S3 clients phải được thiết lập để sử dụng path-style access.


## 4. Consume the Object Storage

Giờ bạn đã thiết lập object store cũng như là tạo 1 bucket, bạn có thể sử dụng nó từ 1 s3 client.

Phần này sẽ hướng dẫn bạn kiểm tra kết nối đến ```CephObjectStore``` và upload/download từ nó. Lưu ý rằng, các lệnh ở phần bên dưới này đều được chạy từ **Rook toolbox**

### Connection Environment Variables

Để đơn giản hóa các lệnh s3 client, bạn sẽ muốn thiết lập 4 environment variables để sử dụng bởi client của bạn (ví dụ như bên trong toolbox). Xem phần bên trên để biết cách lấy tham số cho 1 bucket đã tạo bởi 1 ```ObjectBucketClaim```.

```sh
export AWS_HOST=<host>
export PORT=<port>
export AWS_ACCESS_KEY_ID=<accessKey>
export AWS_SECRET_ACCESS_KEY=<secretKey>
```

- ```Host```: DNS hostname nơi mà rgw service được tìm thấy trong cluster. Giả sử bạn đang sử dụng cluster mặc định ```rook-ceph```, nó sẽ là ```rook-ceph-rgw-my-store.rook-ceph.svc```
- ```Port```: Đây là endpoint mà rgw service sẽ lắng nghe. Chạy lệnh ```kubectl -n rook-ceph get svc rook-ceph-rgw-my-store``` để lấy thông tin về port
- ```Access key```: ```access_key``` của user mà được in ra ở bên trên
- ```Secret key```: ```secret_key``` của user mà được in ra ở bên trên

Ví dụ:

```sh
export AWS_HOST=rook-ceph-rgw-my-store.rook-ceph.svc
export PORT=80
export AWS_ACCESS_KEY_ID=XEZDB3UJ6X7HVBE7X7MA
export AWS_SECRET_ACCESS_KEY=7yGIZON7EhFORz0I40BFniML36D2rl8CQQ5kXU6l
```

Access key và secret key có thể được thu thập bằng cách bên trên, hoặc bằng cách tạo 1 user (thứ mà sẽ được đề cập ở phần sau) nếu bạn không tạo bucket với 1 OBC

### Configure s5cmd

Để kiểm tra ```CephObjectStore```, đặt object store credentials trong toolbox pod mà chứa công cụ ```s5cmd```

**Lưu ý:** Mặc định thì ```toolbox.yaml``` chưa được tích hợp s5cmd. Toolbox mà đi kèm với rook operator image mới bao gồm cả s5cmd

```sh
kubectl create -f deploy/examples/toolbox-operator-image.yaml
mkdir ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF
```

### PUT hay GET 1 object

Upload 1 file:

```sh
echo "Hello Rook" > /tmp/rookObj
s5cmd --endpoint-url http://$AWS_HOST:$PORT cp /tmp/rookObj s3://$BUCKET_NAME
```

Download và verify file từ bucket:

```sh
s5cmd --endpoint-url http://$AWS_HOST:$PORT cp s3://$BUCKET_NAME/rookObj /tmp/rookObj-download
cat /tmp/rookObj-download
```

## 5. Monitoring health

Rook thiết lập health probes trên deployment đã tạo cho CephObjectStore gateways. Hãy xem thêm [CRD document](https://github.com/rook/rook/blob/master/Documentation/CRDs/Object-Storage/ceph-object-store-crd.md#health-settings) để biết thêm thông tin về cách cấu hình probes và monitoring cho deployment.

## 6. Access External to the Cluster

Rook thiết lập object storage để các pods có thể truy cập vào nó từ bên trong cluster. Nếu ứng dụng của bạn đang chạy bên ngoài cluster, bạn sẽ cần cài đặt 1 external service để expose nó ra ```NodePort```

Đầu tiên, ghi lại service mà expose RGW bên trong cluster. Chúng ta sẽ để nguyên service này ở đó và tạo 1 service mới cho việc truy cập từ bên ngoài.

```sh
$ kubectl -n rook-ceph get service rook-ceph-rgw-my-store
NAME                     CLUSTER-IP   EXTERNAL-IP   PORT(S)     AGE
rook-ceph-rgw-my-store   10.3.0.177   <none>        80/TCP      2m
```

Lưu external service vào ```rgw-external.yaml```

```sh
apiVersion: v1
kind: Service
metadata:
  name: rook-ceph-rgw-my-store-external
  namespace: rook-ceph
  labels:
    app: rook-ceph-rgw
    rook_cluster: rook-ceph
    rook_object_store: my-store
spec:
  ports:
  - name: rgw
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: rook-ceph-rgw
    rook_cluster: rook-ceph
    rook_object_store: my-store
  sessionAffinity: None
  type: NodePort
```

Giờ thì tạo nó thôi:

```sh
kubectl create -f rgw-external.yaml
```

Xem cả 2 rgw services mà đang chạy và để ý port của chúng:

```sh
$ kubectl -n rook-ceph get service rook-ceph-rgw-my-store rook-ceph-rgw-my-store-external
NAME                              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
rook-ceph-rgw-my-store            ClusterIP   10.104.82.228    <none>        80/TCP         4m
rook-ceph-rgw-my-store-external   NodePort    10.111.113.237   <none>        80:31536/TCP   39s
```

RGW service mà chạy nội bộ thì lắng nghe trên port 80, trong khi external port trong trường hợp này là ```31536```. Giờ bạn có thể truy cập ```CephObjectStore``` từ bất kỳ đâu. Tất cả những gì bạn cần là hostname/IP của bất kỳ node nào trong cụm, external port, và user credentials.

## 7. Create a User

Nếu bạn cần tạo 1 tập các user credential độc lập để truy cập vào S3 endpoint, tạo 1 ```CephObjectStoreUser```. Người dùng sẽ kết nối đến RGW service trong cluster sử dụng S3 aPI. User sẽ độc lập với bất kỳ Object Bucket Claims mà bạn đã tạo trước đó theo hướng dẫn của tài liệu này.

Xem ```Object Store User CRD``` để biết thêm chi tiết về các cấu hình khả dụng cho ```CephObjectStoreUser```.

```sh
apiVersion: ceph.rook.io/v1
kind: CephObjectStoreUser
metadata:
  name: my-user
  namespace: rook-ceph
spec:
  store: my-store
  displayName: "my display name"
```

Khi ```CephObjectStoreUser``` được tạo, Rook operator sau đó sẽ sử dụng RGW user trên ```CephObjectStore``` đã chỉ định và lưu trữ Access Key và Secret Key trong 1 k8s secret trong cùng namespace với ```CephObjectStoreUser```.

tạo object store user

```sh
kubectl create -f object-user.yaml
```

Để chắc chắn object store user đã được tạo, hãy kiểm tra secret

```sh
$ kubectl -n rook-ceph describe secret rook-ceph-object-user-my-store-my-user
Name:    rook-ceph-object-user-my-store-my-user
Namespace:  rook-ceph
Labels:     app=rook-ceph-rgw
            rook_cluster=rook-ceph
            rook_object_store=my-store
Annotations:  <none>

Type: kubernetes.io/rook

Data
====
AccessKey:  20 bytes
SecretKey:  40 bytes
```

Các trường dữ liệu AccessKey và SecretKey có thể được mount vào trong pod làm environment variables. Thông tin chi tiết hơn về cách sử dụng k8s secret, có thể thêm xem tại [Secret documentation](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/k8s/K8s_Secret.md)

Để trực tiếp kiểm tra secret:

```sh
kubectl -n rook-ceph get secret rook-ceph-object-user-my-store-my-user -o jsonpath='{.data.AccessKey}' | base64 --decode
kubectl -n rook-ceph get secret rook-ceph-object-user-my-store-my-user -o jsonpath='{.data.SecretKey}' | base64 --decode
```

## 8. Virtual host-style Bucket Access

Ceph Object Gateway hỗ trợ truy cập bucket sử dụng kiểu địa chỉ ```virtual host-style```, thứ mà cho phép đánh địa chỉ cho bucket sử dụng bucket name như 1 subdomain cho endpoint.

AWS đã loại bỏ kiểu địa chỉ ```path-style```, thứ mà được sử dụng theo mặc định ở Ceph hay Rook. Kéo theo đó, nhiều end-user applications đã bắt đầu loại bỏ việc hỗ trợ ```path-style``` hoàn toàn. Nhiều production clusters sẽ bắt buộc phải thích nghi với việc sử dụng địa chỉ ```virtual-host-style```

Virtual-host-style yêu cầu 2 thứ:

- 1 endpoint mà hỗ trợ widlcard adressing
- CephObjectStore [hosting](https://github.com/rook/rook/blob/master/Documentation/CRDs/Object-Storage/ceph-object-store-crd.md#hosting-settings) configuration

Wildcard addressing có thể được thiết lập bằng 1 vài cách, có thể kể tới như:

- Kubernetes ingress loadbalancer
- Openshift DNS operator

Thiết lập ```hosting``` tối thiểu được khuyến nghị trong ví dụ dưới đây. Quan trọng là hãy đảm bảo Rook quảng bá wildcard-addressable endpoint có độ ưu tiên cao hơn mặc định. TLS cũng được khuyến khích để tăng tính bảo mật.

```sh
spec:
  ...
  hosting:
    advertiseEndpoint:
      dnsName: my.wildcard.addressable.endpoint.com
      port: 443
      useTls: true
```

1 thiết lập phức tạp khác liên quan đến ```hosting``` được đề cập ở bên dưới. Trong ví dụ này, 2 wildcard-addressable endpoints được thiết lập. 1 là wildcard-addressable ingress service mà có thể được truy cập từ client bên ngoài k8s cluster (```s3.ingress.domain.com```). Cái còn lại là wildcard-addressable k8s cluster service (```s3.rook-ceph.svc```). Cluster service được ưu tiên quảng bá endpoint vì internal service muốn tránh khả nâng router của ingress lại trở thành bottleneck cho các hoạt động của S3 client.

```sh
spec:
  ...
  hosting:
    advertiseEndpoint:
      dnsName: s3.rook-ceph.svc
      port: 443
      useTls: true
  dnsNames:
    - s3.ingress.domain.com
```

## 9. Object Multisite

Multisite là 1 tính năng của Ceph mà cho phép object stores replicate dữ liệu của nó trên nhiều Ceph clusters.

Multisite cũng cho phép object stores độc lập và cô lập với các object stores khác trong cluster.

Để biết thêm thông tin về multisite, hãy đọc [ceph multisite overview](https://github.com/rook/rook/blob/master/Documentation/Storage-Configuration/Object-Storage-RGW/ceph-object-multisite.md) để biết thêm thông tin chi tiết.