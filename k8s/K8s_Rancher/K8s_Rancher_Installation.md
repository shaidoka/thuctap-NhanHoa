# Cài đặt Rancher trên baremetal K8s cluster

Bài này sẽ đi nhanh qua các bước cài đặt Rancher lên K8s bằng Helm. Do đó hãy chắc chắn **kubectl** và **helm** đã được cài đặt.

*Lưu ý: Để xem các tùy chọn cho biết cách tùy biến cert-manager install (bao gồm trường hợp cluster sử dụng PodSecurityPolicies), hãy đọc [cert-manager docs](https://artifacthub.io/packages/helm/cert-manager/cert-manager#configuration)*

```sh
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest

kubectl create namespace cattle-system

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.crds.yaml

helm repo add jetstack https://charts.jetstack.io

helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.11.0
```

Lệnh cuối cùng để cài đặt Rancher sẽ được đề cập ở dưới. Lệnh này cần 1 domain name mà trỏ đến máy chủ cài đặt Rancher. Để đơn giản, ta có thể sử dụng 1 domain giả. Ví dụ như ```<IP_OF_LINUX_NODE>.sslip.io```

Để cài đặt 1 phiên bản Rancher chỉ định, sử dụng cờ ```--version```. Nếu không, phiên bản mới nhất sẽ được cài đặt theo mặc định. 

Từ phiên bản K8s v1.25 trở lên, hãy thiết lập ```global.cattle.psp.enabled``` thành ```false```

```sh
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.baotrung.xyz \
  --set replicas=1 \
  --set bootstrapPassword=<PASSWORD_FOR_RANCHER_ADMIN> \
  --set global.cattle.psp.enabled=false

# Windows Powershell
helm install rancher rancher-latest/rancher `
  --namespace cattle-system `
  --set hostname=<IP_OF_LINUX_NODE>.sslip.io `
  --set replicas=1 `
  --set bootstrapPassword=<PASSWORD_FOR_RANCHER_ADMIN>
```

Giờ nếu ta truy cập vào ```<IP_OF_LINUX_NODE>.sslip.io trên web browser, ta sẽ thấy Rancher UI.

Để đơn giản, ta sử dụng domain giả và 1 self-signed certificate cho cài đặt này. Theo đó, ta sẽ cần thêm 1 ngoại lệ bảo mật vào web browser để thấy được Rancher UI. Lưu ý rằng khi cài đặt trong môi trường production, ta sẽ cần 1 high-availability setup với 1 load balancer, domain name và certificate thật.

Cách cài đặt đầy đủ được đề cập ở [Helm CLI installation docs](https://ranchermanager.docs.rancher.com/pages-for-subheaders/install-upgrade-on-a-kubernetes-cluster)

Để khởi chạy K8s cluster mới với Rancher server mới, ta sẽ cần set up cloud credential trong Rancher. Chi tiết sẽ được đề cập sau.

**Rancher hiện tại mới hỗ trợ K8s v1.26 trở xuống**
