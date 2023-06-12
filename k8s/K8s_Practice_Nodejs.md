# Triển khai ứng dụng nodejs trên K8s

Các bước cài đặt trong bài này gồm có:
- Cài đặt môi trường để triển khai app nodejs
- Code một module nodejs nhỏ để kiểm thử
- Build và tạo Docker image cho ứng dụng
- Triển khai ứng dụng lên K8s dùng các file manifest yaml

## Cài đặt môi trường để build Nodejs App (centos 7)

Ta cần một máy chủ để cài đặt môi trường giúp build nodejs app, từ đó mới triển khai lên k8s được

Đầu tiên máy chủ này phải có docker, nodejs và npm.

```sh
sudo yum clean all && sudo yum makecache fast
sudo yum install -y gcc-c++ make
sudo yum install -y nodejs
sudo yum install -y npm
```

## Pull code về

Cài github CLI

```sh
curl -OL https://github.com/cli/cli/releases/download/v1.14.0/gh_1.14.0_linux_amd64.rpm
yum localinstall gh_1.14.0_linux_amd64.rpm
# Login vào github
gh auth login
gh repo clone rockman88v/nodejs-demo-k8s
```

Cơ bản thì app này làm nhiệm vụ sau:
- Gọi vào "/" trả về file index.html, trong đó có cập nhật giá trị các biến môi trường liên qua đến triển khai (POD_NAME, POD_IP,...)
- Gọi vào "/about" hay "/about-us" trả về about.html
- Các request khác thì trả về 404.html

Ở đây đã có sẵn node_muldes rồi, tuy nhiên ta vẫn có thể cài đặt lại bằng ```npm install```

## Build images và push lên registry

Thực hiện build docker:

```sh
docker build -t shaidoka/nodejs-k8s:v1 .
```

Sau đó push lên registry:

```sh
docker push shaidoka/nodejs-k8s:v1
```

## Triển khai lên k8s

Để triển khai lên k8s thì ta sẽ dùng 3 resource chính là deployment, service và ingress:
- Trong cấu hình deployment có gán các biến môi trường lấy từ thông tin metadata của Pod khi deploy lên K8s
- Service cài đặt nodeport 31123 để kết nối trực tiếp qua IP của Node
- Ingress cài đặt ở địa chỉ host là ```nodejs-demo.baotrung.xyz```

Cấu hình **deployment**:

```sh
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nodejs-app
  labels:
    app: nodejs-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nodejs-app
  template:
    metadata:
      labels:
        app: nodejs-app
    spec:
      containers:
        - name: node-app
          image: shaidoka/nodejs-k8s:v1
          imagePullPolicy: Always
          resources:
            # Specifying the resourses that we might need for our application
            limits:
              memory: "128Mi"
              cpu: "500m"
          ports:
            - containerPort: 8080
          env:
            - name: MY_NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: MY_POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: MY_POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: MY_POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
            - name: MY_POD_SERVICE_ACCOUNT
              valueFrom:
                fieldRef:
                  fieldPath: spec.serviceAccountName
```

Cấu hình service

```sh
apiVersion: v1
kind: Service
metadata:
  name: nodejs-service
spec:
  selector:
    app: nodejs-app
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8080
```

Cấu hình ingress

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nodejs-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: nodejs.baotrung.xyz
    http:
      paths:
      - backend:
          service:
            name: nodejs-service
            port:
              name: http
        path: /
        pathType: Prefix
```

Kết quả, truy cập ```nodejs.baotrung.xyz```

![](./images/K8s_Nodejs_1.png)