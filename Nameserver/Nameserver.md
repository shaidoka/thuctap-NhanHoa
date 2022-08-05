# Máy chủ quản lý tên miền - NameServer

## Giới thiệu chung

NameServer là hệ thống có chức năng điều phối quá trình hoạt động của tên miền website, chuyển đổi từ tên miền sang địa chỉ IP. NameServer hay còn được gọi là DNS Server hay Domain NameServer, tạm dịch là máy chủ quản lý tên miền giúp người dùng truy cập vào trang web mình muốn đến thông qua tên miền

Nhìn chung, địa chỉ IP là 1 dãy số khó nhớ, nên khi cần truy cập trang web sẽ phải gõ tên miền vào thanh trình duyệt. Tuy nhiên, tên miền không phải là yếu tố dùng để truy cập trang web mà phải có 1 hệ thống trung gian để chuyển đổi từ tên miền sang địa chỉ IP

## Một số đặc điểm của NameServer

NameServer có 1 số đặc điểm cơ bản sau:
- Lưu trữ tên miền tương ứng với địa chỉ IP
- Chuyển đổi tên miền thành địa chỉ IP 
- Thời gian truy cập thông tin lên đến 8 tiếng

**Lưu trữ tên miền tương ứng với địa chỉ IP và giúp chuyển đổi giữa tên miền và địa chỉ IP**

Nameserver được xem như một hệ thống danh bạ khổng lồ. Trong đó lưu trữ 1 thư mục lớn tên miền tương ứng với địa chỉ IP và tập hợp tại 1 trung tâm đăng ký. Do đó, chỉ cần người dùng gõ tên miền mình muốn truy cập vào thanh trình duyệt, hệ thống này sẽ tìm ra địa chỉ IP tương ứng đã được lưu trữ ở trung tâm

**Thời gian truy cập thông tin lên đến 8 tiếng**

Khoảng thời gian cho việc cập nhật thông tin giữa các NameServer với nhau có thể lên đến 8 tiếng. Điều này nghĩa là các NameServer có thể truy cập thông tin của các tên miền có đuôi .com và .net trong thời gian tối đa là 8 tiếng sau khi đăng ký. Và thời gian dành cho các tên miền mở rộng (sub-domain) lên đến 48h.

## Thay đổi NameServer cho tên miền

Có 3 cách để thay đổi NameServer cho tên miền:
- Chuyển tên miền sang nhà cung cấp mới
- Đổi bản ghi A của dịch vụ DNS
- Đổi NameServer của tên miền