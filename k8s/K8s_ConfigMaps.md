# ConfigMAps trong Kubernetes

ConfigMap là một đối tượng API được sử dụng để lưu trữ dữ liệu không bảo mật trong các cặp key-value. Các pod có thể sử dụng ConfigMaps dưới dạng các biến môi trường, tham số dòng lệnh hoặc dưới dạng file cấu hình trong một volume.

ConfigMap cho phép ta tách rời cấu hình dành riêng cho môi trường khỏi container image để các ứng dụng có thể dễ dàng di chuyển (portable)

**Lưu ý:** ConfigMap không cung cấp bảo mật hoặc mã hóa. Nếu dữ liệu ta muốn lưu trữ là bí mật, hãy sử dụng Secret thay vì ConfigMap hoặc sử dụng các công cụ bổ sung (bên thứ 3) để giữ dữ liệu riêng tư.

## Động lực

Sử dụng ConfigMap để thiết lập dữ liệu cấu hình tách biệt với mã nguồn ứng dụng.

Ví dụ: hãy tưởng tượng rằng ta đang phát triển một ứng dụng có thể chạy trên máy tính riêng của ta (để phát triển) và trên đám mây (để xử lý traffic thực). Ta viết mã để tìm kiếm biến môi trường có tên là ```DATABASE_HOST```. Tại local, ta thiết lập giá trị của biến đó thành ```localhost```. Trong đám mây, ta thiết lập giá trị của biến đó để tham chiếu đến K8s Service đã expose thành phần database trong cluster.

Điều này cho phép ta lấy về container image đang chạy trong đám mây và debug cục bộ nếu cần.

## ConfigMap object

ConfigMap là một đối tượng API cho phép ta lưu trữ cấu hình cho các object khác sử dụng. Không giống như hầu hết các đối tượng K8s có ```spec```, ConfigMap có phần ```data``` để lưu trữ các mục (key) và value của chúng.

## ConfigMap và Pods

Ta có thể viết ```spec``` của Pod tham chiếu đến một ConfigMap và cấu hình các container trong Pod đó dựa trên dữ liệu trong ConfigMap. Pod và ConfigMap phải ở trong cùng một namespace.

Dưới đây là một ví dụ về ConfigMap có một số key chỉ có 1 value và các key khác trong đó value trông giống như 1 đoạn trong file cấu hình

```sh
apiVersion: v1
kind: ConfigMap
metadata: 
  name: game-demo
data:
  # Các keys kiểu thuộc tính (property); mỗi key ánh xạ đến 1 value đơn giản
  player_initial_lives: "3"
  ui_properties_file_name: "user-interface.properties"
  #
  # keys kiểu file
  game.properties: |
    enemy.types=aliens,monsters
    player.maximum-lives=5
  user-interface.properties: |
    color.good=purple
    color.bad=yellow
    allow.textmode=true
```

Có bốn cách khác nhau mà ta có thể sử dụng ConfigMap để cấu hình container bên trong Pod:
- Tham số dòng lệnh đến entrypoint của một container
- Biến môi trường cho một container
- Thêm một file trong volume read-only, để ứng dụng đọc
- Viết mã để chạy trong Pod sử dụng K8s API để đọc ConfigMap

Các phương pháp khác nhau này được sử dụng theo các cách khác nhau để mô hình hóa dữ liệu sẽ được sử dụng. Đối với ba phương thức đầu tiên, kubelet sử dụng dữ liệu từ ConfigMap khi nó khởi chạy (launch) các container của Pod

Phương thức thứ tư có nghĩa là ta phải viết mã để đọc ConfigMap và dữ liệu của nó. Tuy nhiên, vì ta đang sử dụng trực tiếp K8s API, ứng dụng của ta có thể đăng ký để nhận các bản cập nhật bất cứ khi nào ConfigMap thay đổi và phản ứng khi điều đó xảy ra.

Bằng cách truy cập trực tiếp K8s API, kỹ thuật này cũng cho phép ta truy cập vào ConfigMap trong một namespace khác.

Dưới đây là một ví dụ về Pod sử dụng các value từ ConfigMap có tên ```game-demo``` để cấu hình Pod:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: configmap-demo-pod
spec:
  containers:
    - name: demo
      image: game.example/demo-game
      env:
        # Định nghĩa biến môi trường
        - name: PLAYER_INITIAL_LIVES # Ở đây ta sử dụng chữ HOA
                                     # khác với tên của key sử dụng chữ thường trong ConfigMap
          valueFrom:
            configMapKeyRef:
              name: game-demo
              key: player_initial_lives
        - name: UI_PROPERTIES_FILE_NAME
          valueFrom:
            configMapKeyRef:
              name: game-demo
              key: ui_properties_file_name
          volumeMounts:
          - name: config
            mountPath: "/config"
            readOnly: true
      volumes:
        # Ta thiết lập volume ở cấp Pod, sau đó mount chúng vào trong các container bên trong Pod đó
        - name: config
          configMap:
            # Cung cấp tên của ConfigMap ta muốn mount
            name: game-demo
            # Danh sách các key trong ConfigMap để tạo thành file
            items:
            - key: "game.properties"
              path: "game.properties"
            - key: "user-interface.properties"
              path: "user-interface.properties"
