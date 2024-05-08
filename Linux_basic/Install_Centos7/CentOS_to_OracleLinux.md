# Chuyển đổi từ CentOS sang Oracle Linux

Nếu bạn tìm đến bài viết này, hẳn các bạn đã biết CentOS 7 sẽ (hoặc là đã?) ngừng hỗ trợ cập nhật các bản vá về bảo mật vào ngày 30/06/2024 (nói ngắn gọn là End Of Life). Điều này chắc chắn sẽ ảnh hưởng đến không ít doanh nghiệp vì CentOS 7 giống như distro "quốc dân" trên nhiều lĩnh vực.

## Tại sao lại là Oracle Linux?

Việc nâng cấp lên các bản phân phối mới hơn là điều tất yếu phải suy xét. Tuy vậy, có một vài vấn đề mà người quản trị hệ thống phải cân nhắc thật kỹ lưỡng trước khi thực hiện "chuyển nhà":

1. **Nên chọn bản phân phối nào?** - Bản phân phối được lựa chọn phải đảm bảo cùng thuộc nhánh RedHat và cũng phải có những lợi ích vượt trội so với phiên bản cũ phải không nào. Oracle Linux chắc chắn là 1 lựa chọn tuyệt vời khi đáp ứng đầy đủ các nhu cầu trên. Hãy tìm hiểu thêm về Oracle Linux tại:

