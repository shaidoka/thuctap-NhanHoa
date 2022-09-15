# Công nghệ ảo hóa

### Giới thiệu về ảo hóa

Ngày nay, việc quản lý và sử dụng hạ tầng CNTT là điều rất cần thiết với bất kỳ 1 doanh nghiệp nào. Tuy nhiên vẫn còn những hạn chế trong quản lý và sử dụng tài nguyên theo phương pháp truyền thống:
    
- Mỗi máy chủ vật lý chỉ cài đặt tương ứng có thể cài đặt phục vụ cho mục đích doanh nghiệp
- Việc đầu tư nhiều máy chủ nhưng không sử dụng hết năng lực của máy chủ dẫn đến phí phạm tài nguyên và quản lý tài nguyên trở nên khó khăn
- Các máy chủ vật lý được cài đặt trực tiếp hệ điều hành và ứng dụng gặp khó khăn trong việc sao lưu và phục hồi, thậm chí 1 số máy chủ vật lý đang hoạt động có những cơ chế đặc thù và gần như rất khó hoặc "không thể" thực hiện công việc trên
- Thời gian downtime của máy chủ vật lý thường rất lâu và dễ gặp trục trặc trong quá trình khởi động lại
- Khó khăn trong việc quản trị và giám sát tập trung khi số lượng máy chủ vật lý tăng lên

Công nghệ ảo hóa ra đời nhằm khai thác triệt để khả năng làm việc của 1 máy chủ vật lý. Ảo hóa cho phép vận hành nhiều máy chủ ảo trên cùng 1 máy chủ vật lý, dùng chung các tài nguyên của 1 máy chủ vật lý như CPU, RAM, ổ cứng,... và các tài nguyên khác. Các máy ảo khác nhau có thể vận hành hđh và ứng dụng trên cùng 1 máy chủ vật lý

Công nghệ ảo hóa cho phép hợp nhất và chạy nhiều khối lượng công việc như các máy ảo trên cùng 1 máy tính duy nhất. Một máy ảo là 1 máy tính được tạo ra bởi phần mềm, giống như 1 máy tính vật lý, chạy 1 hđh và các ứng dụng. Mỗi máy ảo có phần cứng ảo riêng của nó, bao gồm 1 CPU, bộ nhớ, đĩa cứng và card mạng ảo, giống như phần cứng cho hđh và ứng dụng

### Chức năng của ảo hóa

**Phân chia:** với công nghệ ảo hóa, chúng ta có thể chạy nhiều máy ảo trên 1 máy thật với nhiều hđh khác nhau, nhờ thế mà ta cũng có thể tách từng dịch vụ ra để cài trên từng máy ảo

**Cô lập:** Mỗi dịch vụ quan trọng được cài trên 1 máy ảo khá nhau thì nếu có sự cố, các dịch vụ khác cũng không bị ảnh hưởng gì

**Đóng gói:** Với công nghệ ảo hóa, các máy ảo được đóng gói thành các file riêng biệt, nhờ vậy mà nó có thể dễ dàng được sao chép để backup và di chuyển sang hệ thống khác để chạy

### Lợi ích của ảo hóa

Tiết kiệm chi phí trong khi đó lại tăng hiệu quả, hiệu năng và tính linh động cho hạ tầng hiện hữu

Giảm số lượng máy chủ vật lý, giảm lượng điện năng tiêu thụ, tiết kiệm được chi phí cho việc bảo trì phần cứng, nâng cao hiệu quả công việc

Dễ dàng mở rộng khi có nhu cầu

Khai thác triệt để các tài nguyên của phần cứng vật lý bằng cách chạy nhiều hđh trên mạng một máy chủ vật lý

Tăng tính linh hoạt của hệ thống, cho phép di chuyển máy chủ mà không gây ảnh hưởng đến các ứng dụng và dịch vụ đang chạy trên các máy chủ. Cung cấp các ứng dụng và tài nguyên nhanh hơn

Trong ảo hóa, người ta có thể ảo hóa:

- RAM virtualization
- CPU virtualization
- Network virtualization
- Device I/O virtualization

### Hypervisor/VMM (Virtual Machine Monitor)

Hypervisor hay còn gọi là phần mềm giám sát máy ảo: là 1 chương trình phần mềm quản lý 1 hoặc nhiều máy ảo (VM). Nó được sử dụng đê tạo, khởi động, dừng và reset các máy ảo. Các hypervisor cho phép mỗi VM hoặc Guest truy cập vào lớp tài nguyên phần cứng vật lý như CPU, RAM, storage. Nó cũng có thể giới hạn số lượng tài nguyên hệ thống mà mỗi máy ảo có thể sử dụng để đảm bảo cho nhiều máy ảo cùng sử dụng đồng thời trên cùng 1 hệ thống

Hypervisor tạo nên 1 nền tảng ảo hóa (virtual platform) trên máy chủ, và dựa trên đó các máy ảo hoạt động và được quản lý

Hypervisor có 2 loại chính đó là:

- **Dedicated virtualization** (Bare-Metal Hypervisor): Hypervisor tương tác trực tiếp với phần cứng của máy chủ để quản lý, phân phối và cấp phát tài nguyên. Loại ảo hóa này bao gồm các giải pháp như VMware ESXi, Microsoft Hyper-V, Xen Server, KVM
- **Hosted Architecture:** đây là loại ảo hóa Hypervisor giao tiếp với phần cứng thông qua hđh. Hypervisor lúc này được xem như 1 ứng dụng của hđh và các phương thức quản lý, cấp phát tài nguyên đều phải thông qua hđh. Loại ảo hóa này bao gồm các giải pháp như: VMware WorkStation, Oracle VirtualBox, Microsoft Virtual PC,...

