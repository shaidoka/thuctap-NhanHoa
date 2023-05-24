# Kubernetes storage HostPath và EmptyDir

## Volume là gì?

Volume hiểu đơn giản là một mount point từ hệ thống file của server vào bên trong container.

Khi ta ghi dữ liệu vào filesystem của container thì dữ liệu này chỉ tồn tại khi container còn chạy, nếu container bị xóa đi thì dữ liệu sẽ mất, do đó để giữ lại những dữ liệu này thì ta phải sử dụng volume.

Trong K8s hỗ trợ nhiều kiểu volume khác nhau, có thể bao gồm:
- emptyDir
- hostPath
- NFS
- gcePersistentDisk, awsElasticBlockStore, azureDisk (cloud storage)
- cinder, cephfs, iscsi, flocker, glusterfs, quobyte, rbd, flexVolume, vshereVolume, photonPersistentDisk, scaleIO
- configMap, secret, downwardAPI
- PersistentVolumeClaim

Những loại volume trên được phân chia thành 3 dạng chính:
- Volume dùng để chia sẻ dữ liệu giữa các container trong Pod
- Volume đính kèm vào trong filesystem một node
- Volume đính kèm vào cluster và các node khác nhau có thể truy cập

Khi ta chạy nhiều container tỏng cùng 1 pod thì ta sẽ nhận ra rằng các container khác nhau có thể truy cập vào cùng 1 folder để ghi dữ liệu, và sẽ có những container khác truy cập vào cùng 1 folder đó để lấy dữ liệu ra xử lý. 

## Sử dụng emptyDir volume để share data giữa các containers

emptyDir là loại volume đơn giản nhất, nó sẽ tạo ra một empty directory bên trong Pod, các container trong một Pod có thể ghi dữ liệu vào bên trong nó. Volume này chỉ tồn tại trong 1 lifecycle của Pod, dữ liệu trong loại volume này chỉ được lưu trữ tạm thời và sẽ mất đi khi Pod bị xóa. Ta dùng loại volume này khi ta chỉ muốn các container có thể chia sẻ dữ liệu lẫn nhau và không cần lưu trữ dữ liệu lại. Ví dụ là dữ liệu log từ một container chạy web API, và ta có một container khác truy cập vào log đó để xử lý log

Ví dụ:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: fortune
spec:
  containers:
  - name: html-generator
    image: luksa/fortune
    volumeMounts:
    - name: html
      mountPath: /var/htdocs
  - name: web-server
    image: nginx:alpine
    ports:
    - containerPort: 80
      protocol: TCP
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
      readOnly: true
  volumes:
  - name: html
    emptyDir: {}
```

Container html-generator này mỗi 10s sẽ tạo ra 1 nội dung bất kì và lưu nó vào file index.html. Và ta sẽ có 1 container khác, tên là web-server sẽ start 1 server và hosting nội dung ở folder ```/usr/share/nginx/html```

Ở đây ta có một emptyDir volume tên là html, được mount vào container html-generator ở folder /var/htdocs và container html-generator sẽ tạo 1 file html index.html ở trong emptyDir volume này. Và emptyDir volume này được mount tới container webserver. Nên khi ta truy cập container Web thì ta sẽ thấy được những nội dung mà container html-generator tạo ra.

Kiểm thử:

```sh
kubectl apply -f pod-emptydir.yaml
kubectl port-forward fortune 8080:80
curl http://localhost:8080
```

Lưu ý là chỉ dùng emptyDir để chia sẻ dữ liệu giữa những container chứ không dùng để lưu persistent data.

## Sử dụng hostPath để truy cập filesystem của worker node

HostPath là loại volume sẽ tạo ra một mount point từ Pod ra ngoài filesystem của node. Đây là loại volume đơn giản nhất để lưu trữ persistent data. Dữ liệu lưu trong volume này chỉ tồn tại trên 1 worker node và sẽ không bị xóa đi khi pod bị xóa

Ví dụ:

```sh
apiVerison: v1
kind: Pod
metadata:
  name: hostpath-volume
