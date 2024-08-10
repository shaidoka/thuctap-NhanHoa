# Ring-builder

Sử dụng swift-ring-builder utility để xây dựng và quản lý rings. Tiện ích này chỉ định các partitions đến các thiết bị và ghi 1 cấu trúc Python được tối ưu hóa đến 1 tệp nén gzipped, được tuần tự hóa trên disk để truyền đến servers. Các tiến trình server thỉnh thoảng kiểm tra thời gian chỉnh sửa của file và reload các bản sao chép in-memory của cấu trúc ring nếu cần thiết. Nếu bạn sử dụng 1 phiên bản ring thấp hơn, 1 trong số 3 replicas của một phần partition sẽ không chính xác vì phương thức ring-builder quản lý các thay đổi đến ring. Bạn có thể tìm hiểu cách giải quyết vấn đề này sau.

Ring-builder cũng giữ tệp builder của nó với thông tin ring và các dữ liệu bổ sung khác cần thiết để build cho các rings trong tương lai. Việc giữ nhiều bản backup của những builder files này. 1 lựa chọn là copy các tệp builder ra mọi máy chủ trong khi sao chép chính các tệp ring. Cách khác là upload các builder files vào chính cluster. Nếu bạn mất builder file, bạn sẽ phải tạo ring mới từ đầu. Gần như mọi partitions sẽ được chỉ định đến các thiết bị mới và, do đó, gần như mọi dữ liệu sẽ phải nhân bản đến vị trí mới. Vì vậy, recovery từ 1 builder file đã mất là có thể, nhưng dữ liệu sẽ không thể được tiếp cận trong 1 khoảng thời gian.

## Ring data structure

Ring data structure chứa 3 top-level fields: 1 danh sách các thiết bị trong cluster, 1 danh sách các thiết bị trong ID thiết bị chỉ thị phân vùng đến các thiết bị, và 1 số nguyên chỉ định số bits để shift 1 MD5 hash để tính toán partition cho hash đó.

## Partition asignment list

Đây là 1 danh sách ```array('H')``` của các ID thiết bị. Danh sách ngoài cùng chứa 1 ```array('H')``` cho mỗi replica. Mỗi ```array('H')``` có 1 độ dài bằng với số lượng partition của rng. Mỗi số nguyên trong ```array('H')``` là 1 index trong danh các thiết bị bên trên. Danh sách partition được biết nội bộ trong Ring class như ```_replica2part2dev_id```.

Vì vậy, để tạo 1 danh sách các device dictionaries đã cấp phát đến 1 partition, Python code có thể trông như sau:

```sh
devices = [self.devs[part2dev_id[partition]] for part2dev_id in self._replica2part2dev_id]
```

Dòng code bên trên là rất cơ bản vì nó không tính đến việc loại bỏ các thiết bị trùng lặp. Nếu 1 ring có nhiều replicas hơn devices, 1 partition sẽ có nhiều hơn 1 replica trên 1 device.

```array('H')``` được sử dụng để tiết kiệm memory vì có thể có hàng triệu partitions.

## Overload

Ring builder cố để giữ các replicas càng xa nhau càng tốt trong khi vẫn xem xét đến device weights. Khi nó không thể đảm bảo cho cả 2, yếu tố overload xác định điều gì sẽ xảy ra. Mỗi device sẽ lấy thêm 1 phần phân vùng mong muốn để cho phép phân tán replica; sau khi các phần bổ sung đó cạn kiệt, các replicas được đặt gần nhau hơn là tối ưu.

Overload factor khiến người quản trị đánh đổi việc phân tán replica (độ bền) với phân tán dữ liệu (uniform disk usage)

Giá trị mặc định của overload factor là 0, tức là device weights sẽ được tuân theo.

Với overload factor là 0.1, mỗi device chấp nhận nhiều hơn 10% phân vùng so với bình thường, nhưng chỉ khi điều đó là cần thiết để duy trì partition dispersion.

VD: xem xét 1 cụm có 3 nodes với các disk có dung lượng là tương đồng; node A có 12 disks, node B có 12 disks, và node C là 11 disks. Ring có overload factor là 0.1 (tức 10%). Nếu không có overload, 1 vài phân vùng sẽ chỉ có replicas ở nodes A và B. Tuy nhiên, với overload, mỗi device có thể chấp nhận thêm 10% partitions cho mục đích dispersion. Disk bị thiếu ở node C có nghĩa là sẽ phải có 1 phân vùng có giá trị = 1 disk nhưng trải rộng trên khắp 11 disks còn lại, thứ mà khiến mỗi disk trong node C phải chịu thêm 1/11 = 9.09% tải. Vì con số này ít hơn 10% overload, sẽ có 1 replica của mỗi partition trên mỗi node.

Tuy vậy, điều này có nghĩa là ổ đĩa ở node C có nhiều dữ liệu hơn các ổ đĩa ở node A và B. Nếu chúng ta thiết lập ngưỡng cảnh báo cho dung lượng ổ đĩa của cluster ở ngưỡng 80% thì có nghĩa là disk A và B mới chỉ đầy có 72.7%.

## Replica counts

Để hỗ trợ việc thay đổi số lượng replica, 1 ring có thể có 1 số thực cho replicas.

1 fractional replica count là cho cả ring chứ không giới hạn ở partition. Nó biểu thị con số trung bình replicas cho mỗi partition. VD, 3.2 replica count có nghĩa là 20% partition có 4 replicas, và 80% còn lại có 3 replicas.

Replica count có thể thay đổi bằng lệnh, ví dụ:

```sh
swift-ring-builder account.builder set_replicas 4
swift-ring-builder account.builder rebalance
```

