# Q&A (tiếp)

## Các loại bản ghi cơ bản

- Bản ghi SOA: chỉ ra máy chủ Name Server là nơi cung cấp thông tin tin cậy từ dữ liệu có trong zone
- Bản ghi NS: chỉ ra máy chủ DNS quản lý tên miền của hệ thống
- Bản ghi host A: ánh xạ tên máy thành địa chỉ IP
- Bản ghi PTR: ánh xạ địa chỉ IP thành tên máy
- Bản ghi CNAME: tạo bí danh khác cho 1 máy chủ
- Bản ghi MX: dùng cho việc chuyển mail

*Chi tiết về DNS xem ở [đây](https://github.com/shaidoka/thuctap-NhanHoa/blob/main/Cac%20giao%20thuc%20mang/DNS/DNS.md)

## Swap và cách tạo swap

### 1. Giới thiệu chung

Swap Memory được sử dụng khi hệ thống quyết định rằng nó cần thêm bộ nhớ RAM trong quá trình hoạt động mà bộ nhớ RAM hiện tại không đủ. Lúc này, dữ liệu tạm thời không sử dụng có trong RAM sẽ được đẩy vào swap memory giúp giải phóng bộ nhớ RAM cho các hoạt động khác

Swap memory sẽ giúp hệ thống hoạt động bình thường, nhưng tốc độ chậm hơn RAM nhiều

Lợi ích của swap memory:
- Tối ưu hóa hệ thống bộ nhớ: dữ liệu không sử dụng trong RAM sẽ được di chuyển đến swap, giúp hệ thống phục vụ cho các hoạt động khác cần thiết hơn
- Tránh các trường hợp không lường trước được ảnh hưởng đến hoạt động của hệ thống
- Linux swap có 2 dạng: phân vùng (partition) và file

Kiểm tra các thông số của swap memory, sử dụng lệnh ```swapon```

### 2. Tạo file swap

Sử dụng lệnh sau để tạo file swap:

```dd if=/dev/zero of=/swapfile bs=1024 count=1048576```

Với ```bs``` là kích thước còn ```count``` là tốc độ đọc ghi

Phân quyền cho swap file: 

```chmod 600 /swapfile```

Sử dụng ```mkswap``` để thiết lập file là file swap

```mkswap /swapfile```

Khởi động file swap:

```swapon /swapfile```

Mở file /etc/fstab và thêm vào dòng sau:

```sh
vi /etc/fstab

/swapfile swap swap defaults 0 0
```

Như vậy file swap mới đã được tạo, có thể kiểm tra bằng lệnh ```swapon```

### 3. Swappiness

Swapiness là giá trị từ 0-100 biểu thị cho mức độ ưu tiên sử dụng swap của linux, giá trị càng cao thì linux sử dụng swap càng nhiều.

Có thể thay đổi swappiness tại ```/proc/sys/vm/swappiness```

### 4. Xóa swap file

Để xóa swap file, đầu tiên deactive swap file:

```swapoff -v /swapfile```

Sau đó, xóa dòng khai báo swap tại file /etc/fstab

Cuối cùng xóa file swap bằng lệnh ```rm -r /swapfile```

## Đổi port SSH, kiểm tra hoạt động của port

1. Cách đổi port SSH

Mặc định SSH dùng port 22, để thay đổi, ta vào file config của ssh có tên là sshd_config tại đường dẫn /etc/ssh/sshd_config

```vi /etc/ssh/sshd_config```

Tìm kiếm dòng ```#Port 22```, bỏ dấu ```#``` và đổi ```22``` thành port mình muốn sử dụng

Sau đó, mở port vừa điền ở firewall

```sh
firewall-cmd --permanent --zone=public --add-port=2200/tcp
firewall-cmd --reload
```

Cuối cùng, khởi động lại dịch vụ ssh bằng lệnh ```systemctl restart sshd```

2. Kiểm tra hoạt động của port

**Windows**: Tải phần mềm nmap

**Linux**: Sử dụng lệnh ```netstat -nltp```