# Phân phối Cluster IP Service

Ở K8s, Services là 1 phương thức ảo để expose 1 ứng dụng đang chạy trên 1 tập Pod. Nhiều service có thể có virtual IP address trong phạm vi cluster (sử dụng Service ```type: ClusterIP```). Client có thể kết nối sử dụng địa chỉ virutal IP đó, và K8s sau đó cân bằng tải traffic đến Service thông qua các backing Pod.

## Cách ClusterIP được phân phối

Khi K8s cần gán 1 virtual IP cho 1 Service, hành động đó có thể thực hiện theo 2 phương thức:
- **Dynamically:** Control plane tự động chọn 1 IP address không sử dụng từ dải IP được cấu hình và gán nó cho Service sử dụng ```type: ClusterIP```
- **Statically:** Người dùng chỉ định 1 IP tùy chọn (từ dải IP đã cấu hình) và gán nó cho Service

Trong cả cluster, mỗi Service ```ClusterIP``` sẽ có 1 địa chỉ duy nhất. Nếu ta cố gắng tạo 1 Service với ```ClusterIP``` chỉ định đã tồn tại sẽ khiến việc phân phối IP trả về lỗi.

## Tại sao ta cần reserve 1 vài ClusterIP?

Đôi khi ta sẽ muốn sử dụng Service chạy 1 địa chỉ IP thường-đặt-như-thế, từ đó các thành phần và users trong cluster có thể sử dụng chúng.

Ví dụ như dịch vụ DNS trong cluster. Như một quy ước ngầm định, ta thường muốn gán địa chỉ IP thứ 10 từ dải IP cho dịch vụ DNS. Giả sử dụng ta cấu hình dải IP cho service là 10.96.0.0/16 và muốn DNS Service IP là 10.96.0.10, file cấu hình yaml đó sẽ như này:

```sh
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: kube-dns
    kubernetes.io/cluster-service: "true"
    kubernetes.io/name: CoreDNS
  name: kube-dns
  namespace: kube-system
spec:
  clusterIP: 10.96.0.10
  ports:
  - name: dns
    port: 53
    protocol: UDP
    targetPort: 53
  - name: dns-tcp
    port: 53
    protocol: TCP
    targetPort: 53
  - name: dns-tcp
    port: 53
    protocol: TCP
    targetPort: 53
  selector:
    k8s-app: kube-dns
  type: ClusterIP
```

Nhưng như đã đề cập bên trên, IP 10.96.0.10 chưa được reserve, do đó Service khác có thể khởi tạo từ trước và sử dụng IP này, do đó việc khởi tạo DNS Service sẽ gặp lỗi.

## Tránh Service ClusterIP conflict như nào?

Phương thức phân phối ClusterIP của K8s vốn được thiết kế để giảm nguy cơ mâu thuẫn trong quá trình phân phối IP.

Dải ```ClusterIP``` được chia ra, theo công thức sau: ```min(max(16, cidrSize / 16)), 256```, điều này giúp dải giá trị không bao giờ nhỏ hơn 16 và lớn hơn 256.

Phương thức phân phối Dynamic IP sẽ sử dụng dải bên trên theo mặc định, khi hết dải này, nó mới sử dụng đến dải bên dưới. Điều này có nghĩa là người dùng có thể sử dụng phân phối IP static trên dải IP dưới giúp tránh mâu thuẫn.

### Ví dụ

**VD1:** Ví dụ này sử dụng dải IP 10.96.0.0/24 cho Service. Hãy cùng tính toán 1 chút:

Độ rộng dải: 2^8 - 2 = 254
Độ lệch dải: ```min(max(16, 256/16), 256) = min (16, 256) = 16```
Bắt đầu dải tĩnh: 10.96.0.1
Kết thúc dải tĩnh: 10.96.0.16
Kết thúc dải: 10.96.0.254

**VD2:** Ví dụ này sẽ sử dụng dải IP 10.96.0.0/20, tiếp tục tính toán nào:

Độ rộng dải: 2^12 - 2 = 4094
Độ lệch dải: ```min(max(16, 4096/16), 256)``` = ```min(256, 256)``` = 256
Bắt đầu dải tĩnh: 10.96.0.1
Kết thúc dải tĩnh: 10.96.1.0
Kết thúc dải: 10.96.15.254

**VD3:** Ví dụ này sử dụng dải 10.96.0.0/16, lại lôi máy tính ra tiếp:

Độ rộng dải: 2^16 - 2 = 65534
Độ lệch dải: ```min(max(16, 65536/16), 256) = min(4096, 256) = 256
Bắt đầu dải tĩnh: 10.96.0.1
Kết thúc dải tĩnh: 10.96.1.0
Kết thúc dải: 10.96.255.254