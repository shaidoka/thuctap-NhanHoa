# Tìm hiểu VXLAN - Virtual Extensible LAN

## I. Tổng quan về VXLAN

### 1. Tại sao cần mở rộng VLAN

VLAN sử dụng Spanning Tree Protocol (STP) để ngăn loop, bằng cách chặn các đường dẫn dư thừa. Ngược lại, VXLAN packet được truyền qua mạng dựa trên layer 3 của nó và tận dụng tối đa lợi thế của layer 3 là routing, ECMP, giao thức link aggregation sử dụng các đường dẫn có sẵn.

VLAN vẫn đang được chạy trong các DC nhiều năm nay, nhưng với sự phát triển mạng mẽ của các công nghệ ảo hóa như hiện nay, nhu cầu về VM của khách hàng đang ngày càng tăng. Với VLAN, số lượng ID tối đa là 4096 (12 bit), chưa tính các ID dự trữ và mặc định, thì số lượng này không đủ để đáp ứng cho nhu cầu hiện nay. ID của VXLAN có 24 bit nên số lượng ID lớn hơn nhiều so với VLAN, khoảng 16 triệu ID.

Ngoài ra còn vì sự giới hạn của STP như vấn đề về hội tụ các link/path để xử lý, kích thước bảng MAC và một số đường mạng đang được sử dụng. Trong khi đó, với VXLAN, nó là một giao thức đóng gói MAC trong UDP, được sử dụng để mở rộng một overlay network layer 2 hoặc layer 3 qua layer 3 infrastructure đang tồn tại sẵn.

VXLAN đóng gói cung cấp 1 VNI, 