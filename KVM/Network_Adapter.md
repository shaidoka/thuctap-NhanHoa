# Các chế độ card mạng trong KVM

Tương tự trong ảo hóa VMware, VMware có 3 chế độ card mạng đó là Bridge, NAT và Host-only thì có KVM có 3 tùy chọn cho card mạng là NAT, Public Bridge và Private Bridge

#### 1. NAT

- Đây là chế độ mặc định trong KVM, đơn giản ở đây hiểu chế độ NAT sẽ cấp cho mỗi VM 1 IP theo dải mạng của hệ thống, chế độ này cho phép chuyển tiếp gói tin giữa lớp mạng bên trong VM với lớp mạng bên ngoài để có thể kết nối ra Internet
- Cơ chế ở đây hiểu đơn giản là 1 bridge cho mạng ảo kết nối với card mạng thật để ra Internet
- Card mạng ảo của VM gắn vào 1 bridge (vibr0), vibr0 mặc định có gateway, các gói tin của máy ảo sẽ đi qua đường này để đến card máy ảo thật và ra ngoài Internet
- KVM cấp DHCP cho các máy dùng chế độ NAT

#### 2. Public Bridge

- Chế độ này sẽ cho phép các máy ảo có cùng dải mạng vật lý với card mạng thật. Để có thể làm được điều này cần thiết lập 1 bridge và cho phép nó kết nối với cổng vật lý của thiết bị thật (eth0)

#### 3. Private Bridge

- Chế độ này sẽ sử dụng 1 bridge riêng biệt để các VM giao tiếp với nhau mà không ảnh hưởng tới địa chỉ của KVM host