Với loại thứ 1, Hypervisor tương tác trực tiếp với phần cứng nên việc quản lý và phân phối tài nguyên được tối ưu và hiệu quả hơn so với loại 2, vì vậy khi triển khai trong thực tế, ảo hóa loại 1 (Bare-Metal Hypervisor) được sử dụng trong các trường hợp thử nghiệm, hoặc mục đích học tập

# Công nghệ ảo hóa KVM

#### 1. KVM là gì?

KVM (hay Kernel Virtualization Machine) là giải pháp ảo hóa cho hệ thống Linux trên nền tảng phần cứng x86 có các module mở rộng hỗ trợ ảo hóa (Intel VTx hoặc AMD-V). KVM là 1 module của Kernel Linux hỗ trợ cơ chế mapping các chỉ dẫn trên CPU ảo (của Guest VM) sang chỉ dẫn trên CPU thật (của Host). Ảo hóa KVM có cách hoạt động giống như người quản lý, chia sẻ các nguồn tài nguyên ổ đĩa, network, CPU 1 cách công bằng


#### 2. Đặc điểm

Công nghệ ảo hóa KVM cho phép có thể chuyển Linux thành ảo hóa để máy chủ chạy trên nhiều môi trường ảo bị cô lập gọi là máy khách hoặc máy ảo VM

Ảo hóa KVM không có tài nguyên dùng chung, chúng được mặc định sẵn. Như vậy RAM của mỗi KVM được định sẵn cho từng gói VPS, tận dụng triệt để 100% và không bị chia sẻ. Điều này sẽ giúp cho chúng hoạt động ổn định hơn, không bị ảnh hưởng bởi các VPS khác trong hệ thống. Tương tự, các tài nguyên khác của ổ cứng được định sẵn phân chia như vậy

#### 3. Kiến trúc của hệ thống KVM

Trong kiến trúc KVM, máy ảo là 1 tiến trình Linux, được lập lịch bởi chuẩn Linux schduler. Trong thực tế mỗi CPU ảo xuất hiện như là 1 tiến trình Linux. Điều này cho phép KVM sử dụng tất cả tính năng của Linux kernel

Linux có tất cả các cơ chế của một VMM cần thiết để vận hành các máy ảo. Chính vì vậy, các nhà phát triển không xây dựng lại mà chỉ thêm vào đó 1 vài thành phần hỗ trợ ảo hóa. KVM được triển khai như 1 module hạt nhân có thể được nạp vào để mở rộng Linux bởi những khả năng này

Trong 1 môi trường Linux thông thường, mỗi process chạy hoặc sử dụng user-mode hoặc kernel-mode. KVM đưa ra một chế độ thứ 3 đó là guest-mode. Nó dựa trên CPU có khả năng ảo hóa với kiến trúc Intel VT hoặc AMD SVM, một process trong guest-mode bao gồm cả kernel-mode và user-mode

**Kiến trúc của KVM bao gồm 3 thành phần chính:**

- KVM kernel module:
    - Là 1 phần trong dòng chính của Linux Kernel
    - Cung cấp giao diện chung cho Intel VMX và AMD SVM (thành phần hỗ trợ ảo hóa phần cứng)
    - Chứa những mô phỏng cho các instruction và CPU modes không được hỗ trợ bởi Intel VMX và AMD SVM
- Qemu-kvm: là chương trình dòng lệnh để tạo ra các máy ảo, thường được vận chuyển dưới dạng các package kvm hoặc qemu-kvm. Có 3 chức năng chính:
    - Thiết lập VM và các thiết bị vào/ra (Input/Output)
    - Thực thi mã khách thông qua KVM kernel module
    - Mô phỏng các thiết bị vào/ra và di chuyển các Guest từ Host này sang Host khác
- Libvirt management stack:
    - Cung cấp API để các tool như virsh có thể gioa tiếp và quản lý các VM
    - Cung cấp chế độ quản lý từ xa an toàn

#### 4. Cơ chế hoạt động

- Để các máy ảo giao tiếp được với nhau, KVM sử dụng Linux Bridge và OpenVSwitch, đây là 2 phần mềm cung cấp các giải pháp ảo hóa network
- Linux Bridge là 1 phần mềm được tích hợp vào trong nhân của Linux để giải quyết các vấn đề ảo hóa phần network trong máy vật lý. Về mặt logic Linux bridge sẽ tạo ra 1 con switch ảo để cho các VM kết nối được vào và có thể nói chuyện được với nhau cũng như sử dụng để kết nối ra bên ngoài
- Cấu trúc của Linux Bridge khi kết hợp với KVM-QEMU:

![](./images/kientruc.png)

- Trong đó:
    - Bridge: tương đương với switch layer 2
    - Port: tương đương với port của switch thật
    - Tap (tap interface): có thể hiểu là giao diện mạng để các VM kết nối với bridge do linux bridge tạo ra
    - fd (forward data): 
- Các tính năng chính:
    - STP: Spanning Tree Protocol - giao thức chống lặp gói tin trong mạng
    - VLAN: chia switch (do Linux Bridge tạo ra) thành các mạng LAN ảo, cô lập traffic giữa các VM trên các VLAN khác nhau của cùng 1 switch
    - FDB (forwarding database): chuyển tiếp các gói tin theo database để nâng cao hiệu năng switch. Database lưu các địa chỉ MAC mà nó học được. Khi gói tin Ethernet đến, bridge sẽ tìm kiếm trong database có chứa MAC address không. Nếu không, nó sẽ gửi gói tin đến tất cả các cổng (broadcast)

