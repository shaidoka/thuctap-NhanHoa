# Giao thức DHCP

#### Giới thiệu chung

DHCP (hay Dynamic Host Configuration Protocol) là giao thức hoạt động ở lớp Application trong mô hình TCP/IP. DHCP cấu hình tự động địa chỉ IP, DHCP có 2 version: cho IPv4 và IPv6, sử dụng port 67, 68 và dùng giao thức UDP

DHCP Server cấp địa chỉ mạng, phân phối thông số cấu hình tương ứng cho client

DHCP hỗ trợ 3 cơ chế cấp địa chỉ IP:
- Cấp tự động: DHCP gán 1 địa chỉ IP thường trực cho 1 client
- Cấp động: DHCP gán địa chỉ IP cho 1 khoảng thời gian hữu hạn nào đó
- Cấp thủ công: 1 địa chỉ IP được gán bởi người quản trị. DHCP chỉ đưa địa chỉ này đến client

#### Một số thuật ngữ trong DHCP

**DHCP Server**: máy chủ quản lý việc cấu hình và cấp phát địa chỉ IP cho Client

**DHCP Client**: máy trạm nhận thông tin cấu hình IP từ DHCP Server

**Scope**: phạm vi liên tiếp của các địa chỉ IP có thể cấp cho client

**Exclusion Scope**: là dải địa chỉ nằm trong Scope không được cấp phát động cho client

**Options**: Cấu hình các thông số mặc định của DHCP

**Lease**: Thời gian "cho thuê" địa chỉ IP đối với mỗi client

**Reservation**: là những đoạn địa chỉ được dành riêng cho một số máy tính trong một scope

**DHCP Replay Agent**: DHCP Replay Agent là một máy tính hoặc Router được cấu hình để lắng nghe và chuyển tiếp các gói tin giữa DHCP Client và DHCP Server

#### Cách thức hoạt động của DHCP

**Bước 1:**

DHCP Client gửi broadcast thông điệp discover để tìm Server nhằm xin IP

**Bước 2:**

DHCP Server gửi lại thông điệp offer mesage cho Client. Thông điệp này chứa MAC của client, IP client, subnetmask, IP server, lease)

**Bước 3:**

Client chọn 1 trong các địa chỉ IP, sau đó gửi lại DHCP Request tương ứng cho DHCP Server đó

**Bước 4:**

Server hoàn tất bằng việc gửi DHCP ACK cho client. Ngoài ra còn có gateway mặc định, địa chỉ DNS server
