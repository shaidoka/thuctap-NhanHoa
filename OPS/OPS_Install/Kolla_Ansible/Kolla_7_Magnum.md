# Magnum - Container cluster service

Magnum là 1 Openstack service mà cung cấp khả năng triển khai và quản lý container cluster như Kubernetes.

## Cấu hình

Enable Magnum, trong ```globals.yml```

```sh
enable_magnum: true
```

### Optional: enable cluster user trust

Điều này cho phép cluster giao tiếp với OpenStack trên phương diện của người dùng mà đã tạo nó, và điều này là cần thiết cho auto-scaler và auto-healer hoạt động. Lưu ý rằng cấu hình này bị tắt đi theo mặc định do nó liên quan đến 1 lỗ hổng [CVE-2016-7404](https://nvd.nist.gov/vuln/detail/CVE-2016-7404). Hãy đảm bảo là bạn đã hiểu hậu quả trước khi enable tùy chọn này:

```sh
enable_cluster_user_trust: true
```

### Optional: private CA

Nếu sử dụng TLS với 1 private CA cho OpenStack public APIs, cluster sẽ cần thêm 1 CA certificate vào truststore của nó để giao tiếp với OpenStack. Certificate phải khả dụng ở trong magnum conductor container. Nó được copy vào cluster thông qua user-data, vì vậy tốt hơn hết là chỉ thêm vào các certificate cần thiết để tránh vượt quá Nova API request body size (điều này có thể được cấu hình thông qua ```[oslo_middleware] max_request_body_size``` trong ```nova.conf``` nếu cần thiết). Trong ```/etc/kolla/config/magnum.conf```:

```sh
[drivers]
openstack_ca_file = <path to CA file>
```

Nếu sử dụng Kolla Ansible để copy CA certificate vào containers, certificates sẽ được đặt ở ```/etc/pki/ca-trust/source/anchors/koll-customca-*.crt```

## Deployment

Để triển khai magnum và dashboard của nó trong 1 cluster OpenStack đã tồn tại:

```sh
kolla-ansible -i <inventory> deploy --tags common,horizon,magnum
```