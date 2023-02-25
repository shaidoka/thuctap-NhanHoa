# Tổng quan về Pacemaker Corosync

**Pacemaker** là trình quản lý tài nguyên trong cluster được phát triển bởi ClusterLabs. Pacemaker tương thích với rất nhiều dịch vụ phổ biến hiện có và hoàn toàn có thể tự phát triển module để quản lý các tài nguyên mà pacemaker chưa hỗ trợ

Kiến trúc triển khai bởi Pacemaker cho phép tùy biến, hỗ trợ tối đa để các tài nguyên thuộc cluster luôn sẵn sàng. Đồng thời pacemaker có khả năng phát hiện phục hồi các tài nguyên, các node đang xảy ra sự cố thông qua các engine hỗ trợ (Corosync, Heartbeat), cho phép tùy biến theo các kiến trúc khác nhau.

Các tính năng chính của Pacemaker:
- Tự động phát hiện, khôi phục các node, các tài nguyên dịch vụ trên node
- Không yêu cầu chia sẻ không gian lưu trữ (shared storage)
- Tất cả tài nguyên có thể quản lý bằng ```script``` đều có thể quản lý bằng Pacemaker
- Hỗ trợ kỹ thuật ```fencing```, kỹ thuật cô lập tài nguyên trên mỗi node
- Hỗ trợ các cluster từ nhỏ tới lớn
- Hỗ trợ kỹ thuật ```Resource-driven cluster```, kỹ thuật phân cấp/nhóm tài nguyên để quản lý độc lập
- Hỗ trợ kỹ thuật ```Quorate Clusters```, kỹ thuật tính điểm trên các node thuộc cluster, ý tưởng của kỹ thuật là khi cụm lớn bị phân mảnh thành 2 phần, cluster sẽ đánh giá so sánh số điểm của 2 cụm để quyết định cụm nào sẽ tiếp tục chạy, cụm nào sẽ bị đóng băng hoặc tắt hẳn
- Hỗ trợ các thiết lập dự phòng
- Tự động nhân bản cấu hình tới các node thuộc cluster
- Có khả năng nhận thức sự thay đổi trên tài nguyên
- Hỗ trợ các kiểu dịch vụ nâng cao:
  - Nhân bản (clone): dịch vụ được nhân bản tới nhiều node để tăng tính sẵn sàng
  - Đa trạng thái (multi-state): dịch vụ có nhiều trạng thái (master/slave hoặc primary/secondary)
- Thống nhất quản trị cluster qua các công cụ hỗ trợ

**Corosync** hay **Corosync Cluster Engine** là dự án mã nguồn mở bắt nguồn từ dự án OpenAIS. Mục đích phát triển của Corosync là tạo ra hệ thống có tính liên kết, cung cấp tính sẵn sàng cao cho các cho các ứng dụng chạy trên đó

**Corosync** cung cấp 4 API viết bằng ngôn ngữu C:
- Nhóm các tiến trình thành mô hình khép kín, đảm bảo trạng thái tiến trình nhân rộng trong nhóm
- Cung cấp trình quản trị đơn giản cho phép khởi động lại tiến trình ứng dụng khi chúng xảy ra sự cố
- Cung cấp cơ sở dữ liệu bộ nhớ (in-memory database) lưu trữ các cấu hình, thống kê trạng thái. Cho phép truy vấn, thiết lập, nhận thông báo khi thay đổi
- Cung cấp hệ thống quorum, cảnh báo khi có hoặc mất quorm

## Kiến trúc Pacemaker

Theo kiến trúc Pacemaker, Cluster được tạo từ 3 thành phần:
- Các thành phần cluster không thể nhận biết (non-cluster-aware components): các thành phần được script hóa để có thể tắt, bật, giám sát
- Quản lý tài nguyên (Resource management): Pacemaker cung cấp trung tâm giám sát, phản ứng với các sự kiện xảy ra trong cluster. Các event có thể là các node bị loại bỏ hay tham gia vào cụm, các thao tác quản trị cơ bản. Pacemaker sẽ nhận thức, tự động đánh giá trạng thái lý tưởng cho cụm, ra chỉ thị cho cụm trở lại trạng thái lý tưởng (tự động di chuyển tài nguyên, loại bỏ thành phần lỗi bằng cách tắt dịch vụ hoặc tắt hẳn node)
- Low-level infrastructure: các project như corosync, CMAN, Heartbeat cung cấp các tin nhắn tin cậy về thông tin tài nguyên, node, quorum của cụm

Kết hợp Corosync + Pacemaker cho phép cluster quản trị các Cluster Filesystem tiêu chuẩn. Tính năng này được phát triển từ tiêu chuẩn ```distributed lock manager``` trên các hệ thống Cluster Filesystem mã nguồn mở, từ đó cho phép corosync thu thập sự kiện về tính trạng các node thuộc cluster filesystem và cho phép Pacemaker ra lệnh cô lập dịch vụ tại các node.

![](./images/Cluster_pacemaker_structure.png)

## Các thành phần nội tại

Pacemaker chia thành 5 thành phần chính:
- **Cluster Information Base (CIB)**: CIB sử dụng XML để thể hiện cấu hình cluster cũng như trạng thái hiện tại của các tài nguyên bên trong cluster. Nội dung của CIB tự động đồng bộ tới tất cả các node trên toàn cluster, đồng thời sử dụng PEngine để đánh giá trạng thái lý tưởng của Cluster và cách để đạt trạng thái lý tưởng
- **Cluster Resource Management Daemon (CRMd)**: Các thao tác tới tài nguyên thuộc Cluster được định tuyến thông qua tiến trình này. Tiến trình cho phép truy vấn thông tin, di chuyển, khởi tạo, thay đổi trạng thái khi cần
- **Local Resource Management daemon (LRMd)**: Mỗi node thuộc cluster chạy tiến trình ```local resource management daemon``` (LRMd), tiến trình này như giao diện giữa CRMd với các tài nguyên nội tại của node. Tiến trình LRMd sẽ chuyển chỉ thị từ CRMd tới các thành phần tài nguyên nó quản lý
- **Policy Engine (PEngine)**: Chịu trách nhiệm tính toán trạng thái lý tưởng của cụm, ra chỉ thị, kịch bản cho CRMd để hiện thực hóa trạng thái mong muốn
- **Shoot the Other Node in the Head (STONITH)**: Giải pháp cho các node "cứng đầu" không chịu phản hồi, không nhận chỉ thị mềm, CRMd sẽ chỉ thị cho STONITH tắt nóng, hoặc khởi động lại trực tiếp thông qua phần cứng (IPMI, IDRAC, ILO,...)

![](./images/Cluster_pacemaker_components.png)

## Các kiểu Cluster hỗ trợ

Pacemaker hỗ trợ bất kể các kiểu Cluster nào, bao gồm:
- Active - Active
- Active - Passive
- N + 1
- N + M
- N to 1
- N to M

Mô hình:

![](./images/Cluster_pacemaker_active_active.png)

![](./images/Cluster_pacemaker_active_passive.png)

![](./images/Cluster_pacemaker_shared_failover.png)