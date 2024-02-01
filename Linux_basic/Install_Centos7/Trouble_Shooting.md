# Một vài lỗi thường gặp với CentOS, AlmaLinux, Rocky Linux

Không cần dài dòng, bài viết này Nhân Hòa sẽ điểm qua một vài lỗi hệ thống và cách giải quyết thường gặp đối với các bản phân phối thuộc nhánh RedHat như CentOS 7/8, AlmaLinux, Rocky Linux.

## I. Quá trình boot của Linux

Mỗi bản phân phối sẽ có những quy trình boot riêng biệt, tuy nhiên nhìn chung hầu hết sẽ dựa theo trình tự sau:

- Power + post: Bật nguồn
- Firmware device search: Thường là quá trình tìm kiếm Master Boot Record (MBR)
- Firmware reads bootloader: Đọc bootloader để tìm kiếm vị trí của OS
- Boot loader loads config (grub2): grub2 nạp cấu hình của bootloader
- Boot loader loads kernel anđ initramfs: Nạp kernel và initramfs
- Boot loader passes control to kernel: Bootloader chuyển quyền kiểm soát cho kernel
- Kernel initializes hardware + executes ```/sbin/init``` as pid 1: Kernel khởi tạo cấu hình phần cứng và tạo tiến trình ```init```
- Systemd executes all initrd targets (mounts filesystem on ```/sysroot```): systemd thực thi tất cả các initrd targets
- Kernel root FS switched from initramfs root (```/sysroot```) to system rootfs (```/```) and systemd re-executes as system version: Kernel chuyển filesystem từ ```/sysroot``` sang ```/``` và thực thi lại systemd
- Systemd looks for default target and starts/stops units as configured while automatically solving dependencies and login page apppears: Systemd tìm default target và start/stop các mục tiêu, cùng lúc đó tự động xử lý các phụ thuộc và đưa ra màn hình login

Quá trình boot của Linux khá phức tạp, tuy nhiên bên trên đây là cách mô tả tổng quan nhất để các bạn có thể hiểu hơn về bài viết này.

## II. Systemd Targets

Các ```targets``` cần phải kiểm tra các phụ thuộc (dependency). Chúng có 1 cấu hình "trước" và "sau" cho những service nào mà cần thiết để đáp ứng target. Ví dụ như ```arp.ethernet.service```, ```firewalld.service```, cần phải được khởi chạy và hoạt động trước khi ```network.target``` có thể được sử dụng. Nếu target này không hoạt động, các service như ```httpd```, ```nfs``` hay ```ldap``` cũng không start lên được. Có 4 boot target có thể được thiết lập:

- ```graphical.target``` (Giao diện người dùng)
- ```multi-user.target``` (Chế độ đa người dùng, text-based login)
- ```rescue.target``` (sulogin prompt, basic system initialization)
- ```emergency.target``` (sulogin prompt, initramfs pivot complete and system root mounted on ```/``` as read only)

Để xem boot target hiện tại, hãy sử dụng lệnh:

```sh
systemctl get-default
```

Bạn có thể thay đổi thay đổi target bằng cách cô lập nó. Điều này sẽ start/stop tất cả service và khởi chạy nó với target mới. Hãy tìm hiểu thêm về ```systemctl isolate new.target```

## III. Single User Mode

Khi sử dụng Linux, sẽ có không ít lần mà bạn cần phải boot vào single user mode để sửa các lỗi liên quan đến hệ điều hành. Để sử dụng ```rescue.target```, ta có thể thao tác như sau:

1. Tại màn hình grub2 (màn hình chọn kernel), hãy nhấn phím ```e```

2. Tìm kiếm dòng chỉ định kernel version (```vmlinuz```) và thêm đoạn cấu hình chỉ định target vào: ```systemd.unit=rescue.target```

3. Nhấn tổ hợp phím "Ctrl + X" để boot

4. Bạn sau đó sẽ cần nhập root password để tiếp tục. Nếu bạn thoát khỏi rescue shell, hệ thống sẽ tự boot vào target mặc định

## IV. Recover root password

Nếu bạn cần khôi phục mật khẩu đăng nhập, hãy sử dụng phương pháp sau để truy nhập vào hệ thống:

1. Reboot

2. Tại màn hình grub2 (màn hình chọn kernel), hãy nhấn phím ```e```

