# Create an Ingress with Basic Authentication for Longhorn UI

Nếu ta cài đặt Longhorn trên K8s cluster với kubectl hoặc Helm, ta sẽ cần phải tạo 1 Ingress để cho phép external traffic có thể đến được Longhorn UI

Authentication không có sẵn khi sử dụng 2 phương pháp cài đặt trên. Do đó bài viết này sẽ mô tả cách để tạo Ingress với basic authentication sử dụng annotation cho nginx ingress controller.

1. Tạo 1 file ```auth```. Tên của file này cần phải là ```auth``` do ta sẽ tạo 1 secret sử dụng key ```data.auth```, nếu không ingress sẽ trả về lỗi 503

```sh
USER=<USERNAME_HERE>; PASSWORD=<PASSWORD_HERE>; echo "${USER}:$(openssl passwd -stdin -apr1 <<< ${PASSWORD})" >> auth
```

2. Tạo secret

```sh
kubectl -n storage create secret generic basic-auth --from-file=auth
```

3. Tạo 1 Ingress manifest ```longhorn-ui-ingress.yaml```

```sh
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: longhorn-ui-ingress
  namespace: storage
  annotations:
    # type of authentication
    nginx.ingress.kubernetes.io/auth-type: basic
    # prevent the controller from redirecting (308) to HTTPS
    nginx.ingress.kubernetes.io/ssl-redirect: 'false'
    # name of the secret that contains the user/password definitions
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    # message to display with an appropriate context why the authentication is required
    nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required'
    # custom max body size for uploading like backing image uploading
    nginx.ingress.kubernetes.io/proxy-body-size: 10000m
spec:
  ingressClassName: nginx
  rules:
  - host: longhorn.baotrung.xyz
    http:
      paths:
      - backend:
          service:
            name: longhorn-frontend
            port:
              name: http
        path: /
        pathType: Prefix
```

4. Apply

```sh
kubectl apply -f longhorn-ui-ingress.yaml
```