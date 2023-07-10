# Triển khai Docker mailserver trên K8s

## Các tệp Manifest

### 1. Cấu hình

Chúng ta muốn cung cấp các cấu hình cơ bản trong dạng biến môi trường với 1 ```ConfigMap```. Lưu ý rằng đây chỉ là cấu hình ví dụ, thay đổi ```ConfigMap``` này tùy vào nhu cầu của bạn.

```sh
apiVersion: v1
kind: ConfigMap
metadata:
  name: mailserver.environment
immutable: false
data:
  TLS_LEVEL: modern
  POSTSCREEN_ACTION: drop
  OVERRIDE_HOSTNAME: mail.baotrung.xyz
  FAIL2BAN_BLOCKTYPE: drop
  POSTMASTER_ADDRESS: postmaster@baotrung.xyz
  UPDATE_CHECK_INTERVAL: 10d
  POSTFIX_INET_PROTOCOLS: ipv4
  ONE_DIR: '1'
  ENABLE_CLAMAV: '1'
  ENABLE_POSTGREY: '0'
  ENABLE_FAIL2BAN: '1'
  AMAVIS_LOGLEVEL: '-1'
  SPOOF_PROTECTION: '1'
  MOVE_SPAM_TO_JUNK: '0'
  ENABLE_UPDATE_CHECK: '1'
  ENABLE_UPDATE_CHECK: '1'
  ENABLE_SPAMASSASSIN: '1'
  SUPERVISOR_LOGLEVEL: warn
  SPAMASSASSIN_SPAM_TO_INBOX: '1'

# Cấu hình SSL dưới đây chỉ là ví dụ
  SSL_TYPE: manual
  SSL_CERT_PATH: /secrets/ssl/rsa/tls.crt
  SSL_KEY_PATH: /secrets/ssl/rsa/tls.key
```

### 2. Volume

Chúng ta cần PVC cho dữ liệu:

```sh
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data

spec:
  storageClassName: local-path
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 25Gi
```

### 3. Service

```sh
apiVersion: v1
kind: Service
metadata:
  name: mailserver
  labels:
    app: mailserver
spec:
  type: LoadBalancer
  selector:
    app: mailserver
  ports:
  - name: transfer
    port: 25
    targetPort: transfer
    protocol: TCP
  - name: esmtp-implicit
    port: 465
    targetPort: esmtp-implicit
    protocol: TCP
  - name: esmtp-explicit
    port: 587
    targetPort: esmtp-explicit
    protocol: TCP
  - name: imap-implicit
    port: 993
    targetPort: imap-implicit
    protocol: TCP
```

### 4. Deployment

```sh
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailserver
  annotations:
    ignore-check.kube-linter.io/run-as-non-root: >-
      'mailserver' needs to run as root
    ignore-check.kube.linter.io/privileged-ports: >-
      'mailserver' needs privilegedes ports
    ignore-check.kube-linter.io/no-read-only-root-fs: >-
      There are too many files written to make the root FS read-only

spec:
  replicas: 1
  selector:
  matchLabels:
    app: mailserver
  template:
    metadata:
      labels:
        app: mailserver
      annotations:
        container.apparmor.security.beta.kubernetes.io/mailserver: runtime/default
    spec:
      hostname: mail
      containers:
      - name: mailserver
        image: ghcr.io/docker-mailserver/docker-mailserver:latest
        imagePullPolicy: IfNotPresent

        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFileSystem: false
          runAsUser: 0
          runAsGroup: 0
          runAsNonRoot: false
          privileged: false
          capabilities:
            add:
              - CHOWN
              - FOWNER
              - MKNOD
              - SETGID
              - SETUID
              - DAC_OVERRIDE
              - NET_ADMIN
              - NET_RAW
              - NET_BIND_SERVICE
              - SYS_CHROOT
              - KILL
            drop: [ALL]
          seccompProfile:
            type: RuntimeDefault

        resources:
          requests:
            memory: 2Gi
            cpu: 600m

        volumeMounts:
        - name: data
          mountPath: /var/mail
          subPath: data
          readOnly: false
        - name: data
          mountPath: /var/mail-state
          subPath: state
          readOnly: false
        - name: data
          mountPath: /var/log/mail
          subPath: log
          readOnly: false
        
        - name: certificates-rsa
          mountPath: /secrets/ssl/rsa/
          readOnly: true
        
        - name: tmp-files
          mountPath: /tmp
          readOnly: false
        
        ports:
        - name: transfer
          containerPort: 25
          protocol: TCP
        - name: esmtp-implicit
          containerPort: 465
          protocol: TCP
        - name: esmtp-explicit
          containerPort: 587
        - name: imap-implicit
          containerPort: 993
          protocol: TCP
        
        envFrom:
        - configMapRef:
            name: mailserver.environment
      restartPolicy: Always

      volumes: 
      - name: files
        configMap:
          name: mailserver.files
      - name: data
        persistentVolumeClaim:
          claimName: data
      - name: certificates-rsa
        secret:
          secretName: mail-tls-certificate-rsa
          items:
            - key: tls.key
              path: tls.key
            - key: tls.crt
              path: tls.crt
      - name: tmp-files
        emptyDir: {}
```

### 5. Certificates

Trong ví dụ này, chúng ta sử dụng ```cert-manager``` để cung cấp RSA certificates. Ta cũng có thể sử dụng RSA cert để dự phòng, và cung cấp ECDSA làm certificate chính

