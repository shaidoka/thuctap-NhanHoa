# Secrets

Kubernetes Secret cho phép ta lưu trữ và quản lý thông tin nhạy cảm, chẳng hạn như mật khẩu, OAuth token và SSH key. Việc lưu trữ các thông tin bí mật trong Secret sẽ an toàn các thông tin bí mật trong Secret sẽ an toàn và linh hoạt hơn so với việc để nó nguyên văn trong định nghĩa Pod hoặc trong container image.

## Tổng quan về Secrets

Secret là một object chứa một lượng nhỏ dữ liệu nhạy cảm như mật khẩu, token hoặc key. Thông tin đó có thể được đưa vào trong đặc tả Pod hoặc trong container image. Người dùng hoặc hệ thống đều có thể tạo Secret.

Để sử dụng Secret, Pod cần tham chiếu đến Secret. Một Secret có thể được sử dụng với Pod theo 3 cách:
- Như là các file trong một volume được mount trên 1 hoặc nhiều container của Pod
- Như là biến môi trường của container
- Bởi kubelet khi pull image cho Pod

Hãy cùng đi từng phần trong bài viết này.

### Secret tích hợp sẵn

**Service account tự động tạo và đính kèm Secret với thông tin xác thực API**

K8s tự động tạo các Secret chứa thông tin xác thực (**credential**) để truy cập API và tự động chỉnh sửa các Pod của ta để sử dụng loại Secret này.

Việc tạo và sử dụng tự động các thông tin xác thực API có thể bị vô hiệu hóa hoặc ghi đè nếu muốn. Tuy nhiên, nếu tất cả những gì ta cần là truy cập an toàn vào API server thì đây là quy trình làm việc được đề xuất.

Cách hoạt động của ServiceAccount được đề cập ở [đây](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)

### Tự tạo Secret

1. **Tạo Secret bằng cách sử dụng ```kubectl```**

Secret có thể chứa thông tin xác thực (**credentia**) của người dùng theo yêu cầu của Pods để truy cập cơ sở dữ liệu. Ví dụ: chuỗi kết nối (connection string) cơ sở dữ liệu bao gồm username và password. Ta có thể lưu username trong file ```./username.txt``` và password trong file ```./password.txt``` trên máy cục bộ.

```sh
# Tạo các file cần thiết để sử dụng cho các ví dụ bên dưới
echo -n 'admin' > ./username.txt
echo -n 'eJd9z2suof96XCvX' > ./password.txt
```

Lệnh ```kubectl create secret``` sẽ đóng gói các file này thành 1 Secret và tạo ra object tương ứng trên API server.

```sh
kubectl create secret generic db-user-pass --from-file=./username.txt --from-file=./password.txt
```

Đầu ra sẽ có dạng:

```sh
secret "db-user-pass" created
```

Tên key mặc định sẽ là tên file. Ta có thể tùy ý đặt tên key bằng tham số ```[--from-file=[key=]source]```. Ví dụ:

```sh
kubectl create secret generic db-user-pass --from-file=username=./username.txt --from-file=password=./password.txt
```

