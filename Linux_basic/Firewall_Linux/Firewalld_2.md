# Kích hoạt ghi log loại bỏ packet của firewalld

Chúng ta đều đã biết Linux có iptables hoạt động ở tầng network như 1 tường lửa vô cùng hữu dụng. Vậy Firewalld, nằm ở tầng ứng dụng liệu có thể sử dụng như iptables không? 

Firewalld thực ra linh hoạt không kém gì iptables, trong bài viết này chúng ta hãy cùng tìm hiểu cách sử dụng tùy chọn ```LogDenied``` để ghi lại các gói tin bị loại bỏ bởi firewalld.

Có nhiều cách để thực hiện mục đích được nhắc tới bên trên, bao gồm:

## 1. Cấu hình tệp firewalld.conf

Chỉnh sửa file ```/etc/firewalld/firewalld.conf```:

```sh
vi /etc/firewalld/firewalld.conf
```

Tìm tham số

```sh
LogDenied=off
```

Và thay thế bằng

```sh
LogDenied=all
```

Lưu lại sau đó restart firewalld service

```sh
systemctl restart firewalld
# hoặc
firewall-cmd --reload
```

Mặc định LogDenied được tắt đi. Tùy chọn này cho phép firewalld ghi lại log ngay khi các chains INPUT, FORWARD, hay OUTPUT loại bỏ 1 gói tin nào đó. Các giá trị khả dụng là:
- ```all```: Khi sử dụng giá trị này, tất cả các gói tin bị từ chối (bao gồm cả unicast, broadcast và multicast) đều sẽ được ghi nhật ký.
- ```unicast```: Khi sử dụng giá trị này, chỉ các gói tin unicast (gói tin được gửi đến một địa chỉ IP duy nhất) bị từ chối sẽ được ghi nhật ký.
- ```broadcast```: Khi sử dụng giá trị này, chỉ các gói tin broadcast (gói tin được gửi đến tất cả các thiết bị trong một mạng) bị từ chối sẽ được ghi nhật ký.
- ```multicast```: Khi sử dụng giá trị này, chỉ các gói tin multicast (gói tin được gửi đến một nhóm địa chỉ IP) bị từ chối sẽ được ghi nhật ký.
- ```off```: Khi sử dụng giá trị này, các gói tin bị từ chối sẽ không được ghi nhật ký.

## 2. Sử dụng lệnh firewall-cmd

Tìm và kiểm tra giá trị của tham số ```LogDenied``` hiện tại

```sh
$ firewall-cmd --get-log-denied

LogDenied=off
```

Thay đổi giá trị

```sh
firewall-cmd --set-log-denied=all
```

Kiểm tra

```sh
$ firewall-cmd --get-log-denied

LogDenied=all
```

## 3. Xem log này ở đâu?

Sử dụng grep command hoặc journalctl để kiểm tra

```sh
journalctl -xe
```

Hoặc sử dụng dmesg

```sh
dmesg
dmesg | grep -i REJECT
```

## 3. Cách để ghi log tất cả packet vào file

Tạo 1 file cấu hình tên ```firewalld-droppd.conf```

```sh
vi /etc/rsyslog.d/firewalld-droppd.conf
```

Thêm đoạn cấu hình này vào

```sh
:msg,contains,"_DROP" /var/log/firewalld-droppd.log
:msg,contains,"_REJECT" /var/log/firewalld-droppd.log
& stop
```

Restart rsyslog service

```sh
systemctl restart rsyslog.service
```

Giờ có thể kiểm tra file log được rồi

```sh
tail -f /var/log/firewalld-droppd.log
```

## 4. Tổng kết

Theo dõi các gói tin bị từ chối và loại bỏ bowrir firewalld là một nhiệm vụ không thể thiếu của người quản trị hệ thống. Nhờ đó cho phép bạn tránh được nhiều cuộc tấn công hay vấn đề về bảo mật.