```sh
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: mail-tls-certificate-rsa
spec:
  secretName: mail-tls-certificate-rsa
  isCA: false
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
  dnsNames: [mail.baotrung.xyz]
  issuerRef:
    name: mail-issuer
    kind: Issuer
```

### 6. Expose service

K8s cung cấp nhiều cách để expose service, mỗi cách đều có điểm phức tạp riêng. Vấn đề lớn nhất khi expose DMS ra bên ngoài đó là giữ được IP thật của client. IP này được DMS sử dụng để thực hiện kiểm tra SPF - 1 phương thức chống spam không thể thiếu của email server.

Cách tiếp cận đơn giản nhất, bằng cách sử dụng ```externalTrafficPolicy: Local```, điều này sẽ tắt service proxy, nhưng khiến service chỉ khả dụng ở nội bộ. Cách tiếp cận này chỉ hoạt động khi ta nhận được IP chính xác từ 1 load balancer (như MetalLB).

Ta cũng có thể sử dụng 1 load balancer không có external IP và DNAT network traffic đến mail server. Nếu không có 1 IP public dedicated, hãy sử dụng cách này. Còn không thì sử dụng cách trước đó.

#### a. External IPs Service

Đây là cách đơn giản nhất để expose DMS bằng Service với externalIPs. Cách này sẽ cấp phát IP cho service trực tiếp

```sh
apiVersion: v1
kind: Service
metadata:
  name: mailserver
  labels:
    app: mailserver
spec:
  selector:
    app: mailserver
  ports:
  - name: smtp
    port: 25
    targetPort: smtp
  externalIPs:
  - 80.11.12.10
```

Cách tiếp cận này:
- Không giữ được IP thật của client, do đó SPF check sẽ fail
- Yêu cầu chỉ định IP public rõ ràng

#### b. Proxy port đến Service

Proxy pod sẽ giúp ta tránh phải chỉ định external IP rõ ràng. Cách thức này có thể phức tạp, ta phải deploy 1 proxy pod ở mỗi Node mà ta muốn expose DMS

Cách tiếp cận này không giữ được IP thật của client.

#### c. Liên kết với Node cụ thể và sử dụng host network

1 cách để giữ IP thật của client là sử dụng ```hostPort``` và ```hostNetwork: true```. Điều này sẽ giúp ta truy cập DMS thông qua IP của Node mà DMS được deploy

```sh
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailserver
...
    spec:
      hostNetwork: true
      containers:
        ports:
        - name: smtp
          containerPort: 25
          hostPort: 25
        - name: smtp-auth
          containerPort: 587
          hostPort: 587
        - name: imap-secure
          containerPort: 993
          hostPort
...
```

Với cách tiếp cận này:
- Không truy nhập được DMS qua Node khác thuộc cluster, mà chỉ qua Node DMS được triển khai
- Mỗi port trong container sẽ được expose ở phía Host

#### d. Proxy port đến Service thông qua giao thức Proxy

Ý tưởng của cách thức này tương tự với sử dụng 1 proxy pod, nhưng thay vì 1 proxy pod riêng biệt, ta cấu hình ingress để proxy TCP traffic đến DMS pod sử dụng giao thức PROXY, nhờ đó giữ được IP thật của client.

**Cấu hình Ingress**

Với 1 Nginx Ingress Controller, thiết lập ```externalTrafficPolicy: Local``` cho service của nó, và thêm TCP service configmap giống dưới đây (chi tiết về cách làm này ở [đây](https://kubernetes.github.io/ingress-nginx/user-guide/exposing-tcp-udp-services))

```sh
25:  "mailserver/mailserver:25::PROXY"
465: "mailserver/mailserver:465::PROXY"
587: "mailserver/mailserver:587::PROXY"
993: "mailserver/mailserver:993::PROXY"
```

**Cấu hình Mailserver**

Sau đó, cấu hình Postfix và Dovecot để sử dụng giao thức PROXY

```sh
kind: ConfigMap
apiVersion: v1
metadata:
  name: mailserver.config
  labels:
    app: mailserver
data:
  postfix-main.cf: |
    postscreen_upstream_proxy_protocol = haproxy
  postfix-master.cf: |
    smtp/inet/postscreen_upstream_proxy_protocol=haproxy
    submission/inet/smtpd_upstream_proxy_protocol=haproxy
    submissions/inet/smtpd_upstream_proxy_protocol=haproxy
  dovecot.cf: |
    # Assuming your ingress controller is bound to 10.0.0.0/8
    haproxy_trusted_networks = 10.0.0.0/8, 127.0.0.0/8
    service imap-login {
      inet_listener imap {
        haproxy = yes
      }
      inet_listener imaps {
        haproxy = yes
      }
    }
# ...
---

kind: Deployment
apiVersion: apps/v1
metadata:
  name: mailserver
spec:
  template:
    spec:
      containers:
        - name: docker-mailserver
          volumeMounts:
            - name: config
              subPath: postfix-main.cf
              mountPath: /tmp/docker-mailserver/postfix-main.cf
              readOnly: true
            - name: config
              subPath: postfix-master.cf
              mountPath: /tmp/docker-mailserver/postfix-master.cf
              readOnly: true
            - name: config
              subPath: dovecot.cf
              mountPath: /tmp/docker-mailserver/dovecot.cf
              readOnly: true
        volumes: 
        - name: config
          configMap:
            name: mailserver.config
```

Với cách tiếp cận này thì ta sẽ không thể truy cập DMS thông qua cluster-DNS, vì sẽ cần PROXY cho incoming connections.