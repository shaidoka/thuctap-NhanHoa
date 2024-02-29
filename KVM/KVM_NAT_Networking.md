# KVM default NAT-based networking

NAT-based networking thường được cung cấp và enable mặc định bởi hầu hết các bản phân phối Linux mà hỗ trợ KVM virtualization.

Cấu hình network này sử dụng 1 Linux bridge kết hợp với Network Address Translation (NAT) để cho phép 1 guest OS có thể kết nối ra ngoài được, bất kể loại network là gì (có dây, không dây, dial-up,...).

Giống với các lựa chọn bridge mềm khác, NAT-based networking cho phép các KVM guest chia sẻ cùng bridge để giao tiếp ngay cả khi nếu bridge này không kết nối đến 1 interface nào ở KVM host, hoặc nếu KVM host không có network vật lý nào được thiết lập.

Trong khi NAT là 1 lựa chọn rất thuận tiện và linh hoạt, cho phép 1 guest OS dễ dàng kết nối đến mạng internet, thì nó lại có đặc điểm khiến nó có thể kém hợp lý hơn trong nhiều trường hợp hay trong doanh nghiệp.

Đầu tiên, mặc định, bridge mà cấu hình cho NAT-based connectivity thường sử dụng private IP từ dải ```192.168.x.x```. Địa chỉ trong dải này không được phân phối cho bất kỳ tổ chức cụ thể nào cả và bất kể ai sử dụng chúng đồng nghĩa với chưa được sự đồng thuận của regional Internet registry. Sử dụng 1 dải ```192.168.x.x``` cho phép 1 bản phân phối Linux tránh đi nhiều tasks và sự phức tạp khi cấu hình liên quan tới tiết kiệm tài nguyên và quản lý (thứ được cho là nhức nhối hàng đầu ở thời điểm hiện tại).

Thứ 2, các interfaces mà sử dụng NAT, mặc định sẽ không nhìn thấy được bên ngoài host KVM. Điều này có nghĩa là các hệ thống bên ngoài và các thành phần mạng của chúng không biết được cách để định tuyến traffic đến 1 KVM guest OS trên KVM host riêng biệt.

Thứ 3, việc sử dụng NAT cùng bridge sẽ tạo thêm các phát sinh, thứ mà sẽ ảnh hưởng đến thông lượng hay độ trễ của mạng, cũng như tăng mức tiêu thụ CPU và memory của máy chủ. Hành vi của NAT thường được hiện thực hóa bằng cách sử dụng Linux firewall bằng các quy tắc static và dynamic. Việc sử dụng firewall đặt ra các yêu cầu bổ sung cho hệ thống.

Với hầu hết các bản phân phối Linux, NAT-based networking thường được cấu hình và khả dụng theo mặc định khi OS được cài đặt. Thông thường, tên của NAT bridge mặc định là ```virbr0``` và tên của network mặc định là ```default```.

Để liệt kê network nào được định nghĩa với libvirt daemon cho KVM guest sử dụng, có thể dùng lệnh sau:

```sh
virsh net-list
```

KVM guest muốn sử dụng NAT bridge mặc định sẽ cần thêm hoặc chỉnh sửa phần network trong libvirt XML configuration file, ví dụ:

```sh
<interface type="bridge"> 
    <source bridge="bridge-name"/>
    <model type="virtio"/>
    <driver name="vhost"/>
</interface>
```

Để định nghĩa 1 NAT bridge mới, hãy sử dụng các bước sau:

1. Tạo 1 libvirt network mới  với cấu hình như sau:

```sh
vi ~/new-kvm-network.xml
<network>
  <name>newnatnetwork</name>
  <forward mode='nat' dev='br0' />
  <bridge name='nat-bridge' stp='on' delay='0'/>
  <ip address='192.168.0.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.0.2' end='192.168.0.254'/>
    </dhcp>
  </ip>
</network>
```

Lưu ý là tên và IP addres của bridge có thể tùy chỉnh được, nhưng nên tránh trùng với tên của bridge mặc định (```virbr0```) và IP của bridge đó (```192.168.122.1```).

2. Thêm network mới bằng cách định nghĩa file XML vừa tạo:

```sh
virsh net-define ~/new-kvm-network.xml
```

3. Thiết lập khởi động cùng hệ thống:

```sh
virsh net-start nat-bridge
virsh net-autostart nat-bridge
```

4. Thêm hoặc thay đổi thiết lập của KVM guest để sử dụng network hoặc bridge này

Để xem chi tiết cấu hình của 1 network cụ thể được định nghĩa trong libvirt, hãy sử dụng lệnh sau:

```sh
virsh net-dumpxml 
```