Bạn phải tái cân bằng replica ring sau khi cấu hình lại replica. Người quản trị của những cụm này thường sẽ muốn số replica bằng với số region. Do đó, khi 1 người quản trị thêm hoặc loại bỏ 1 region, họ cũng sẽ thực hiện tương ứng với số lượng replica. Giảm số lượng replicas sẽ giúp tiếp kiệm chi phí cho disk.

Bạn có thể tăng dần dần số lượng replica với 1 tỉ lệ mà không làm ảnh hưởng bất lợi tới hiệu suất của cụm. VD:

```sh
swift-ring-builder object.builder set_replicas 3.01
swift-ring-builder object.builder rebalance
<distribute rings and wait>...

swift-ring-builder object.builder set_replicas 3.02
swift-ring-builder object.builder rebalance
<distribute rings and wait>...
```

Thay đổi sẽ có tác dụng sau khi ring được ```rebalance```. Do đó, nếu bạn muốn thay đổi 3 replicas thành 3.01 nhưng lại lỡ gõ 2.01 thì cũng không làm dữ liệu bị mất đi

Thêm vào đó, ```swift-ring-builder X.builder create``` command giờ cũng có thể chấp nhận đối số dạng thập phân.

## Partition shift value

Partition shift value được biết đến nội bộ đến Ring class là ```_part_shift```. Giá trị này được sử dụng để shift 1 MD5 hash để tính toán partition nơi mà dữ liệu cho hash được đặt. Chỉ có top 4 bytes của hash được sử dụng trong tiến trình này. VD: để tính toán partition cho đường dẫn ```/account/container/object``` sử dụng Python:

```sh
partition = unpack_from('>I',md5('/account/container/object').digest())[0] >>
self._part_shift
```

Với ring mà được tạo với part_power là P, thì partition shift value của nó là 32 - P

## Build the ring

Ring builder process bao gồm những bước chính sau:

1. ring-builder utility tính toán số lượng partitions để cấp phát cho device dựa trên weight của device. VD: cho 1 partition có power là 20, ring có 1,048,576 parttitions. 1000 devices có weight như nhau và mỗi trong số chúng có 1,048,576 parttitions. Các devices được sắp xếp theo số lượng partitions mà chúng muốn, điều này được giữ trong suốt quá trình khởi tạo.

*Lưu ý: Mỗi device cũng được cấp cho 1 con số ```tiebreaker``` ngẫu nhiên mà sẽ được sử dụng khi 2 devices có cùng số lượng partitions. Con số tiebreaker này không lưu trữ ở bất kỳ đâu cả, do đó 2 ring mà có tham số như nhau hoàn toàn có thể có kết quả cấp phát partition khác nhau. Đối với các cấp phát partition có thể lặp lại, ```ringbuilder.rebalance()``` lấy 2 giá trị hạt giống tùy chọn để tạo nên trình sinh số giả ngẫu nhiên của Python*

2. Ring builder cấp phát mỗi partition replica đến device mà cần partition nhất vào thời điểm đó trong khi vẫn giữ chúng càng xa càng tốt với các replicas khác. Ring builder muốn cấp phát 1 replica đến 1 device trong 1 region mà chưa có 1 replica. Nếu không có region như thế khả dụng, ring builder sẽ tìm kiếm 1 device trong 1 zone khác, hoặc trên 1 server khác. Nếu nó vẫn không tìm thấy device mong muốn, nó sẽ tìm đến device mà không có replicas. Cuối cùng, nếu tất cả lựa chọn trên đều cạn kiệt, ring builder cấp phát replica đến device mà có ít replicas đã được cấp phát nhất

*Lưu ý: Ring builder cấp phát nhiều replicas đến 1 device chỉ khi ring có ít devices hơn số lượng replicas*

3. Khi xây dựng 1 ring mới từ 1 ring cũ, ring builder tính toán lại con số partition mong muốn của mỗi device.

4. Ring builder thu hồi partitions và thu thập những partitions này để cấp phát lại, như sau:

- Ring builder thu hồi bất kỳ partition nào đã được cấp phát từ bất kỳ devices đã bị loại bỏ nào và thêm những partition này vào danh sách đã thu thập
- Ring builder thu hồi bất kỳ partition replicas nào mà có thể được mở rộng để tăng độ bền và thêm những partitions này vào danh sách đã thu thập
- Ring builder thu hồi 1 số lượng partitions ngẫu nhiên từ bất kỳ devices nào mà có nhiều partitions hơn lượng chúng cần và thêm những partition này vào danh sách đã thu thập

5. Ring builder cấp phát lại những partition có trong danh sách đã thu thập đến các devices bằng cách tương tự như đã đề cập bên trên

6. Khi ring builder tái cấp phát 1 replica đến 1 partition, ring builder ghi lại thời gian của lần tái cấp phát. Ring builder sử dụng giá trị này khi thu thập partitions cho tái cấp phát, nhờ đó mà không partition nào bị di chuyển 2 lần trong 1 khoảng thời gian (có thể cấu hình được thông qua ```min_part_hours```). Ring builder bỏ qua hạn chế này với các replicas của các partitions trên các devices đã bị loại bỏ vì việc loại bỏ thiết bị chỉ xảy ra trên các device lỗi, và tái cấp phát là lựa chọn duy nhất

Những bước này không phải luôn luôn hoàn hảo để rebalance 1 ring vì tính ngẫu nhiên của việc thu thập partitions để tái cấp phát. Để giúp tiến tới 1 ring cân bằng hơn, hãy lặp lại quá trình rebalance cho tới khi tiệm cận hoàn hảo (cách biệt dưới 1%) hoặc khi giá trị balance không thay đổi ít nhất 1%.