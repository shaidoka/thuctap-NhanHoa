# Các định dạng image của Glance

Các định dạng trên đĩa (Disk Formats) của một image máy ảo là định dạng của hình ảnh đĩa cơ bản. Sau đây là các định dạng đĩa được hỗ trợ bởi Openstack Glance

## Disk formats

|Disk format|Mô tả|
|:-|:-|
|raw|Định dạng đĩa phi cấu trúc|
|VHD|Định dạng chung hỗ trợ bởi nhiều công nghệ ảo hóa trong OPS, trừ KVM|
|VMDK|Định dạng hỗ trợ bởi VMware|
|qcow2|Định dạng đĩa QEMU, định dạng mặc định hỗ trợ bởi KVM và QEMU, hỗ trợ các chức năng nâng cao|
|VDI|Định dạng hỗ trợ bởi VirtualBox|
|ISO|Định dạng lưu trữ cho đĩa quang|
|AMI, ARI, AKI|Định dạng image amazon machine, ramdisk, kernel|

## Container formats

Container Formats mô tả định dạng files chứa các thông tin metadata về máy ảo thực sự. Các định dạng container hỗ trợ bởi Glance bao gồm:

|Container format|Mô tả|
|:-|:-|
|bare|Định dạng xác định không có container hoặc metadata đóng gói cho image|
|ovf|Định dạng container OVF|
|aki|Xác định lưu trữ trong Glance là Amazon kernel image|
|ari|Xác định lưu trữ trong Glance là Amazon ramdisk image|
|ami|Xác định lưu trữ trong Glance là Amazon machine image|
|ova|Xác định lưu trữ trong Glance là file lưu trữ OVA|
|docker|Xác định lưu trữ trong Glance là 1 Docker tar archive của container filesystem|