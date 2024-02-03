# Cài đặt Jenkins trên Kubernetes

## I. Kubernetes

Kubernetes (K8s) là 1 hệ thống mã nguồn mở để tự động triển khai, mở rộng, và quản lý các ứng dụng đặt trong container.

Một K8s cluster thêm vào 1 lớp tự động hóa mới vào Jenkins. K8s đảm bảo rằng tài nguyên được sử dụng có hiệu quả và máy chủ của bạn sẽ không bị quá tải. Kubernetes cho phép điều phối container giúp Jenkins luôn luôn có đủ lượng tài nguyên cần thiết để hoạt động.

Cài đặt Jenkins trên Kubernetes Cluster phù hợp với những triển khai dựa trên Kubernetes và container. Trong bài viết này, chúng ta sẽ tìm hiểu từng bước để cài đặt Jenkins trên cụm K8s.

## II. Cài đặt Jenkins trên Kubernetes

Tổng quan, để cài đặt Jenkins trên K8s, chúng ta sẽ cần các bước sau:

1. Tạo 1 **Namespace**

2. Tạo 1 **service account** với quyền Kubernetes **admin**

3. Tạo **local persistent volume** để lưu dữ liệu cho Jenkins

4. Tạo 1 **deployment** để triển khai Jenkins

5. Tạo 1 **service** truy cập vào Jenkins

**Lưu ý:** Bên trên là các bước cơ bản để deploy Jenkins, tuy nhiên trong bài này sẽ **không** sử dụng persistent volume

### Jenkins Kubernetes Manifest files

Tất cả các tệp manifest của Jenkins Kubernetes được sử dụng trong bài này đều công khai trên GitHub. Bạn hoàn toàn có thể clone nó về với git

```sh
git clone https://github.com/scriptcamp/kubernetes-jenkins
```

### Kubernetes Jenkins Deployment

Hãy bắt đầu với việc triển khai Jenkins lên K8s

**Bước 1:** Tạo 1 Namespace cho Jenkins. Phân chia rạch ròi từng công cụ DevOps trên các namespaces khác nhau là 1 thói quen tốt, hãy ghi nhớ điều đó.

```sh
kubectl create ns devops-tools
```

**Bước 2:** Tạo 1 tệp ```serviceAccount.yaml``` với nội dung như dưới đây

```sh
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: jenkins-admin
rules:
  - apiGroups: [""]
    resources: ["*"]
    verbs: ["*"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins-admin
  namespace: devops-tools
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jenkins-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: jenkins-admin
subjects:
- kind: ServiceAccount
  name: jenkins-admin
  namespace: devops-tools
```

Tệp manifest bên trên tạo 1 ClusterRole, ServiceAccount, ClusterRoleBinding với cùng tên ```jenkins-admin```.

Cluster Role ```jenkins-admin``` sẽ có tất cả quyền để quản lý các thành phần trong cụm. Bạn có thể hạn chế điều này bằng cách chỉ định chính xác resource và action (verb) mong muốn.

Áp dụng tệp manifest trên bằng lệnh:

```sh
kubectl apply -f serviceAccount.yaml
```

**Bước 3:** Tạo 