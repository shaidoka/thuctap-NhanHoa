# Thêm nội dung vào /etc/hosts của Pod bằng HostAliases

Việc thêm nội dung vào file ```/etc/hosts``` của pod cung cấp cho ta thêm 1 giải pháp để ghi đè hostname ở mức pod khi DNS và các tùy chọn khác không sử dụng được. Ta có thể thêm nội dung tùy chọn thông qua trường ```HostAliases``` trong PodSpec.

Việc chỉnh sửa trực tiếp file ```/etc/hosts``` mà không sử dụng trường ```HostAliases``` là không nên bởi vì file được quản lý bởi kubelet và có thể bị ghi đè trong quá trình tạo/khởi động lại pod.

## Nội dung file hosts mặc định

Ví dụ ta khởi động 1 Nginx pod:

```sh
kubectl run nginx --image nginx --generator=run-pod/v1
```

Kiểm tra địa chỉ IP của pod:

```sh
kubectl get pods --output=wide
```

Output có dạng:

```sh
NAME                   READY   STATUS              RESTARTS   AGE     IP           NODE
nginx                  1/1     Running             0          6s      <none>       k8s-worker2
```

Xem nội dung file ```/etc/hosts```

```sh
kubectl exec nginx -- cat /etc/hosts
```

```sh
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.244.2.3      nginx
```

Mặc định, file ```hosts``` chỉ bao gồm IPv4 và IPv6 cho ```localhost``` và hostname của chính nó.

## Thêm nội dung sử dụng ```hostAliases```

Ngoài các giá trị mặc định, ta có thể thêm các mục khác vào file ```hosts``` . Ví dụ để phân giải ```foo.local```, ```bar.local``` thành ```127.0.0.1``` và ```foo.remote```, ```bar.remote``` thành ```10.1.2.3```, ta có thể cấu hình trường ```HostAliases``` của pod trong phần ```.spec.hostAliases```:

```sh
apiVersion: v1
kind: Pod
metadata:
  name: hostaliases-pod
spec:
  restartPolicy: Never
  hostAliases:
  - ip: "127.0.0.1"
    hostnames:
    - "foo.local"
    - "bar.local"
  - ip: "10.1.2.3"
    hostnames:
    - "foo.remote"
    - "bar.remote"
  containers:
  - name: cat-hosts
    image: busybox
    command:
    - cat
    args:
    - "/etc/hosts"
```

Khi ta kiểm tra nội dung file hosts của pod sẽ có kết quả sau:

```sh
kubectl logs hostaliases-pod
```

```sh
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.244.2.4      hostaliases-pod

# Entries added by HostAliases.
127.0.0.1       foo.local       bar.local
10.1.2.3        foo.remote      bar.remote
```

## Tại sao Kubelet phải quản lý file hosts?

Kubelet quản lý file ```hosts``` cho mỗi container trong Pod để ngăn Docker khỏi chỉnh sửa file sau khi container đã được khởi động. Vì vậy, tuyệt đối tránh thay đổi file hosts 1 cách thủ công.