3. Đưa con trỏ đến cuối dòng mà có chỉ định kernel (```vmlinuz```). Bạn sẽ muốn loại bỏ tất cả console khác ngoại trừ TTY0, nhưng bước này sẽ không cần thiết với môi trường của bạn.

4. Thêm ```rd.break``` vào cuối dòng, điều này sẽ ngừng tiến trình boot ngay trước khi quyền điều khiển được trao lại từ initramfs cho system

5. Nhấn tổ hợp phím "Ctrl + X" để boot

Lúc này, 1 root shell với filesystem mount read-only vào ```/sysroot``` sẽ được đưa ra. Hãy remount nó với quyền write vào ```/sysroot```

```sh
mount -o remount,rw /sysroot
```

Chuyển đến chroot

```sh
chroot /sysroot
```

Thay đổi password của user mong muốn (ví dụ như ```root```)

```sh
passwd root
```

Nếu như bạn sử dụng SELinux, bạn nên cân nhắc gắn nhãn lại tất cả các file trước khi tiếp tục tiến trình boot (bạn có thể bỏ qua bước này nếu không sử dụng SELinux)

```sh
touch /.autorelabel
```

Sử dụng ```exit``` để thoát chroot. Sử dụng ```exit``` 1 lần nữa và hệ thống sẽ boot từ điểm mà chúng ta đã ngắt ở bước 4

## Xem lại boot logs

Xem lại log của lần boot fail trước có thể giúp ta rất nhiều trong quá trình troubleshooting. Journald logs thường được lưu trữ trong RAM và được giải phóng khi boot. Nếu bạn muốn giữ lại log này, nó có thể được xem lại với công cụ ```journalctl```. Làm theo các bước sau đây nếu bạn muốn giữ lại boot log:

Ở tài khoản root, tạo log file:

```sh
mkdir -p 2775 /var/log/journal && chown :systemd-journal /var/log/journal
systemctl restart systemd-journald
```

Để kiểm tra log của lần boot trước đó, sử dụng lệnh ```journalctl``` với tùy chọn ```-b```. Nếu không sử dụng đối số nào khác, ```-b``` sẽ lọc đầu ra chỉ bao gồm lần boot gần nhất. Thêm vào 1 số âm sẽ giúp ta kiểm tra được các lần boot xa hơn. Ví dụ:

```sh
journalctl -b-1 -p err
```

Lệnh trên sẽ giúp hiển thị error log từ lần boot trước lần boot mới nhất. Bạn có thể thay đổi giá trị số âm này để phù hợp với nhu cầu.

## Sửa chữa filesystem bị lỗi

1 trong những lỗi phổ biến nhất gây lỗi boot là cấu hình ```/etc/fstab``` sai. Bạn **KHÔNG THỂ** sử dụng ```rescue.target``` để sửa ```/etc/fstab``` được do target này cần nhiều chức năng hơn thế. Thay vào đó hãy dùng ```emergency.target```.

Dưới đây là 1 vài vấn đề mà bạn nên sử dụng ```emergency.target```:

- Filesystem lỗi (corrupt file system)
- UUID không tồn tại trong ```/etc/fstab```
- Mount point không tồn tại trong ```/etc/fstab```
- Mount option không chính xác trong ```/etc/fstab```

**Lưu ý:** Sau khi chỉnh sửa ```/etc/fstab``` trong emergency mode, hãy chạy lệnh sau:

```sh
systemctl daemon-reload
```

Dưới đây là các bước cần thiết để boot vào emergency mode và loại bỏ phần cấu hình lỗi trong ```/etc/fstab```

- Tại menu grub2 (màn hình chọn kernel), nhấn phím ```e```
- Tìm dòng chỉ định kernel (dòng có chữ ```vmlinuz```) và thêm đoạn sau vào cuối dòng đó: ```systemd.unit=emergency.target```
- Nhấn tổ hợp phím ```Ctrl + X``` để boot
- Bạn sẽ cần nhập password của root để tiếp tục
- Remount ```/``` để ta có thể sửa được ```fstab```

```sh
mount -o remount,rw /
```

- Chúng ta có thể sử dụng lệnh mount với tùy chọn ```-a``` để xem thứ gì đang lỗi

```sh
mount -a
```

- Loại bổ phần cấu hình lỗi trong ```/etc/fstab```

- Sử dụng lệnh ```mount -a``` 1 lần nữa để xem vấn đề đã được giải quyết chưa

