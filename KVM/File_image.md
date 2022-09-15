# Giới thiệu chung về file image

Công nghệ ảo hóa phần cứng của QEMU rất giống với KVM. Cả hai đều được điều khiển thông qua libvirt, hỗ trợ tính năng thiết lập giống nhau, và tất cả các image máy ảo tương thích với KVM thì cũng tương thích với QEMU. Điểm khác biệt chính giữa QEMU và KVM là QEMU không hỗ trợ native virtualization, do đó QEMU có hiệu suất kém hơn KVM

QEMU được sử dụng trong các trường hợp sau:
- Chạy trên các phần cứng cũ không hỗ trợ ảo hóa
- Chạy trên các dịch vụ điện toán trên 1 máy ảo cho mục đích phát triển hoặc thử nghiệm

QEMU hỗ trợ các định dạng hình ảnh máy ảo sau đây:
- Raw
- QEMU Copy-on-write (qcow2)
- VMware virtual machine disk format (vmdk)

File image của đĩa CD/DVD chính là 1 dạng file có định dạng theo các chuẩn tại file ảnh. File image là 1 file đóng gói hết tất cả nội dung của 1 đĩa CD/DVD vào trong nó

Trong KVM Guest có 2 thành phần chính đó là VM definition được lưu dưới dạng file xml tại **/etc/libvirt/qemu**. File này chứa các thông tin của máy ảo như tên, số ram, số cpu... File còn lại là storage thường được lưu dưới dạng file image tại thư mục **/var/lib/libvirt/images**

3 định dạng thông dụng nhất của file image sử dụng trong KVM đó là iso, raw, qcow2

### Định dạng file image phổ biến trong KVM

**1. File ISO**

- File ISO là file ảnh của 1 đĩa CD/DVD, nó chứa toàn bộ dữ liệu của đĩa CD/DVD đó. File ISO thường được sử dụng để cài đặt hệ điều hành của VM, người dùng có thể import trực tiếp hoặc tải từ Internet về

- Boot từ file ISO cũng là 1 trong số những tùy chọn mà người dùng có thể sử dụng khi tạo máy ảo

**2. File raw**

- Là định dạng file image phi cấu trúc 
- Khi người dùng tạo mới 1 máy ảo có disk format là raw thì dung lượng của file disk sẽ bằng đúng dung lượng của ổ đĩa máy ảo bạn đã tạo
- Định dạng raw khi tạo máy ảo với virt-manager hoặc không khai báo khi tạo VM bằng virt-install thì định dạng ổ đĩa sẽ là raw. Hay nói cách khác, raw chính là định dạng mặc định của QEMU

**3. File qcow2**

- Qcow2 là 1 định dạng tập tin cho image nơi các tập tin được sử dụng bởi QEMU. Viết tắt của "QEMU Copy On Write" và sử dụng cách thức tối ưu hóa lưu trữ disk để trì hoãn phân bổ dung lượng lưu trữ cho đến khi nó thực sự cần thiết. Các tập tin trong định dạng qcow, có thể chứa 1 loạt các disk image thường được gắn liền với client cụ thể các hđh
- Qcow2 là 1 phiên bản cập nhật của định dạng qcow, nhằm để thay thế. Khác với bản gốc, qcow2 hỗ trợ nhiều snapshot thông qua máy ảo mới. Tức là, khi snapshot thì disk này sẽ tạo ra 1 máy ảo mới
- Qcow2 hỗ trợ copy-on-write với những tính năng đặc biệt như snapshot, mã hóa, nén dữ liệu
    - Các tập tin với định dạng này có thể phát triển khi dữ liệu được thêm vào. Điều này cho phép kích thước tệp nhỏ hơn hình ảnh đĩa thô, phân bổ toàn bộ không gian image vào tệp
    - Định dạng qcow cũng cho phép lưu trữ các thay đổi được thực hiện với 1 base image chỉ đọc trên 1 tập tin qcow riêng biệt bằng cách sử dụng copy on write. Tập tin qcow mới này chứa đường dẫn đến base image để có thể tham chiếu trở lại khi cần thiết. Khi đọc dữ liệu từ image này, nội dung đó sẽ được lấy ra nếu nó là mới. Nếu không, dữ liệu sẽ được lấy từ base image
    - Tính năng tùy chon bao gồm mã hóa AES và zlib dựa trên giải nén trong suốt
    - Bất lợi của image qcow là không được gắn trực tiếp như disk image
- Copy on write (cow) đôi khi gọi là chia sẻ tiềm ẩn, là 1 kỹ thuật quản lý tài nguyên được sử dụng trong lập trình máy tính để thực hiện có hiệu quả các thao tác "nhân bản" hoặc "sao chép" trên các tài nguyên có thể thay đổi. Nếu một tài nguyên được nhân đôi nhưng không được sửa đổi thì không cần thiết phải tạo 1 tài nguyên mới. Tài nguyên có thể được chia sẻ giữa bản sao và bản gốc
- Qcow2 hỗ trợ việc tăng bộ nhớ bằng cơ chế Thin Provisioning