spec:
  containers:
  - image: nginx:alpine
    name: web-server
    volumeMounts: 
    - name: html
      mountPath: /usr/share/nginx/html
      readOnly: true
    - name: log
      mountPath: /var/log/nginx
  ports:
  - containerPort: 80
    protocol: TCP
  volumes:
  - name: html
    hostPath:
      path: /usr/share/nginx/html
  - name: log
    hostPath:
      path: /var/log
```

Đối với loại volume này thì Pod cần phải được tạo đúng worker node thì mới có được dữ liệu trước đó, nếu Pod của ta được tạo ở worker node khác thì khi đó Pod sẽ không có dữ liệu cũ. Loại volume này ta không sử dụng nó cho việc lưu trữ persistent data hoàn toàn được. CÁc ta muốn là dù Pod được tạo ở worker node nào thì dữ liệu của ta vẫn có, để mount được vào trong container.

## Sử dụng cloud storage để lưu trữ persistent data

Loại volume này chỉ được hỗ trợ trên các nền tảng cloud, giúp ta lưu trữ persistent data, kể cả khi pod được tạo ở các worker node khác nhau, dữ liệu của ta vẫ tồn tại cho container. 3 nền tảng cloud mà phổ biến nhất là AWS, GG Cloud, Azure tương ứng với 3 loại volume là **gcePersistentDisk**, **awsElasticBlockStore**, **azureDisk**

Ví dụ với GCE:

```sh
gcloud compute disks create --size=1GiB --zone=europe-west1-b mongodb
```

Tạo 1 file tên là gcepd.yaml với config như sau:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mongodb
spec:
  containers:
  - image: mongo
    name: mongodb
    ports:
    - containerPort: 27017
      protocol: TCP
    volumeMounts:
    - name: mongodb-data
      mountPath: /data/db
  volumes:
  - name: mongodb-data
    gcePersistentDisk:
      pdName: mongodb
      fsType: ext4
```

```sh
kubectl create -f gcepd.yaml
```

Ở đây ta sẽ tạo 1 volume loại gcePersistentDisk với name là mongodb-data và mount nó vào trong container mongodb ở folder /data/db

Vì loại volume này ta sẽ sử dụng GCE persistent disk, nên nó không thuộc về bất cứ worker node nào mà nằm riêng lẻ một mình nó. Khi đó Pod của ta dù tạo ở bất kì worker node nào thì ta vẫn có thể mount được tới volume này. Và dữ liệu của volume này vẫn được giữ nguyên khi Pod xóa đi

Để sử dụng volume của cloud storage khác thì ta chỉ cần thay đổi loại volume là được, rất đơn giản, ví dụ như sau:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mongodb
spec:
  ...
  volumes:
  - name: mongodb-data
    awsElasticBlockStore:
      pdName: aws-ebs
      fsType: ext4
```

Bây giờ ta sẽ test bằng cách ghi dữ liệu vào bên trong mongodb-data container, và ta xóa Pod, khi ta tạo Pod lại, ta sẽ thấy dữ liệu của ta vẫn còn ở đó

```sh
kubectl exec -it mongodb mongo

MongoDB shell version: 3.2.8
connecting to: mongodb://127.0.0.1:27017
Welcome to the MongoDB shell.
...
```

```sh
> use mystore
switched to db mystore
> db.foo.insert({name:'foo'})
WriteResult({ "nInserted" : 1 })
> db.foo.find()
{ "_id" : ObjectId("57a61eb9de0cfd512374cc75"), "name" : "foo" }
```

```sh
kubectl delete pod mongodb
```

```sh
kubectl create -f gcepd.yaml
```

```sh
kubectl exec -it mongodb mongo

MongoDB shell version: 3.2.8
connecting to: mongodb://127.0.0.1:27017
Welcome to the MongoDB shell.
...
```

```sh
> use mystore
switched to db mystore
> db.foo.find()
{ "_id" : ObjectId("57a61eb9de0cfd512374cc75"), "name" : "foo" }
```