# Giới thiệu tổng quan về giải pháp lưu trữ CEPH

```Ceph``` là 1 project mã nguồn mở, cung cấp giải pháp data storage. CEPH cung cấp hệ thống lưu trữ phân tán mạnh mẽ, tính mở rộng, hiệu năng cao và khả năng chịu lỗi cao. Xuất phát từ mục tiêu, CEPH được thiết kế với khả năng mở rộng cao, hỗ trợ lưu trữ tới mức exabyte cùng với tính tương thích cao với các phần cứng có sẵn.

## Lịch sử hình thành

**03/07/2012 - Argonaut:** team CEPH đã phát triển và release bản Argonaut, bản phát hành "ổn định" lớn đầu tiên của CEPH. Bản phát hành này chỉ nhận được các cập nhật sửa lỗi ổn định và cập nhật hiệu suất và các tính năng mới sẽ được lên lịch cho các bản phát hành trong tương lai

**01/01/2012 - Bobtail:** team CEPH phát triển và released bản Bobtail, bản phát hành ổn định lần thứ 2 của CEPH. Bản phát hành này tập trung chủ yếu vào sự ổn định, hiệu suất và khả năng nâng cấp từ loạt ổn định Argonaut trước đó

**07/05/2013 - Cuttlefish:** team CEPH đã phát triển và release bản Cuttlefish, bản phát hành ổn định lần thứ 3 của CEPH. Bản này gồm 1 số cải tiến về tính năng và hiệu suất cũng như là bản phát hành ổn định đầu tiên có công cụ triển khai "ceph-deploy" để thay đổi phương thức triển khai "mkcephfs" trước đó

**14/08/2013 - Dumpling:** Bản này bao gồm thêm global namespace, region support, REST API cho việc giám sát

**09/01/2013 - Emperor:** bản này cung cấp tính năng mới là multi-datacenter replication cho RADOSgw, cải thiện khả năng sử dụng và đạt được nhiều hiệu suất gia tăng và công việc tái cấu trúc nội bộ để hỗ trợ các tính năng sắp tới trong Firefly

**07/05/2014 - Firefly:** bản ra mắt tính năng mã hóa, phân vùng bộ đệm (cache tiering), thử nghiệm thêm key/value OSD backend

**29/10/2014 - Giant**

**07/04/2015 - Hammer**

**06/01/2015 - Infernalis**

**21/04/2016 - Jewel:** phiên bản major đầu tiên của CEPH mà được coi là thực sự ổn định. Các công cụ CephFS repair, disaster recovery tools đã được hoàn thành, một số chức năng bị tắt theo mặc định. Bản này bao gồm phụ trợ RADOS thử nghiệm mới có tên là BlueStore, được lên kế hoạch làm phụ trợ lưu trữ mặc định trong các bản phát hành sắp tới

**20/01/2017 - Kraken:** nhóm phát triển CEPH đã phát hành Kraken. Định dạng lưu trữ BlueStore mới, được giới thiệu trong Jewel, hiện có định dạng trên disk ổn định và là 1 phần của bộ thử nghiệm. Mặc dù vẫn được đánh dấu là thử nghiệm, BlueStore đã sẵn sàng phát triển và nên được đánh dấu như vậy trong bản tiếp theo là Luminous

**29/08/2017 - Luminous:** nhóm phát triển CEPH đã phát hành Luminous. Trong số các tính năng khác, định dạng lưu trữ BlueStore (sử dụng raw disk thay vì hệ thống filesystem) hiện được coi là ổn định và được khuyến nghị sử dụng

**01/06/2018 - Mimic:** phát hành bản Mimic. Với việc phát hành Mimic, snapshots hiện ổn định khi kết hợp với multiple MDS daemons và RESTful gateways frontend Beast được tuyên bố là ổn định và sẵn sàng để sử dụng

**19/03/2019 - Nautilus**

## Các tính năng quan trọng của CEPH

Hiện nay, các nền tảng hạ tầng đám mây, public, private, hybrid cloud dần trở nên phổ biến và to lớn. CEPH trở thành giải pháp nổi bật cho các vấn đề đang gặp phải

Các yêu cầu mong muốn của 1 hệ thống lưu trữ (storage):
- Sử dụng thay thế lưu trữ trên ổ đĩa server thông thường
- Sử dụng để backup, lưu trữ an toàn
- Sử dụng để thực hiện triển khai các dịch vụ HA khác như LB cho Webserver, DB Replication,...
- Xây dựng Storage giải quyết bài toán lưu trữ cho Cloud hoặc phát triển Cloud Storage