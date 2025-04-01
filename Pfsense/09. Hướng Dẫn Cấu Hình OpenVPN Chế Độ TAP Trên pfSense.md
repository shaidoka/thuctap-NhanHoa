# Hướng Dẫn Cấu Hình OpenVPN Chế Độ TAP Trên pfSense

Hướng dẫn này sẽ giúp bạn thiết lập **OpenVPN** chế độ **TAP (Layer 2)** trên pfSense, cho phép các client từ xa kết nối như thể đang ở cùng một mạng LAN.

## 1. Cấu Hình Máy Chủ OpenVPN

### 1.1 Tạo Server OpenVPN
1. Truy cập **VPN > OpenVPN > Servers** và nhấn **Add** để tạo mới máy chủ OpenVPN.

2. Cấu hình các thông số cơ bản như sau:

#### **General Information**
- **Description**: Nhập mô tả cho VPN (ví dụ: `client to site`).
- **Disabled**: Bỏ chọn để kích hoạt server này.

#### **Mode Configuration**
- **Server Mode**: Chọn **Remote Access (SSL/TLS + User Auth)**.
- **Backend for authentication**: Chọn **Local Database** để quản lý tài khoản người dùng trực tiếp trên pfSense.
- **Device Mode**: Chọn **tap - Layer 2 Tap Mode** để sử dụng chế độ Layer 2.

#### **Endpoint Configuration**
- **Protocol**: Chọn **UDP on IPv4 only** để sử dụng UDP với IPv4.
- **Interface**: Chọn **WAN** để OpenVPN lắng nghe trên giao diện WAN.
- **Local port**: Nhập **1194** (cổng mặc định của OpenVPN).

### 1.2 Cấu Hình Mật Mã (Cryptographic Settings)
- **TLS Configuration**: Chọn **Use a TLS Key** và nhập khóa TLS của bạn vào.
- **Peer Certificate Authority**: Chọn **OpenVPN_Server_Cert** để sử dụng chứng chỉ bạn đã tạo cho máy chủ.
- **Server Certificate**: Chọn **OpenVPN_Server_Cert**.
- **DH Parameter Length**: Chọn **2048 bit**.
- **Data Encryption Algorithms**: Chọn các thuật toán mã hóa phù hợp với yêu cầu bảo mật của bạn (ví dụ: `AES-256-GCM`).

### 1.3 Tunnel Settings
- **Bridge DHCP**: Tích vào **Allow clients on the bridge to obtain DHCP** để cho phép client nhận IP qua DHCP từ mạng nội bộ.
- **Bridge Interface**: Chọn **VLAN90** (hoặc bất kỳ VLAN nào bạn muốn sử dụng).
- **Bridge Route Gateway**: Tích vào **Push the Bridge Interface IPv4 address to connecting clients as a route gateway**.
- **Server Bridge DHCP Start/End**: Nhập dải địa chỉ IP DHCP để cấp cho client (ví dụ: `10.10.90.10` đến `10.10.90.40`).

### 1.4 Advanced Configuration
- **Custom Options**: Nhập các dòng `push route` để đẩy các tuyến cần thiết cho các client:
  ```plaintext
      push "route 10.10.91.0 255.255.255.0";
      push "route 10.10.92.0 255.255.255.0";

Gateway creation: Chọn IPv4 only nếu chỉ sử dụng IPv4.

# 2. Cấu Hình Bridge
Truy cập Interfaces > Assignments và chọn tab Bridges.

Nhấn Add để tạo một bridge mới và thêm các interface sau vào bridge:

VLAN90 (hoặc VLAN đã chọn)
VPN (giao diện của OpenVPN TAP)
Đặt tên bridge, ví dụ là BRIDGE0.

## 3. Cấu Hình Interface Cho Bridge
Vào Interfaces > Assignments và gán BRIDGE0 làm một interface mới.
Đặt tên và bật interface BRIDGE0.
Cấu hình IP cho BRIDGE0 để nó thuộc cùng subnet với VLAN của bạn.

## 5. Cấu Hình DHCP Cho Bridge
Vào Services > DHCP Server và chọn tab BRIDGE0.
Kích hoạt Enable DHCP server on BRIDGE0 interface và cấu hình dải địa chỉ IP mà DHCP sẽ cấp cho các thiết bị.
## 6. Tạo Tài Khoản Người Dùng OpenVPN
Truy cập System > User Manager.
Nhấn Add để tạo người dùng mới, nhập tên, mật khẩu, và tạo chứng chỉ người dùng cho OpenVPN.
## 7. Xuất Cấu Hình Client
Truy cập VPN > OpenVPN > Client Export.
Chọn máy chủ OpenVPN bạn vừa tạo và tải về cấu hình .ovpn cho người dùng.
Cung cấp file này cho các người dùng từ xa để họ kết nối vào VPN.
## 8. Kiểm Tra Kết Nối VPN
Đảm bảo rằng cổng 1194 đã được mở trên firewall của pfSense (vào Firewall > Rules > WAN để kiểm tra).
Kiểm tra rằng các client có thể kết nối và nhận địa chỉ IP từ dải DHCP đã cấu hình.