**Lưu ý:** các ký tự đặc biệt như $, \, *, = và ! sẽ được thông dịch bởi shell và yêu cầu ký tự escape. Trong hầu hết các shell, cách dễ nhất để escape password là bao quanh nó bởi dấu strong quote ('). Ta không cần phải escape nếu ký tự đặc biệt nằm trong file.

Ta có thể kiểm tra xem Secret đã được tạo ra chưa bằng lệnh

```sh
kubectl get secrets
```

Đầu ra sẽ có dạng:

```sh
NAME                  TYPE                                  DATA      AGE
db-user-pass          Opaque                                2         51s
```

Mô tả chi tiết về secret:

```sh
kubectl describe secrets/db-user-pass
```

Đầu ra:

```sh
Name:            db-user-pass
Namespace:       default
Labels:          <none>
Annotations:     <none>

Type:            Opaque

Data
====
password.txt:    12 bytes
username.txt:    5 bytes
```

2. **Tạo Secret thủ công**

Trước tiên, ta tạo nội dung đặc tả của Secret trong một file, ở định dạng JSON hoặc YAML, sau đó tạo Secret object đó trên API server. Secret chứa 2 ánh xạ (map): ```data``` và ```stringData```

Trường ```data``` được sử dụng để lưu trữ dữ liệu tùy ý, được mã hóa bằng **base64**. Trường ```stringData``` được cung cấp chỉ để thuận tiện, nó cho phép ta cung cấp dữ liệu Secret dưới dạng chuỗi không được mã hóa.

Ví dụ: để lưu trữ hai chuỗi trong Secret bằng trường ```data```, hãy chuyển đổi chuỗi thành base64 như sau:

```sh
echo -n 'admin' | base64
```

Đầu ra:

```sh
YWRtaW4=
```

```sh
echo -n 'eJd9z2suof96XCvX' | base64
```

Đầu ra:

```sh
ZUpkOXoyc3VvZjk2WEN2WA==
```

Viết nội dung đặc tả của Secret như sau:

```sh
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=
  password: ZUpkOXoyc3VvZjk2WEN2WA==
```

Giờ ta tạo Secret bằng lệnh ```kubectl apply```

```sh
kubectl apply -f ./secret.yaml
```

Đầu ra có dạng:

```sh
secret "mysecret" created
```

Trong một số trường hợp nhất định, ta có thể muốn sử dụng trường ```stringData```. Trường này cho phép ta đặt một chuỗi (không được mã hóa theo base64) trực tiếp vào đặc tả Secret và chuỗi sẽ được mã hóa khi Secret được tạo hoặc cập nhật.

Một ví dụ thực tế về điều này có thể là khi ta đang triển khai một ứng dụng sử dụng Secret để lưu trữ file cấu hình và ta muốn đưa vào (populate) các phần của file cấu hình đó trong quá trình triển khai của mình.

Ví dụ: nếu ứng dụng của ta sử dụng file cấu hình sau:

```sh
apiUrl: "https://my.api.com/api/v1"
username: "user"
password: "password"
```

Ta có thể lưu trữ nó trong 1 Secret sử dụng đặc tả sau:

```sh
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
stringData:
  config.yaml: |-
    apiUrl: "https://my.api.com/api/v1"
    username: {{username}}
    password: {{password}}
```

Công cụ triển khai sau đó có thể thay thế các biến mẫu (template variable) {{username}} và {{password}} trước khi chạy ```kubectl apply```

Trường ```stringData``` là trường chỉ ghi (write only) giúp ta thuận tiện hơn. Nó không bao giờ xuất output đầu ra khi ta lấy về Secret (từ api server). Ví dụ: nếu ta chạy lệnh sau:

```sh
kubectl get secret mysecret -o yaml
```

Đầu ra sẽ như sau:

```sh
apiVersion: v1
data:
  config.yaml: YXBpVXJsOiAiaHR0cHM6Ly9teS5hcGkuY29tL2FwaS92MSIKdXNlcm5hbWU6IHt7dXNlcm5hbWV9fQpwYXNzd29yZDoge3twYXNzd29yZH19
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret","metadata":{"annotations":{},"name":"mysecret","namespace":"default"},"stringData":{"config.yaml":"apiUrl: \"https://my.api.com/api/v1\"\nusername: {{username}}\npassword: {{password}}"},"type":"Opaque"}
  creationTimestamp: "2023-04-04T04:34:44Z"
  name: mysecret
  namespace: default
  resourceVersion: "1403569"
  uid: b4a20982-95b6-49ec-a4a4-a6105ab1e9f4
type: Opaque
```

Nếu một trường, chẳng hạn như ```username```, được chỉ định trong cả ```data``` và ```stringData``` thì giá trị trong ```stringData``` sẽ được ưu tiên sử dụng. Ví dụ:

```sh
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=
stringData:
  username: administrator
```

Secret đó sau khi được tạo sẽ như sau:

```sh
apiVersion: v1
data:
  username: YWRtaW5pc3RyYXRvcg==
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"username":"YWRtaW4="},"kind":"Secret","metadata":{"annotations":{},"name":"mysecret","namespace":"default"},"stringData":{"username":"administrator"},"type":"Opaque"}
  creationTimestamp: "2023-04-04T04:40:41Z"
  name: mysecret
  namespace: default
  resourceVersion: "1404108"
  uid: e995da3f-ada5-4600-8572-0fdf5f018cbd
type: Opaque
```

Trong đó ```YWRtaW5pc3RyYXRvcg==``` là mã hóa base64 của ```administrator```

Các key của ```data``` và ```stringData``` chỉ được bao gồm các ký tự chữ và số, dấu gạch ngang '-', gạch dưới '_', hoặc dấu chấm '.'

3. **Tạo ra Secret từ generator**

Kể từ Kubernetes 1.14, ```kubectl``` hỗ trợ quản lý các object bằng [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/). Kustomize cung cấp tài nguyên **Generator** để tạo Secret và ConfigMaps. Kustomize generator phải được chỉ định trong file ```kustomization.yaml``` bên trong một thư mục. Sau khi tạo Secret, ta có thể tạo Secret trên API server bằng lệnh ```kubectl apply```

4. **Tạo ra Secret từ file**

Ta có thể tạo Secret bằng cách định nghĩa ```SecretGenerator``` từ các file ```./username.txt``` và ```./password.txt```

```sh
cat <<EOF >./kustomization.yaml
secretGenerator:
- name: db-user-pass
  files:
  - username.txt
  - password.txt
EOF
```

Chạy lệnh ```kubectl apply``` tại thư mục có chứa file ```kustomization.yaml``` để tạo ra Secret:

```sh
kubectl apply -k .
```

Đầu ra có dạng

```sh
secret/db-user-pass-96mffmfh4k created
```

Ta có thể kiểm tra Secret đã tạo bằng lệnh

```sh
kubectl get secrets
```

Hoặc describe bằng

```sh
kubectl describe secrets/db-user-pass-96mffmfh4k
```

5. **Tạo Secret từ chuỗi ký tự (literal)**

Ta có thê tạo Secret bằng cách định nghĩa ```secretGenerator``` từ chuỗi ký tự (literal) ```username=admin``` và ```passsword=secret```:

```sh
cat <<EOF >./kustomization.yaml
secretGenerator:
- name: db-user-pass
  literals:
  - username=admin
  - password=secret
EOF
```

Sau đó cũng chạy ```kubectl apply``` để tạo Secret

**Lưu ý:** Khi secret được tạo ra, tên của nó sẽ được thêm 1 đoạn đằng sau, đoạn này là hash của dữ liệu trong Secret. Điều này đảm bảo rằng mỗi khi dữ liệu được sửa đổi thì sẽ có 1 Secret mới được tạo ra.

6. **Giải mã Secret**

Secret có thể được lấy về bằng cách chạy lệnh ```kubectl get secret```. Ví dụ: ta có thể xem Secret được tạo ra trong phần trước bằng cách chạy lệnh:

```sh
kubectl get secret mysecret -o yaml
```

Đầu ra:

```sh
apiVersion: v1
data:
  username: YWRtaW5pc3RyYXRvcg==
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"username":"YWRtaW4="},"kind":"Secret","metadata":{"annotations":{},"name":"mysecret","namespace":"default"},"stringData":{"username":"administrator"},"type":"Opaque"}
  creationTimestamp: "2023-04-04T04:40:41Z"
  name: mysecret
  namespace: default
  resourceVersion: "1404108"
  uid: e995da3f-ada5-4600-8572-0fdf5f018cbd
type: Opaque
```

Giải mã trường ```ussername```:

```sh
echo 'YWRtaW5pc3RyYXRvcg==' | base64 --decode
```

Đầu ra:

```sh
administrator
```

7. **Chỉnh sửa Secret**

Secret hiện có thể được chỉnh sửa bằng lệnh sau:

```sh
kubectl edit secrets mysecret
```

Lệnh trên sẽ mở trình soạn thảo được cấu hình mặc định và cho phép cập nhật giá trị Secret mã hóa base64 trong trường ```data```

```sh
apiVersion: v1
data:
  username: YWRtaW5pc3RyYXRvcg==
  password: MWYyZDFlMmU2N2Rm
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"username":"YWRtaW4="},"kind":"Secret","metadata":{"annotations":{},"name":"mysecret","namespace":"default"},"stringData":{"username":"administrator"},"type":"Opaque"}
  creationTimestamp: "2023-04-04T04:40:41Z"
  name: mysecret
  namespace: default
  resourceVersion: "1404108"
  uid: e995da3f-ada5-4600-8572-0fdf5f018cbd
type: Opaque
```

## Sử dụng Secret

Secret có thể được mount dưới dạng **volume dữ liệu** hoặc được expose dưới dạng các **biến môi trường** được sử dụng bởi một container trong Pod. Các Secret cũng có thể được sử dụng bởi các phần khác của hệ thống mà không cần phải expose trực tiếp cho Pod.

Ví dụ: Secrets có thể giữ thông tin xác thực (credential) mà các phần khác trong hệ thống nên sử dụng để tương tác với các hệ thống bên ngoài thay mặt cho ta.

### 1. Sử dụng Secret như là file từ pod

Để sử dụng Secret trong một volume trong Pod:
- Tạo 1 Secret mới hoặc sử dụng Secret hiện có. Nhiều Pods có thể tham chiếu đến cùng 1 Secret
- Chỉnh sửa định nghĩa Pod để thêm Volume trong ```.spec.volumes[]```. Đặt tên bất kỳ cho volume và thiết lập trường ```.spec.volumes[].Secret.secretName``` bằng với tên của Secret object ở bước 1.
- Thêm trường ```.spec.containers[].VolumeMounts[]``` vào mỗi container cần sử dụng Secret. Chỉ định ```.spec.containers[].VolumeMounts[].ReadOnly = true``` và ```.spec.containers[].VolumeMounts[].MountPath``` là một tên thư mục chưa được sử dụng, nơi ta muốn Secret sẽ xuất hiện.
- Chỉnh sửa container image hoặc command line để chương trình tìm kiếm các file trong thư mục đó. Mỗi key trong phần ```data``` của Secret sẽ trở thành tên file trong ```mountPath```

Ví dụ về cách Pod mount Secret trong một volume:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/etc/foo"
      readOnly: true
  volumes:
  - name: foo
    secret:
      secretName: mysecret
```

Mỗi Secret ta muốn sử dụng cần được tham chiếu trong ```.spec.volumes```.

Nếu có nhiều container trong Pod thì mỗi container cần có phần ```volumeMounts``` riêng của nó nhưng chỉ cần một ```.spec.volume``` cho mỗi Secret.

Ta có thể đóng gói nhiều file thành một Secret hoặc sử dụng nhiều Secret, tùy theo cách nào thuận tiện hơn.

**Ánh xạ (project) Secret key đến đường dẫn cụ thể**

Ta cũng có thể kiểm soát các đường dẫn trong volume nơi các Secret key sẽ được ánh xạ (projected). Ta có thể sử dụng trường ```.spec.volumes[].Secret.items``` để thay đổi đường dẫn mục tiêu của từng key:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/etc/foo"
      readOnly: true
  volumes:
  - name: foo
    secret:
      secretName: mysecret
      items:
      - key: username
        path: my-group/my-username
```

Với đặc tả trên:
- ```username``` secret được lưu trữ trong file ```/etc/foo/my-group/my-username``` thay vì ```/etc/foo/username```
- ```password``` secret sẽ không được ánh xạ (project)

Nếu ```.spec.volumes[].Secret.items``` được sử dụng, chỉ các key được chỉ định trong ```items``` là được ánh xạ. Để sử dụng tất cả các key trong Secret, tất cả chúng phải được liệt kê trong trường ```items```. Tất cả các key được liệt kê phải tồn tại trong Secret tương ứng. Nếu không thì volume sẽ không được tạo ra.

**Quyền truy cập của Secret file**

Ta có thể thiết lập các quyền của truy cập file cho một key của Secret. Nếu ta không chỉ định bất kỳ quyền nào, ```0644``` sẽ được sử dụng theo mặc định. Ta cũng có thể thiết lập chế độ mặc định cho toàn bộ Secret volume và ghi đè trong mỗi key nếu cần.

Ví dụ: ta có thể chỉ định một chế độ mặc định như sau:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/etc/foo"
  volumes:
  - name: foo
    secret:
      secretName: mysecret
      defaultMode: 0400
```

Sau đó, secret sẽ được mount vào ```/etc/foo``` và tất cả các file được tạo bởi secret volume mount sẽ có quyền ```0400```.

Lưu ý rằng đặc tả JSON không hỗ trợ ký hiệu bát phân (octal), vì vậy hãy sử dụng giá trị ```256``` cho quyền ```0400```. Nếu ta sử dụng YAML thay vì JSON cho Pod, ta có thể sử dụng ký hiệu bát phân (octal) để chỉ định các quyền theo cách tự nhiên hơn.

Lưu ý nếu ta chạy lệnh ```kubectl exec``` để vào bên trong Pod, ta cần lần theo symlink để biết được chế độ truy cập thực sự của file. Ví dụ:

Kiểm tra chế độ truy cập file secret trong Pod:

```sh
kubectl exec mypod -it sh

cd /etc/foo
ls -l
```

Đầu ra có dạng

```sh
total 0
lrwxrwxrwx 1 root root 15 May 18 00:18 password -> ..data/password
lrwxrwxrwx 1 root root 15 May 18 00:18 username -> ..data/username
```

Lần theo symlink để tìm đến file và kiểm tra chế độ truy cập của file

```sh
cd ..data
ls -l
```

Đầu ra có dạng

```sh
total 8
-r-------- 1 root root 12 May 18 00:18 password
-r-------- 1 root root  5 May 18 00:18 username
```

Ta cũng có thể sử dụng ánh xạ (mapping) như trong ví dụ trước và chỉ định các quyền khác nhau cho các file khác nhau như sau:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/etc/foo"
  volumes:
  - name: foo
    secret:
      secretName: mysecret
      items:
      - key: username
        path: my-group/my-username
        mode: 0777
```

Trong trường hợp này, file sẽ được ánh xạ tại ```/etc/foo/my-group/my-username``` sẽ có giá trị quyền (permission) là ```0777```. Nếu ta sử dụng JSON thì sẽ là ```511``` tương ứng.

**Sử dụng giá trị Secret từ volume**

Bên trong container có mount secret volume, các secret key xuất hiện dưới dạng file và các secret value đã được giả mã khỏi định dạng Base64 và được lưu trữ bên trong các file này. Đây là kết quả của các lệnh được thực thi bên trong container từ ví dụ trên:

```sh
ls /etc/foo/
```

Đầu ra

```sh
username    password
```

```sh
cat /etc/foo/username
```

Đầu ra

```sh
admin
```

Nhờ đó, ứng dụng trong container có trách nhiệm đọc các secret từ các file trên.

**Các Secret đã mount sẽ được cập nhật tự động**

Khi một Secret (hiện đang được sử dụng trong một volume) được cập nhật, các key được ánh xạ (projected) cũng sẽ được cập nhật theo. kubelet sẽ kiểm tra xem Secret được mount đã được cập nhật chưa mỗi khi thực hiện đồng bộ hóa theo định kỳ. Tuy nhiên, kubelet sẽ sử dụng bộ nhớ đệm cục bộ (local cache) của nó để lấy về giá trị hiện tại của Secret. Loại cache có thể cấu hình được bằng cách sử dụng trường ```ConfigMapAndSecretChangeDetectionStrategy``` trong [KubeletConfiguration struct](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubelet/config/v1beta1/types.go)

Secret có thể được quảng bá bằng cách watch (mặc định), ttl-based hoặc đơn giản là chuyển hướng (redirect) tất cả các yêu cầu trực tiếp đến API server. Kết quả là tổng độ trễ (delay) từ thời điểm Secret được cập nhật đến thời điểm các key mới được ánh xạ (projected) vào Pod chính là thời gian đồng bộ hóa (sync pediod) của kubelet + độ trễ lan truyền cache, trong đó độ trễ lan truyền cache phụ thuộc vào cách Secret được quảng bá (với watch là độ trễ lan truyền watch ; với ttl-based là ttl của cache ; với redirect là 0 tương ứng).

**Secret và ConfigMap bất biến**

Tính năng Kubernetes alpha Secret và ConfigMap bất biến (immutable) cung cấp tùy chọn để thiết lập các Secret và ConfigMap thành bất biến (immutable). Đối với các cluster sử dụng rộng rãi Secret (ít nhất hàng chục nghìn lần mount Secret đến Pod), việc ngăn thay đổi dữ liệu của chúng có các ưu điểm sau:

Bảo vệ ta khỏi các cập nhật vô tình (hoặc không mong muốn) có thể khiến ứng dụng ngừng hoạt động
Cải thiện hiệu năng của cluster bằng cách giảm đáng kể tải trên kube-apiserver, bằng cách đóng các watches của Secret đã được đánh dấu là không thay đổi (immutable).
Để sử dụng tính năng này, hãy kích hoạt ```ImmutableEmphemeralVolumes``` [feature gate](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/) và thiết lập trường ```immutable``` của Secret hoặc ConfigMap thành ```true```

### 2. Sử dụng Secret như là biến môi trường

Để sử dụng Secret như là biến môi trường trong Pod:
- Tạo 1 Secret mới hoặc sử dụng Secret hiện có. Nhiều Pods có thể cùng tham chiếu đến 1 secret
- Chỉnh sửa phần định nghĩa cho mỗi container (trong đặc tả Pod) mà ta muốn sử dụng value của secret key để thêm biến môi trường cho mỗi secret key ta muốn sử dụng. Biến môi trường sử dụng secret key sẽ điền tên của secret và key trong ```env[].ValueFrom.secretKeyRef```.
- Chỉnh sửa container image và/hoặc command line để ứng dụng tìm kiếm value trong biến môi trường được chỉ định

Đây là một ví dụ về Pod sử dụng Secret như biến môi trường

```sh
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec: 
  containers:
  - name: mycontainer
    image: redis
    env:
      - name: SECRET_USERNAME
        valueFrom:
          secretKeyRef:
            name: mysecret
            key: username
      - name: SECRET_PASSWORD
        valueFrom:
          secretKeyRef:
            name: mysecret
            key: password
  restartPolicy: Never
```

**Sử dụng Secret value từ biến môi trường**

Bên trong container sử dụng Secret trong các biến môi trường, các secret key xuất hiện dưới dạng các biến môi trường bình thường chứa các value đã được giải mã khỏi định dạng base64 từ ```data``` của Secret. Đây là kết quả của các lệnh được thực thi bên trong container từ ví dụ trên:

```sh
echo $SECRET_USERNAME
```

Đầu ra:

```sh
admin
```

### 3. Sử dụng imagePullSecrets

Trường ```imagePullSecrets``` là 1 danh sách tham chiếu đến các Secret trong cùng một namespace. Ta có thể sử dụng ```imagePullSecrets``` để truyền một Secret có chứa registry password của Docker image (hoặc loại khác) cho kubelet. kubelet sẽ sử dụng thông tin này để pull về private image thay mặt cho Pod.

**Chỉ định ```imagePullSecret``` thủ công**

Ta có thể tự tạo ```imagePullSecrets``` và tham chiếu nó từ ServiceAccount. Bất kỳ Pods nào được tạo với ServiceAccount đó (hoặc được tạo với ServiceAccount đó theo mặc định), sẽ có trường ```imagePullSecrets``` của chúng được thiết lập như trong ServiceAccount. 

**Tự động mount Secret (được tạo tự động)**

Các Secret được tạo thủ công (ví dụ: secret chứa token để truy cập tài khoản GitHub) có thể được tự động đính kèm vào các pod dựa trên ServiceAccount của chúng.

## Chi tiết

### 1. Những hạn chế

Nguồn Secret volume sẽ được kiểm tra để đảm bảo rằng object tham chiếu đã chỉ định thực sự trỏ đến một object thuộc loại Secret. Do đó, Secret caafnd dược tạo ra trước bất kỳ Pod nào phụ thuộc vào nó.

Tài nguyên Secret nằm trong một namespace. Secret chỉ có thể được tham chiếu bởi Pods trong cùng namespace đó.

Mỗi Secret bị giới hạn ở kích thước 1MiB. Điều này là để ngăn chặn việc tạo ra Secret lớn làm cạn kiệt bộ nhớ API server và bộ nhớ kubelet. Tuy nhiên, việc tạo ra nhiều Secret nhỏ hơn cũng có thể làm cạn kiệt bộ nhớ. Việc giới hạn toàn diện hơn về sử dụng bộ nhớ là do Secret là một tính năng được lên kế hoạch.

kubelet chỉ hỗ trợ việc sử dụng các Secret cho Pods, trong đó các Secret được lấy từ API server. Điều này bao gồm bất kỳ Pods nào được tạo bằng ```kubectl``` hoặc gián tiếp thông qua Replication Controller. Nó không bao gồm các Pod được tạo ra như là kết quả của cờ ``--manifest-url``` hoặc cờ ```--config``` khi chạy kubelet, hoặc REST API (đây không phải cách phổ biến để tạo Pods).

Secret phải được tạo TRƯỚC khi chúng được sử dụng trong Pods dưới dạng các biến môi trường trừ khi chúng được đánh dấu là tùy chọn. Việc tham chiếu đến các Secret không tồn tại sẽ ngăn Pod khởi động.

Các tham chiếu (trường ```secretKeyRef```) đến các key không tồn tại trong Secret cũng sẽ ngăn không cho Pod khởi động.

Các Secret được sử dụng để điền vào các biến môi trường bởi trường ```envFrom``` có các key được xem là tên biến môi trường không hợp lệ thì các key đó sẽ bị bỏ qua. Pod vẫn sẽ được phép khởi động. Tuy nhiên, một sự kiện sẽ được sinh ra với lý do là ```InvalidVariableNames``` và nội dung thông điệp (message) sẽ chứa danh sách các key không hợp lệ đã bị bỏ qua. Ví dụ dưới đây cho thấy một Pod tham chiếu đến ```myscret``` (trong namespace ```default```) có chứa 2 key không hợp lệ là ```1badkey``` và ```2alsobad```

```sh
kubectl get events
```

Đầu ra có dạng:

```sh
LASTSEEN   FIRSTSEEN   COUNT     NAME            KIND      SUBOBJECT                         TYPE      REASON
0s         0s          1         dapi-test-pod   Pod                                         Warning   InvalidEnvironmentVariableNames   kubelet, 127.0.0.1      Keys [1badkey, 2alsobad] from the EnvFrom secret default/mysecret were skipped since they are considered invalid environment variable names.
```

### Tương tác vòng đời giữa Secret và Pod

Khi một Pod được tạo ra bằng cách gọi API của K8s, sẽ không có thao tác kiểm tra xem Secret được tham chiếu đã tồn tại hay chưa. Khi Pod được lập lịch, kubelet sẽ cố gắng lấy về các value của Secret. Nếu Secret không thể được lấy về vì nó không tồn tại hoặc do mất kết nối tạm thời với API server, kubelet sẽ thử lại theo định kỳ. kubelet sẽ báo cáo một sự kiện giải thích lý do Pod chưa được khởi động. Sau khi Secret được lấy về, kubelet sẽ tạo và mount một volume chứa nó. Không có container nào của Pod được khởi động cho đến khi tất cả các volume của Pod được mount.

## Use case

### 1. Sử dụng Secret như là biến môi trường

Viết đặc tả Secret

```sh
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  USER_NAME: YWRtaW4=
  PASSWORD: MWYyZDFlMmU2N2Rm
```

Tạo Secret object

```sh
kubectl apply -f mysecret.yaml
```

Sử dụng ```envFrom``` để định nghĩa tất cả ```data``` của Secret sẽ là các biến môi trường của container. Các key trong Secret sẽ trở thành tên biến môi trường trong Pod

```sh
apiVersion: v1
kind: Pod
metadata:
  name: secret-test-pod
spec:
  containers:
    - name: test-container
      image: k8s.gcr.io/busybox
      command: [ "/bin/sh", "-c", "env" ]
      envFrom:
      - secretRef:
          name: mysecret
  restartPolicy: Never
```

### 2. Pod với SSH key

Tạo Secret có chứa SSH key

```sh
kubectl create secret generic ssh-key-secret --from-file=ssh-privatekey=/path/to/.ssh/id_rsa --from-file=ssh-publickey=/path/to/.ssh/id_rsa.pub
```

Đầu ra:

```sh
secret "ssh-key-secret" created
```

Ta cũng có thể tạo file ```kustomization.yaml``` với trường ```secretGenerator``` có chứa ssh key

Giờ ta có thể tạo một Pod tham chiếu Secret bằng ssh key và sử dụng nó trong volume

```sh
apiVersion: v1
kind: Pod
metadata:
  name: secret-test-pod
  labels:
    name: secret-test
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: ssh-key-secret
  containers:
  - name: ssh-test-container
    image: mySshImage
    volumeMounts:
    - name: secret-volume
      readOnly: true
      mountPath: "/etc/secret-volume"
```

Khi lệnh của container chạy, các phần của key sẽ có sẵn trong:

```sh
/etc/secret-volume/ssh-publickey
/etc/secret-volume/ssh-privatekey
```

Container sau đó được tự do sử dụng dữ liệu Secret để thiết lập kết nối SSH.

### 3. Pod với prod/test credential

Ví dụ này minh họa một pod sử dụng Secret chứa thông tin xác thực (**credential**) cho môi trường production và một Pod khác sử dụng Secret với thông tin xác thực cho môi trường test.

Ta có thể tạo file ```kustomization.yaml``` có trường ```secretGenerator``` hoặc chạy lệnh ```kubectl create secret``` để tạo các Secret sau đây:

```sh
kubectl create secret generic prod-db-secret --from-literal=username=produser --from-literal=password=Y4nys7f11
```

```sh
kubectl create secret generic test-db-secret --from-literal=username=testuser --from-literal=password=iluvtests
```

Tạo 2 pod bằng tệp cấu hình như sau:

```sh
apiVersion: v1
kind: List
items:
- kind: Pod
  apiVersion: v1
  metadata:
    name: prod-db-client-pod
    labels:
      name: prod-db-client
  spec:
    volumes:
    - name: secret-volume
      secret:
        secretName: prod-db-secret
    containers:
    - name: db-client-container
      image: myClientImage
      volumeMounts:
      - name: secret-volume
        readOnly: true
        mountPath: "/etc/secret-volume"
- kind: Pod
  apiVersion: v1
  metadata:
    name: test-db-client-pod
    labels:
      name: test-db-client
  spec:
    volumes:
    - name: secret-volume
      secret:
        secretName: test-db-secret
    containers:
    - name: db-client-container
      image: myClientImage
      volumeMounts:
      - name: secret-volume
        readOnly: true
        mountPath: "/etc/secret-volume"
EOF
```

Tạo pod bằng lệnh ```kubectl apply -f```

Cả hai container sẽ có các file sau đây trên filesystem của chúng với các giá trị tương ứng cho từng môi trường (production & evironment) của container:

```sh
/etc/secret-volume/username
/etc/secret-volume/password
```

Lưu ý đặc tả cho cả 2 Pods chỉ khác nhau một trường duy nhất. Điều này tạo điều kiện cho việc tạo các Pod với các khả năng khác nhau từ một Pod template chung.

Ta có thể đơn giản hóa hơn nữa đặc tả của Pod cơ sở (base) bằng cách sử dụng 2 ServiceAccount sau:
- ```prod-user``` với ```prod-db-secret```
- ```test-user``` với ```test-db-secret```

Đặc tả Pod được rút ngắn thành

```sh
apiVersion: v1
kind: Pod
metadata:
  name: prod-db-client-pod
  labels:
    name: prod-db-client
spec:
  serviceAccount: prod-db-client
  containers:
  - name: db-client-container
    image: myClientImage
```

### 4. dotfile trong secret volume

Ta có làm cho dữ liệu của mình "ẩn" đi bằng cách định nghĩa key bắt đầu bằng dấu chấm (dot). Key này đại diện cho một **dotfile** hoặc file **ẩn**. Ví dụ: khi Secret sau được mount vào một volume:

```sh
apiVersion: v1
kind: Secret
metadata:
  name: dotfile-secret
data:
  .secret-file: dmFsdWUtMg0KDQo=
---
apiVersion: v1
kind: Pod
metadata:
  name: secret-dotfiles-pod
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: dotfile-secret
  containers:
  - name: dotfile-test-container
    image: k8s.gcr.io/busybox
    command:
    - ls
    - "-la"
    - "/etc/secret-volume"
    volumeMounts:
    - name: secret-volume
      readOnly: true
      mountPath: "/etc/secret-volume"
```

Volume sẽ chứa một file duy nhất, có tên là ```.secret-file``` và ```dotfile-test-container``` sẽ có file này xuất hiện tại đường dẫn ```/etc/secret-volume/.secret-file```

### 5. Secret hiển thị cho 1 container trong Pod

Hãy xem xét một chương trình cần xử lý các yêu cầu HTTP, thực hiện một số logic nghiệp vụ phức tạp và sau đó ký một số tin nhắn với một HMAC. Bởi vì nó có logic ứng dụng phức tạp, có thể có một thao tác đọc file từ xa không được chú ý trên server, có thể làm lộ private key cho kẻ tấn công.

Để giải quyết, ta có thể chia thành 2 quy trình trong 2 container:
- ```frontend container``` xử lý tương tác với người dùng và logic nghiệp vụ, nhưng không thể thấy private key.
- ```signer container``` có thể nhìn thấy private key và đáp ứng các yêu cầu ký đơn giản từ frontend (ví dụ: qua mạng localhost)

Với cách tiếp cận được phân vùng này, một kẻ tấn công giờ đây phải đánh lừa máy chủ ứng dụng làm một việc gì đó cần nhiều quyền hơn, điều này có thể khó hơn là bắt nó đọc 1 file.

## Kinh nghiệm thực tiễn

### Client sử dụng Secret API

Khi triển khai các ứng dụng tương tác với Secret API, ta nên giới hạn quyền truy cập bằng các [chính sách ủy quyền](https://kubernetes.io/docs/reference/access-authn-authz/authorization/) như [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

Các Secret thường lưu giữ nhiều giá trị quan trọng, nhiều trong số đó có thể gây ra sự leo thang đặc quyền bên trong K8s (VD: service account token) và cho các hệ thống bên ngoài. Ngay cả khi một ứng dụng riêng lẻ có thể có lý do chính đáng để sử dụng Secret mà nó dự kiến sẽ tương tác, tuy nhiên, các ứng dụng khác trong cùng một namespace có thể khiến những giả định đó không hợp lệ.

Vì những lý do này, các yêu cầu **watch** và **list** Secret trong một namespace là những yêu cầu có khả năng cực kỳ mạnh mẽ và nên tránh, vì việc liệt kê (list) secret cho phép client kiểm tra các giá trị của tất cả các Secret trong namespace đó. Khả năng **watch** và **list** tất cả các Secret trong một cluster chỉ được dành riêng cho các thành phần cấp hệ thống, có đặc quyền nhất.

Các ứng dụng cần truy cập Secret API sẽ thực hiện yêu cầu ```get``` về các Secret chúng cần. Điều này cho phép admin hạn chế quyền truy cập vào tất cả các Secret trong khi vẫn cho phép truy cập vào các instance riêng lẻ trong whitelist mà ứng dụng cần.

Để cải thiện hiệu năng cho một vòng lặp ```get```, client có thể thiết kế các tài nguyên tham chiếu đến Secret sau đó ```watch``` tài nguyên, yêu cầu lại Secret khi tham chiếu thay đổi.

## Các thuộc tính bảo mật

### 1. Protections

Vì các Secret có thể được tạo ra một cách độc lập với các Pod sử dụng chúng nên ít có nguy cơ Secret bị lộ trong quá trình tạo, xem và chỉnh sửa Pods. Hệ thống cũng có thể thực hiện các biện pháp phòng ngừa bổ sung với Secret, chẳng hạn như tránh ghi chúng vào disk nếu có thể.

Một Secret chỉ được gửi đến 1 node nếu 1 Pod trên node đó yêu cầu nó. Các kubelet lưu trữ Secret vào ```tmpfs``` để Secret không được ghi vào disk. Khi Pod phụ thuộc vào Secret bị xóa, kubelet cũng sẽ xóa bản sao cục bộ của Secret data.

Có thể có Secret cho nhiều Pod trên cùng 1 node. Tuy nhiên, chỉ những Secret mà Pod yêu cầu là có thể nhìn thấy được bên trong các container của nó. Do đó, một Pod không có quyền truy cập vào các Secret của một Pod khác.

Có thể có nhiều container trong một Pod. Tuy nhiên, mỗi container trong Pod phải yêu cầu secret volume trong trường ```volumeMounts``` của nó thì mới thấy được trong container. Điều này có thể được sử dụng để xây dựng các phân vùng bảo mật hữu ích ở cấp độ Pod.

Trên hầu hết các bản phân phối K8s, giao tiếp giữa người dùng và API server và từ API server đến các kubelets sẽ được bảo vệ bởi SSL/TLS. Secret sẽ được bảo vệ khi truyền qua các kênh này.

### 2. Mã hóa

Ta có thể kích hoạt [mã hóa](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) cho dữ liệu Secret để các Secret không được lưu trữ ở dạng text vào etcd

### 3. Rủi ro

Trong API server, dữ liệu được lưu trữ trong etcd, vì thế:
- Admin nên kích hoạt **mã hóa** cho dữ liệu của Secret trong cluster
- Admin nên giới hạn quyền truy cập vào etcd chỉ cho Admin thôi
- Admin có thể muốn **wipe/shred** disk được sử dụng bởi etcd khi không còn sử dụng.
- Nếu ta chạy etcd trong cluster, Admin nên đảm bảo sử dụng SSL/TLS cho giao tiếp cho giao tiếp p2p với etcd

Nếu ta cấu hình Secret thông qua file đặc tả (JSON hoặc YAML) có dữ liệu secret được mã hóa theo định dạng base64, việc chia sẻ file này hoặc đưa nó vào kho lưu trữ mã nguồn có nghĩa là Secret đã bị xâm phạm. Mã hóa Base64 không phải là một phương thức mã hóa và chỉ được coi là giống như văn bản thuần túy.

Các ứng dụng vẫn cần bảo vệ giá trị của Secret sau khi đọc nó từ volume, chẳng hạn như không vô tình đăng nhập hoặc truyền nó cho một bên không tin cậy.

Người dùng nào có quyền tạo Pod sử dụng Secret thì cũng có thể thấy giá trị của Secret đó. Ngay cả khi chính sách của API server không cho phép người dùng đó đọc Secret, thì khi người dùng chạy Pod vẫn có thể làm lộ Secret.

Hiện tại, bất kỳ ai có quyền root trên bất kỳ node nào cũng có thể đọc bất kỳ Secret nào từ API server bằng cách mạo danh kubelet. Đây là 1 tính năng được lên kế hoạch để chỉ gửi Secret đến các node thực sự yêu cầu chúng, mục đích là để hạn chế tác động của việc khai thác quyền root trên một node.