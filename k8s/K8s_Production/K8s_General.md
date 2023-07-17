# Tài liệu backup, restore, kiểm thử các trường hợp lỗi K8s

## I. Backup PVC/PV

Persistent Volume trong K8s là 1 trong những thành phần cần được backup thường xuyên do chứa dữ liệu chính của ứng dụng cũng như có thể là nhiều thông tin về cấu hình khác.

Trong cluster K8s này, chúng ta sử dụng Longhorn để quản lý PV/PVC, do đó tính năng backup/restore cũng sẽ được khai thác từ volume controller này.

Chi tiết xem tại: [Longhorn]