[Oracle Linux - Giải pháp thay thế cho CentOS 7](https://wiki.nhanhoa.com/kb/oracle-linux-giai-phap-thay-the-cho-centos-7/)

2. **Tính tương thích** - Đương nhiên rồi, tính tương thích luôn là vấn đề quan trọng nhất khi thực hiện bất kể nâng cấp nào, và thật may mắn rằng Oracle Linux sẽ đảm bảo cho bạn về vấn đề này

3. **Tiện lợi và nhanh chóng** - Một cách thức nâng cấp tiện lợi và nhanh chóng mặc dù không đóng vai trò quyết định nhưng lại vô cùng cần thiết khi tránh cho bạn những sai sót, cũng như tiết kiệm thời gian trong quá trình chuyển đổi

## Phiên bản và kiến trúc hỗ trợ

Script nâng cấp hiện tại cho phép chuyển đổi từ CentOS 6, CentOS 7, CentOS 8, Rocky Linux 8 và Rocky Linux 9 trên các kiến trúc ```x86_x64``` và ```aarch64```. Nó không hỗ trợ CentOS Stream

## I. Bước chuẩn bị

**LƯU Ý:** Script này đang được phát triển và không được thiết kế để xử lý tất cả các loại cấu hình. Hãy chắc chắn là bạn đã backup tất cả những thứ cần thiết của hệ thống trước khi thực hiện bất kỳ điều gì. Script sẽ **không** cho phép bạn rollback hay undo trong trường hợp nâng cấp thất bại

**LƯU Ý 2:** CentOS 8 đã End of life rồi, và repos của bản phân phối này cũng được chuyển sang ```vault.centos.org```. Hãy chắc chắn là máy chủ CentOS 8 của bạn đã up-to-date và có thể truy cập vào những repos kể trên

### Loại bỏ tất cả phiên bản kernel không tiêu chuẩn

Do lỗ hổng bảo mật [GRUB2 BootHole](https://blogs.oracle.com/linux/cve-2020-10713-grub2-boothole), SecureBoot của Oracle Linux chỉ có thể boot vào kernels mà được ký bởi Oracle và script chỉ có thể thay thế các kernels mặc định của CentOS.

Trong khi điều này có thể không ảnh hưởng nếu SecureBoot bị disabled, nếu một ngày nào đó bạn bật nó lên thì có thể dẫn đến hệ thống không thể boot được. Vì lý do đó, chúng tôi rất khuyến khích bạn loại bỏ tất cả kernels không tiêu chuẩn.

Ví dụ như bất kỳ kernel nào mà được cài đặt không phải bởi ```base``` và ```updates``` repo. Điều này bao gồm cả [centosplus](https://wiki.centos.org/AdditionalResources/Repositories/CentOSPlus) kernels.

1. Hãy đảm bảo CentOS của bạn có cấu hình ```yum``` hoặc ```dnf``` đang hoạt động. VD như không có repo cũ.

2. Disable toàn bộ repo không thuộc về CentOS. Bạn có thể kích hoạt lại nó sau khi chuyển đổi thành công.

3. Đảm bảo còn trống ít nhất 5GB disk tại ```/var/cache```

4. Tất cả update tự động phải được tắt. Ví dụ như ```yum-cron``` thì nên disable đi

## II. Sử dụng

1. SSH vào máy chủ CentOS Linux 6, 7 hoặc 8 hoặc Rocky Linux 8 hoặc 9 và đảm bảo có quyền ```sudo```

2. Clone hoặc download script chuyển đổi, bạn có thể download nó bằng lệnh sau:

```sh
wget https://raw.githubusercontent.com/oracle/centos2ol/main/centos2ol.sh
```

3. Thực thi script

```sh
sudo bash centos2ol.sh
```

### Các tùy chọn sử dụng

- ```-r```: Cài đặt lại tất cả CentOS RPMs với Oracle Linux RPMs

Nếu 1 hệ thống được chuyển đổi thành Oracle Linux và không có phiên bản Oracle Linux mới hơn nào của 1 package đã được cài đặt trước đó, thì phiên bản CentOS vẫn được giữ nguyên. Tùy chọn này tiến hành cài lại bất kỳ RPM nào của CentOS bất kể nó có giống Oracle Linux hay không. Điều này không quá cần thiết và không ảnh hưởng đến hoạt động của hệ thống, tuy nhiên nó giúp bạn loại bỏ các GPG Key của CentOS khỏi truststore. 1 danh sách tất cả các RPM không phải của Oracle sẽ được hiển thị sau khi quá trình cài đặt lại.

- ```-k```: Không cài đặt UEK kernel và tắt UEK repos

Tùy chọn này sẽ không cài đặt UEK kernel và tắt UEK yum repositories

- ```-V```: Xác thực thông tin RPM trước khi và sau khi chuyển đổi

Tùy chọn này tạo 4 tệp đầu ra tại ```/var/tmp/```:

- ```${hostname}-rpms-list-[before|after].log```: 1 danh sách được sắp xếp của các packages được cài đặt trước và sau khi chuyển sang Oracle Linux
- ```${hostname}-rpms-verified-[before|after].log```: kết quả xác thực cho tất cả các package trước và sau khi chuyển sang Oracle Linux

## III. Hạn chế

1. Script này hiện tại cần phải giao tiếp được với cả CentOS hoặc Rocky và Oracle Linux yum repositories bằng cách trực tiếp hoặc thông qua proxy

2. Script hiện tại không hỗ trợ instances mà được đăng ký bởi 1 công quản lý của bên thứ 3 như Spacewalk, Foreman, hoặc Uyuni

3. Tương thích với các packages từ các bên thứ 3 nhưng không đảm bảo

4. Packages mà được cài đặt bởi bên thứ 3 và/hoặc kernel module mã nguồn đóng (như các phần mềm antivirus) có thể không hoạt động sau khi chuyển đổi

5. Script chỉ enable base repositories cần thiết để chuyển đổi sang Oracle Linux. Người sử dụng sẽ cần phải enable thêm repositories khác để updates các packages đã được cài đặt

## Kết luận

Vậy đó, để chuyển từ CentOS sang Oracle Linux chỉ đơn giản như vậy thôi. Mặc dù có nhiều lưu ý, nhưng để thực hiện thì rất đơn giản.

Hãy sớm chuyển đổi các hệ thống cũ lên Oracle Linux để đảm bảo tính ổn định lâu dài nhé!