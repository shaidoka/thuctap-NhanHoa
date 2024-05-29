# Centralize Logging

1 triển khai OpenStack sinh rất nhiều dữ liệu log. Để thuận tiện hơn cho việc theo dõi và giám sát, cũng như để dễ dàng phát hiện lỗi thì ta sẽ cần 1 giải pháp hiệu quả hơn là SSH và "grep".

## Preparation và deployment

Chỉnh sửa file ```globals.yml``` như sau:

```sh
enable_central_logging: "yes"
```

## OpenSearch

Kolla triển khai OpenSearch để lưu trữ, tổ chức, và khiến log có thể dễ dàng theo dõi hơn

Mặc định thì OpenSearch được triển khai ở port ```9200```

**Lưu ý:** OpenSearch lưu trữ rất nhiều logs, do đó hãy chắc chắn là cấp đủ bộ nhớ cho ```/var/lib/docker```. Hoặc, bạn có thể thay đổi đường dẫn lưu log bằng cách thay đổi biến ```opensearch_datadir_volume```

## Applying log retention policies

Để giảm áp lực cho disk, ta có thể sử dụng Index State Management plugin của OpenSearch để định nghĩa log retention policies. 1 retention policy được áp dụng đến tất cả index mà khớp với ```opensearch_log_index_prefix```. Policy này đầu tiên đóng tất cả index cũ, và sau đó định kỳ xóa chúng đi. Điều này có thể được tùy chỉnh thông qua các biến sau:

- ```opensearch_apply_log_retention_policy```
- ```opensearch_soft_retention_period_days```
- ```opensearch_hard_retention_period_days```

Mặc định chu kỳ soft và hard retention tương ứng là 30 và 60 ngày. Nếu bạn đang nâng cấp từ ElasticSearch, và có cấu hình ```elasticsearch_curator_soft_retention_period_days``` hoặc ```elasticsearch_curator_hard_retention_period_days``` từ trước đó rồi, những biến này sẽ được sử dụng thay vì những biến mặc định. Bạn nên chuyển cấu hình để sử dụng những tên biến mới nếu muốn deploy bản phát hành ```Caracal```.