```

ConfigMap không phân biệt giữa các giá trị kiểu thuộc tính (property) 1 dòng và giá trị kiểu file đa dòng. Điều quan trọng là làm thế nào để Pods và các đối tượng khác sử dụng những giá trị đó.

Trong ví dụ trên, việc định nghĩa một volume và mount nó vào trong container ```demo``` tại ```/config``` sẽ tạo ra 2 file, ```/config/game.properties``` và ```/config/user-interface.properties```, mặc dù có đến 4 key trong ConfigMap. Điều này là do phần định nghĩa Pod chỉ định một danh sách chỉ có 2 ```items``` trong phần ```volumes```. Nếu ta bỏ qua (để trống) hoàn toàn danh sách ```item``` này thì mọi key trong ```ConfigMap``` sẽ trở thành một file có cùng tên với key và kết quả là ta sẽ có 4 file.

## Sử dụng ConfigMaps

ConfigMaps có thể được mount dưới dạng volume dữ liệu. ConfigMap cũng có thể được sử dụng bởi các phần khác của hệ thống mà không cần phải expose ConfigMap trực tiếp đến Pod. Ví dụ, ConfigMaps có thể chứa dữ liệu mà các phần khác của hệ thống nên sử dụng để cấu hình.

**Lưu ý:** Cách phổ biến nhất để sử dụng ConfigMaps là cấu hình thiết lập cho các container đang chạy trong Pod trong cùng một namespace. Ta cũng có thể sử dụng một ConfigMap riêng biệt. Ví dụ: Ta có thể gặp các addon hoặc operator (một controller đặc biệt để quản lý các tài nguyên tùy biến) để điều chỉnh hành vi của chúng dựa trên ConfigMap.

### Sử dụng ConfigMap như là file từ Pod

Để sử dụng ConfigMap trong một volume bên trong Pod:
- Tạo một configMap mới hoặc sử dụng configMap hiện có. Nhiều Pods có thể tham chiếu đến cùng một một configMap.
- Chỉnh sửa định nghĩa của Pod để thêm volume vào phần ```.spec.volumes[]```. Đặt tên bất kỳ cho volume và thiết lập trường ```.spec.volumes[].ConfigMap.name``` để tham chiếu đến ConfigMap object ở bước 1
- Thêm trường ```.spec.containers[].VolumeMounts[]``` vào mỗi container cần configMap. Chỉ định trường ```.spec.containers[].VolumeMounts[].ReadOnly = true``` và ```spec.containers[].VolumeMounts[].MountPath``` đến tên thư mục chưa được sử dụng, thư mục này chính là nơi ta muốn configMap sẽ xuất hiện
- Chỉnh sửa image hoặc command line để chương trình sẽ tìm kiếm các file trong thư mục đó. Mỗi key trong phần ```data``` của đặc tả configMap sẽ trở thành tên file trong ```mountPath```

Đây là một ví dụ về Pod mount ConfigMap trong volume:

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
    configMap:
      name: myconfigmap
```

Mỗi ConfigMap ta muốn sử dụng cần được tham chiếu trong ```.spec.volumes```

Nếu có nhiều container trong Pod thì mỗi container cần có định nghĩa cho ```volumeMounts``` riêng, nhưng chỉ cần một ```.spec.volumes``` cho mỗi ConfigMap

### ConfigMap đã mount sẽ được tự động cập nhật

Khi một configMap (hiện đang được sử dụng trong một volume) được cập nhật, các key được ánh xạ (projected) cũng sẽ được cập nhật. Kubelet sẽ kiểm tra xem configMap được mount đã được cập nhật chưa mỗi khi thực hiện đồng bộ hóa theo định kỳ. Tuy nhiên, kubelet sẽ sử dụng bộ nhớ đệm cục bộ (local cache) của nó để lấy về giá trị hiện tại của configMap. Loại cache có thể cấu hình được bằng cách sử dụng trường ```ConfigMapAndSecretChangeDetectionStrategy``` trong [KubeletConfiguration struct](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubelet/config/v1beta1/types.go)

ConfigMap có thể được quảng báo bằng cách **watch** (mặc định), **ttl-based** hoặc đơn giản là chuyển hướng (**redirect**) tất cả các yêu cầu trực tiếp đến API server. Kết quả là tổng độ trễ (delay) từ thời điểm ConfigMap được cập nhật đến thời điểm các key mới được ánh xạ (projected) vào Pod chính là thời gian đồng bộ hóa (sync period) của kubelet + độ trễ lan truyền cache, trong đó độ trễ lan truyền cache phụ thuộc vào cách ConfigMap được quảng bá (với **watch** là độ trễ lan truyền watch; **ttl-based** là ttl của cache; **redirect** là 0 tương ứng)

## Secret và ConfigMap bất biến

*Khả dụng từ bản 1.18*

Tính năng K8s alpha Secret và ConfigMap bất biến (immutable) cung cấp tùy chọn để thiết lập các Secret và ConfigMap thành bất biến. Đối với các cluster sử dụng rộng rãi ConfigMap (ít nhất hàng chục nghìn lần mount ConfigMap đến Pod), việc ngăn thay đổi dữ liệu của chúng có các ưu điểm sau:
- Bảo vệ ta khỏi các cập nhật vô tình (hoặc không mong muốn) có thể khiến ứng dụng ngừng hoạt động
- Cải thiện hiệu suất của cluster bằng cách giảm đáng kể tải trên kube-apiserver, bằng cách đóng các **watches** của configMap đã được đánh dấu là không thay đổi (immutable)

Để sử dụng tính năng này, hãy kích hoạt ```ImmutableEmphemeralVolumes``` [feature gate](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/) và thiết lập trường ```immutable``` của Secret hoặc ConfigMap thành ```true```. Ví dụ:

```sh
apiVersion: v1
kind: ConfigMap
metadata:
 ...
data:
 ...
immutable: true
```

**Lưu ý:** Một khi configMap hoặc Secret được đánh dấu là không thay đổi (immutable), ta không thể phục hồi lại thay đổi cũng như không thay đổi nội dung của trường data của configMap được. Ta chỉ có thể xóa và tạo lại ConfigMap. Do các pod hiện có vẫn duy trì mount point với ConfigMap đã bị xóa -> vì vậy ta nên tạo lại các Pod này