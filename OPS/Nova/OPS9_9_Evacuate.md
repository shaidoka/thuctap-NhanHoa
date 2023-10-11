# Evacuate - Rebuild máy ảo trong trường hợp Compute bị chết

## I. Giới thiệu

Evacuation là một kỹ thuật được dùng để chuyển máy ảo từ 1 node compute đã chết hoặc bị tắt sang 1 node compute khác ở trong cùng 1 môi trường. Vì thế nó chỉ có tác dụng khi máy ảo sử dụng shared storage hoặc block storage bởi nếu không thì ổ cứng của máy ảo sẽ không thể được truy cập từ bên ngoài trong trường hợp host bị chết. Trong trường hợp rebuild máy ảo được boot từ local sử dụng ephemeral disk thì một máy mới sẽ được tạo mang cùng thông số của máy ảo cũ (IP, ID, flavor,...) nhưng ổ đĩa lúc này đã mất đồng nghĩa với việc dữ liệu cũng không còn nữa.

Evacuation cho phép người dùng lựa chọn host mới, nếu không thì host sẽ được lựa chọn bởi scheduler

Lưu ý rằng bạn chỉ có thể evacuate máy ảo khi host đã bị tắt.

Một số kỹ thuật khác được dùng để vận chuyển máy ảo:
- Tạo một bản copy của máy ảo cho mục đích backup hoặc copy nó tới môi trường / hệ thống mới, sử dụng snapshot (nova image-create)
- Di chuyển máy ảo ở trạng thái static tới host trên cùng 1 môi trường / hệ thống, sử dụng cold migrate (nova migrate)
- Di chuyển máy ảo ở trạng thái đang chạy tới host mới trên cùng 1 môi trường/hệ thống, sử dụng live migrate (nova live-migration)

## II. Workflow khi evacuate máy ảo