Nếu bạn muốn cấu hình nâng cao hơn bằng cách ghi đè ```opensearch_retention_policy``` với 1 policy. Hãy xem ở [Index Management plugin documentation](https://opensearch.org/docs/latest/im-plugin/index/) để biết thêm thông tin chi tiết.

### Updating log retention policies

Theo thiết kế, Kolla Ansible sẽ **không** cập nhật 1 retention policy đã tồn tại trong OpenSearch. Điều này để tránh những thay đổi thông qua OpenSearch Dashboards UI, hoặc các công cụ bên ngoài, có thể khiến policy bị xóa sạch.

Có 3 lựa chọn để thay đổi 1 policy đã tồn tại là:

1. Thông qua OpenSearch Dashboards UI. Xem thêm tại [Index Management plugin documentation](https://opensearch.org/docs/latest/im-plugin/index/)

2. Thông qua OpenSearch API sử dụng các công cụ bên ngoài

3. Xóa thủ công policy đã tồn tại thông qua OpenSearch Dashboards UI (hoặc API), trước khi áp dụng lại policy được cập nhật với Kolla Ansible

## OpenSearch Dashboards

Kolla triển khai OpenSearch dashboards để cho phép người quản trị có thể tìm kiếm và hiển thị logs một cách tập trung.

Sau khi triển khai thành công, OpenSearch Dashboards có thể được truy cập bằng trình duyệt web trên địa chỉ ```<kolla_internal_fqdn>:5601``` hoặc ```<kolla_external_fqdn>:5601```

Username mặc định là ```opensearch```, password có thể được dặt dưới ```<opensearch_dashboards_passwords>``` trong ```/etc/kolla/passwords.yml```

Nếu bạn muốn ngăn chặn OpenSearch Dashboards bị exposed ra ngoài external VIP, bạn có thể đặt ```enable_opensearch_dashboards_external``` thành ```false``` trong ```/etc/kolla/globals.yml```

### First Login

Khi OpenSearch Dashboards được mở lần đầu tiên, nó yêu cầu tạo 1 default index pattern. Để xem, phân tích và tìm kiếm logs, ít nhất 1 index pattern phải được tạo. Để khớp index đã lưu trữ trong OpenSearch, chúng tôi khuyến khích sử dụng cấu hình như sau:

1. Index pattern: flog-*

2. Time Filter field name: @timestamp

3. Expand index pattern when searching [DEPRECATED]: not checked

4. Use event times to create index names [DEPRECATED]: not checked

Sau khi thiết lập các tham số, ta có thể tạo 1 index với nút ```Create```

### Search logs - Discover tab

Người quản trị có thể tạo và lưu trữ các kết quả tìm kiếm dựa trên nheiefu trường (field) từ logs, ví dụ, "show all logs marked with ERROR on nova-compute".

Để làm điều này, click vào ```Discover``` tab. Fields từ logs có thể được filter bằng cách di chuột lên trên chúng ở phía bên trái, và chọn ```add``` hoặc ```remove```. Thêm các trường sau:

- Hostname
- Payload
- severity_label
- programname

Bằng cách này ta có thể dễ dàng đọc danh sách các logs từ mỗi node trong cụm. Nếu muốn xem logs giống với khi sử dụng lệnh ```tail```, ta có thể click vào icon hình đồng hồ ở góc phải trên màn hình, sau đó chọn ```Auto-refresh```.

Logs cũng có thể được filter sâu hơn nữa. Để sử dụng ví dụ trên, hãy nhập ```programname:nova-compute``` vào thành tìm kiếm (search bar). Click vào mũi tên trỏ xuống (drop-down arrow) từ 1 trong các kết quả, sau đó nhấn vào hình kính lúp nhỏ bên cạnh trường programname. Giờ nó sẽ hiển thị 1 danh sách tất cả các event từ nova-compute service trong toàn cụm.

Kết quả search hiện tại cũng có thể được lưu bằng cách nhấn vào nút ```Save Search``` ở bên tay phải của menu

### VD: Sử dụng OpenSearch Dashboards để truy vết 1 lỗi thường gặp

Ví dụ sau đây cho thấy cách sử dụng OpenSearch để có thể truy vết 1 lỗi thường gặp trong OpenStack, nơi mà 1 instance không thể hoạt động với thông báo lỗi "No valid host was found"

Đầu tiên, hãy tạo lại server bị lỗi nhưng với tùy chọn ```--debug```:

```sh
openstack --debug server create --image cirros --flavor m1.tiny \
--key-name mykey --nic net-id=00af016f-dffe-4e3c-a9b8-ec52ccd8ea65 \
demo1
```

Trong output dưới đây, hãy để ý key ```X-Compute-Reqeust-Id```. Đây là định danh độc nhất mà có thể sử dụng để theo dõi request trong hệ thống. 1 ID ví dụ sẽ có dạng như này:

```sh
X-Compute-Request-Id: req-c076b50a-6a22-48bf-8810-b9f41176a6d5
```

Lấy giá trị request bên trên vào tìm trong OpenSearch Dashboard, bỏ đi phần tiền tố ```req-```. Giả sử 1 vài filter cơ bản đã được thêm vào như phần bên trên có nói, OpenSearch Dashboards giờ sẽ hiển thị chặng đường mà request này được tạo thông qua các service trong cụm. Bắt đầu từ ```nova-api``` trên control node, đến ```nova-scheduler```, ```nova-conductor```, và cuối cùng là ```nova-compute```. Phân tích ```Payload``` của dòng mà được đánh dấu là ```ERROR``` có thể giúp ta nhanh chóng xác định được vấn đề.

### Visualize data - Visualize tab

Trong visualization tab có hỗ trợ rất nhiều loại Charts. Nếu không có bất kỳ visualization nào được lưu trước đó, hãy tạo 1 cái bằng nút ```Create a new visualization```. Nếu 1 visualization đã được lưu rồi, sau khi vào tab này, visualization mà được chỉnh sửa cuối cùng sẽ được mở lên. Trong trường hợp này, ta có thể tạo 1 visualization mới với nút ```add visualization``` ở menu bên phải. Để tạo visualization mới, 1 trong các tùy chọn sau phải được chọn: pie chart hoặc area chart. Mỗi visualization có thể được tạo từ 1 saved hoặc new search. Sau khi chọn bất kỳ loại search nào, 1 design panel sẽ được mở. Trong panel này, 1 chart có thể được khởi tạo và preview. Trong menu bên tay trái, metrics cho 1 chart có thể được chọn. Chart có thể được sinh bằng cách chọn mũi tên màu xanh ở menu góc trên bên trái

### Exporting and importing created items - Settings tab

Ta có thể export visualization, search, hoặc dashboard đã tạo ra dạng JSON ở tab Settings => Objects. Mỗi item có thể được export riêng biệt bằng cách lựa chọn menu. Tất cả item cũng có thể được export cùng lúc bằng cách chọn ```export everything```.

Thao tác import cũng có thể được thực hiện trong tab Settings => Objects

## Custom log rules

Kolla Ansible tự động deploy Fluentd để forward OpenStack logs từ nhiều node khác nhau về 1 nơi tập trung. Fluentd configuration được chia ra thành 4 phần: Input, forwarding, filtering, và formatting. Những thành phần trên có thể được tùy chỉnh như sau:

### Custom log filtering

Trong vài hoàn cảnh, việc áp dụng một vài bộ lọc vào logs trước khi foward chúng có thể giúp ích rất nhiều. Ví dụ như thêm các tags vào các messages hoặc chỉnh sửa tags để thỏa mãn với 1 log format mà khác với loại đã được định nghĩa bởi kolla-ansible.

Cấu hình custom fluentd filters có thể được thiết lập bằng cách đặt file cấu hình filter trong ```/etc/kolla/config/fluentd/filter/*.conf``` trên control node.

### Custom log formatting

Trong vài hoàn cảnh, việc thực hiện định dạng logs trước khi forward chúng có thể đem lại nhiều lợi ích. Ví dụ, JSON formatter plugin có thể được sử dụng để chuyển định dạng 1 event thành JSON.

Cấu hình custom fluentd formatting có thể thực hiện bằng cách đặt file cấu hình ở ```/etc/kolla/config/fluentd/format/*.conf``` trên control node

### Custom log forwarding

Nếu bạn muốn sử dụng log service khác opensearch, điều này có thể được thực hiện bằng cách tùy chỉnh fluentd outputs.

Để thực hiện điều này, hãy đặt file cấu hình tại ```/etc/kolla/config/fluentd/output/*.conf``` trên control node

### Custom log inputs

Bạn có thể thêm nhiều loại logs đầu vào từ các dịch vụ khác, ví dụ như network. Điều này có thể thực hiện bằng cách đặt file cấu hình ở ```/etc/kolla/config/fluentd/input/*.conf``` trên control node

### Systemd logs

Mặc định, khi bật central logging, chúng ta cũng bật thu thập ```systemd``` logs từ file ```/var/log/journal```.

Để tắt nó đi, hãy đặt tham số ```enable_fluentd_systemd``` thành ```false``` trong ```globals.yml```