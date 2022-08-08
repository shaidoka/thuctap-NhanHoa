# Cài đặt Centos 7

## Tạo máy ảo trên Vmware WorkStation

**Tại giao diện khởi đầu của VMware, chọn "Create a New Virtual Machine**

![](./images/create_virtual_machine.png)

**Chọn "Custom (advanced)" sau đó nhấn Next để sang bước tiếp theo**

![](./images/step2.png)

**Chọn phiên bản máy ảo của VMware Workstation**

![](./images/step3.png)

**Chọn file cài đặt hệ điều hành, thông thường chọn "I will install the operation system later" để tiến hành cài đặt hệ điều hành sau khi đã có máy ảo**

![](./images/step4.png)

**Chọn hệ điều hành sẽ cài đặt, ở bài này ta chọ Linux - Centos 7 64bit**

![](./images/step5.png)

**Sửa tên của máy ảo và vị trí lưu trữ trên máy thật**

![](./images/step6.png)

**Chọn số cpu của máy ảo và số nhân với mỗi chip**

![](./images/step7.png)

**Điều chỉnh lượng RAM của máy ảo**

![](./images/step8.png)

**Lựa chọn kiểu kết nối mạng mà máy ảo sẽ sử dụng**

![](./images/step9.png)

- Use bridged networking: card mạng ảo kết nối thẳng với mạng thật bên ngoài
- Use network address translation (NAT): card mạng ảo NAT tới card mạng thật của máy host
- Use host-only networking: sử dụng mạng riêng tách biệt mới máy host

**Chọn ổ đĩa, thông thường chọn tạo ra 1 ổ đĩa ảo, sau đó điều chỉnh dung lượng ổ**

![](./images/step10.png)

![](./images/step11.png)

*Lưu ý rằng, ổ đĩa ảo sẽ không thực sự chiếm hết 20GB ở ổ đĩa thật mà chỉ chiếm đúng số lượng mà ta sử dụng đến ở máy ảo*

**Kiểm tra lại thông số cài đặt và nhấn finish để hoàn thành**

![](./images/final_step.png)

## Cài đặt hệ điều hành CentOS 7 trên máy ảo VMware Workstation

**Tải file ISO cài đặt hệ điều hành CentOS 7 tại trang chủ của CentOS:** [https://www.centos.org/download/](https://www.centos.org/download/)

**Tiến hành đưa đĩa cài vào ổ đĩa của máy ảo: Chọn CD/DVD (IDE) rồi chọn Use ISO image file và Browse tới file cài đặt Cent 7 vừa download**

![](./images/step2_1.png)

**Chọn "Instal CentOS 7"**

![](./images/step2_2.png)

**Chọn ngôn ngữ cho hệ điều hành**

![](./images/step2_3.png)

**Chọn "DATE & TIME" để điều chỉnh ngày giờ**

![](./images/step2_4.png)

**Ở phần "SOFTWARE SELECTION", ta chọn GNOME Desktop để cài đặt giao diện đồ họa thuận tiện cho người sử dụng**

![](./image/step2_5.png)

*Lưu ý là các phần mềm khác hoàn toàn có thể được cài đặt sau khi hoàn thiện hệ điều hành*

**Tiếp đến, tại "INSTALLATION DESKTINATION", chọn "I will configure partitioning" để tự điều chỉnh các phân vùng**

![](./images/step2_6.png)

- /boot: 1Gb - Là phân vùng dành cho việc khởi động hệ điều hành
    - Device type: Standard Partition
    - File System: ext4
- /swap: 3Gb - Là phân vùng được sử dụng khi bộ nhớ RAM đầy, lúc này tài nguyên và dữ liệu tạm thời không hoạt động trên bộ nhớ RAM để lưu trữ vào không gian Swap để giải phóng bộ nhớ RAM và sử dụng cho việc khác
    - Device type: Standard Partition
    - File System: swap
- /: tổng dung lượng còn lại - Là phân vùng dùng cho việc lưu trữ file
    = Device type: LVM
    - File System: ext4

**Tại "NETWORK & HOSTNAME" tiến hành chỉnh sửa hostname**

![](./images/step2_7.png)

Ở network ta chọn OFF để máy có kết nối Internet, thay đổi này có thể điều chỉnh sau trong hệ điều hành

**Chọn "Begin Installation" để bắt đầu cài đặt, trong lúc chờ ta có thể thay đổi mật khẩu của root hay tạo thêm user**

![](./images/step2_8.png))

**Sau khi hoàn thành, chọn Reboot để khởi động lại máy ảo**

![](./images/final_step_centos.png)

**Done.**

![](./images/done.png)
