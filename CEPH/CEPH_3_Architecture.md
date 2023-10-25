# Tìm hiểu về kiến trúc trong CEPH

Ceph storage cluster xây dựng từ các tiến trình service khác nhau. Mỗi tiến trình đều có vai trò riêng trong tính năng của Ceph

Nền tảng Ceph xây dựng dựa trên object, tổ chức object thành các Blocks. Tất cả các kiểu dữ liệu, block, file đều được lưu trên object thuộc Ceph cluster. Object storage là giải pháp thay thế cho hệ thống lưu trữ truyền thống, cho phép xây dựng kiến trúc hạ tầng độc lập với phần cứng. Ceph quản lý trên mức object, nhân bản obj toàn cluster, nâng cao tính bảo đảm. Trong Ceph, object sẽ không tồn tại đường dẫn vật lý, kiến trúc object linh hoạt khi lưu trữ tăng tính mở rộng.

Tuy CEPH có nhiều kiểu tổ chức lưu trữ dữ liệu nhưng ở mức độ nhỏ nhất trong CEPH dữ liệu được lưu trữ thành các object. Phía trên là 1 lớp phủ để quản lý, giao tiếp giữa client dưới dạng object (librados). Tầng trên cùng là các kiểu hỗ trợ client lưu trữ dữ liệu xuống dưới CEPH (CephFS, Block device, Object storage)

![](./images/CEPH_1.jpg)

Service bắt buộc phải có trong Ceph cluster: Ceph MONS, Ceph OSD

**CEPH OSD:** Đây là thành phần lưu trữ dữ liệu thực sự trên các object. Phần lớn hoạt động bên trong Ceph Cluster