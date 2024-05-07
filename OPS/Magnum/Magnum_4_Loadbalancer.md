# Kubernetes External Loadbalancer in Openstack

Trong 1 K8s cluster, tất cả masters và minions đều phải kết nối tới 1 Neutron private subnet, subnet này sau đó mới kết nối đến 1 router và đi ra ngoài mạng public. Điều này cho phép các node có thể giao tiếp với nhau và với mạng bên ngoài.

Tất cả K8s pods và service được tạo trong cluster đều kết nối đến 1 private container network, mặc định là Flannel, lúc này 1 overlay network sẽ được đặt trên Neutron private subnet. Các pods và services được cấp các địa chỉ IP từ container network này và chúng có thể giao tiếp với nhau và với mạng bên ngoài. Tuy vậy, những IP này không thể được truy cập từ internet.

Để công khai 1 service endpoint ra bên ngoài, K8s cung cấp 1 tính năng gọi là external load balancer. Điều này được đơn giản thực hiện thông qua thuộc tính "type: LoadBalancer" trong file manifest của service. Khi service được tạo, K8s sẽ thêm 1 external load balancer lên phía trước service, nhờ đó mà service có thêm 1 external IP address bên cạnh internal IP address. Service endpoint có thể được truy nhập thông qua địa chỉ IP public.

1 K8s cluster được triển khai bởi Magnum sẽ có tất cả cấu hình cần thiết cho external loadbalancer. Bài viết này mô tả cách sử dụng tính năng đó.

## Steps for the cluster administrator

Vì K8s master cần giao tiếp với OpenStack để tạo và quản lý Neutron load balancer, chúng ta cần cung cấp 1 credentials cho K8s để nó sử dụng.

Trong phiên bản hiện tại, cluster administrator sẽ phải tự thực hiện bước này. Các nhà phát triển của OpenStack sẽ cố gắng khiến Magnum tự động nó trong tương lai. Điều này có nghĩa là, sau khi K8s cluster được khởi tạo, loadbalancer sẽ không có sẵn. Nếu người quản trị không muốn enable feature này, tất cả service vẫn sẽ được tạo bình thường, services mà được khai báo với kiểu load balancer cũng sẽ được tạo thành công, nhưng không có load balancer nào được tạo ra cả.

Lưu ý rằng, các phiên bản K8s khác nhau thì cũng cần những phiên bản Neutron LBaaS khác nhau.

Trước khi enable K8s loadbalancer feature, hãy chắc chắn rằng Openstack instance đang chạy phiên bản Neutron LBaaS phù hợp. Để xác định điều này