- Sử dụng ```systemctl daemon-reload``` để reload tất cả unit files, và tạo lại tất cả dependency tree

Sau khi thoát emergency shell, hệ thống sẽ tiếp tục quá trình boot.

## Vấn đề liên quan đến Bootloader với Grub 2

File ```/boot/grub2/grub.cfg``` là tệp cấu hình chính. Tuy vậy, **đừng** trực tiếp thay đổi nội dung file này. Thay vào đó, sử dụng ```grub2-mkconfig``` để khởi tạo cấu hình grub2 mới sử dụng 1 tập các cấu hình khác nhau và danh sách của các kernel đã cài đặt. Lệnh ```grub2-mkconfig``` sẽ kiểm tra các tùy chọn trong ```/etc/default/grub``` như thời gian menu timeout mặc định và command line của kernel để sử dụng. Sau đó nó dùng 1 tập các script tại ```/etc/grub.d``` để khởi tạo file cấu hình cuối cùng.

Dưới đây là ví dụ về mối quan hệ của grub2

```
/boot/grub2/grub.cfg
               |
               |__________________
               |                  |
         /etc/default/grub         /etc/grub.d/*
```

**Lưu ý:** Để thay đổi tệp grub.cfg, bạn sẽ cần thay đổi file ```/etc/default/grub``` và các file trong ```/etc/grub.d```, sau đó mới tạo file ```grub.cfg``` mới với lệnh

```sh
grub2-mkconfig > /boot/grub2/grub.cfg
```

## Troubleshooting Grub

Để có thể troubleshooting được grub, ta phải hiểu được các cú pháp trong ```/boot/grub2/grub.cfg``` đã:

- Đầu tiên, bootable entries (các kernel version, target,...) sẽ được đặt trong khối ```menuentry```. Trong những khối này, ```linux16``` và ```initrd16``` trỏ đến kernel mà sẽ được nạp vào từ disk (bên cạnh kernel command line) và initramfs tương ứng. Trong màn hình tương tác khi boot, tab có thể được sử dụng để tìm những dòng này

- Dòng ```set root``` bên trong những khối trên không trỏ vào root file system, thay vào đó nó trỏ đến file system từ nơi mà grub2 nên nạp kernel và initramfs files. Cú pháp là ```harddrive.partition``` nơi ```hd0``` là ổ cứng đầu tiên trong hệ thống và ```hd1``` là ổ thứ 2. Phân vùng được chỉ định là ```msdos1``` cho phân vùng MBR đầu tiên hoặc ```gpt1``` cho phân vùng GPT đầu tiên.

VD:

```sh
### BEGIN /etc/grub.d/10_linux ###
menuentry 'CentOS Linux (3.10.0-514.26.2.el7.x86_64) 7 (Core)' --class centos --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-a2531d12-46f8-4a0f-8a5c-b48d6ef71275' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint='hd0,msdos1'  123455ae-46f8-4a0f-8a5c-b48d6ef71275
    else
      search --no-floppy --fs-uuid --set=root 123455ae-46f8-4a0f-8a5c-b48d6ef71275
    fi
```

Nếu bạn cần cài đặt lại bootloader trên 1 thiết bị, hãy sử dụng lệnh sau:

```sh
grub2-install <device>
```

## Sửa lỗi Grub

Hãy làm theo các bước sau nếu bạn muốn troubleshooting 1 hệ thống mà không thể boot sau khi đến được menu grub2

- Bạn nên bắt đầu bằng việc chỉnh sửa grub menu và tìm kiếm cú pháp lỗi. Nếu bạn tìm thấy, hãy sửa nó tạm thời và truy cập vào hệ thống để khắc phục nó triệt để. Nếu bạn không thể tìm thấy bất kỳ lỗi nào, hãy boot vào emergency target. Sau đó remount root ```/``` filesystem
- Kiểm tra cấu hình grub2 hiện tại bằng lệnh ```grub2-mkconfig```
- Nếu bạn không thấy bất kỳ lỗi nào, hãy kiểm tra cả file ```boot/grub2/grub.cfg``` vì có thể ai đó đã sửa trực tiếp lên file này. Rebuild cấu hình grub bằng lệnh ```grub2-mkconfig < /boot/grub2/grub.cfg```

Sau khi rebuild grub, hệ thống sẽ có thể boot được bình thường.