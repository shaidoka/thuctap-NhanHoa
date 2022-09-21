# Crontab và cách sử dụng Crontab

Một trong những nỗi khổ của sysadmin là phải làm task cả ngày lẫn đêm. Có những lệnh, script phải chạy ngoài giờ như những bản backup hay cập nhật, và người admin không thể lúc nào cũng thức đêm để thực hiện những việc này

Do đó, tiện ích giúp chạy lệnh 1 cách tự động ra đời như 1 lẽ dĩ nhiên. Hai dịch vụ ```cron``` và ```at``` giúp các sysadmin có thể lên lịch cụ thể cho các task. Sau đó chúng sẽ tự động chạy vào những thời điểm đó. Dịch vụ ```at``` sẽ chỉ định 1 task chạy 1 lần duy nhất vào 1 thời gian xác định. Trong khi đó, cron cho phép lên lịch thực hiện task lặp lại nhiều lần. Thời gian lặp có thể theo ngày, theo tuần hoặc theo tháng

### 1. Crontab là gì?

```Cron``` là 1 cách để tạo và chạy các lệnh theo 1 chu kỳ xác định. Đây là tiện ích giúp lập lịch trình để chạy những dòng lệnh bên phía server nhằm thực thi 1 hoặc nhiều công việc nào đó theo thời gian được lập sẵn

### 2. Cách thức hoạt động

Một ```cron schedule``` đơn giản là 1 text file. Mỗi user có 1 ```cron schedule``` riêng, file này thường nằm ở ```var/spool/cron```. Crontab files không cho phép bạn tạo hoặc chỉnh sửa trực tiếp với bất kỳ trình text editor nào, trừ phi bạn dùng lệnh crontab

```crond daemon``` là 1 dịch vụ chạy ```background enable``` các chức năng của cron. Dịch vụ cron sẽ check các file trong thư mục ```/var/spool/cron``` và ```/etc/cron.d```, và file ```/etc/anacrontab```. Các file này chứa nội dung xác định các công việc mà cron phải chạy trong những khoảng thời gian khác nhau. Các dịch vụ và ứng dụng hệ thống thường sẽ thêm các file công việc vào ```/etc/cron.d```

Một vài lệnh thường dùng:

- Tạo hoặc chỉnh sửa file crontab:

```sh
crontab -e
```

- Hiển thị file crontab

```sh
crontab -l
```

- Xóa file crontab

```sh
crontab -r
```

### 3. Cài đặt Crontab

Hầu hết VPS đều được cài đặt sẵn crontab, nếu không, có thể cài đặt bằng lệnh sau

```sh
yum install cronie
```

Khởi động dịch vụ crontab và cho nó khởi động cùng hđh

```sh
systemctl start crond
systemctl enable crond
```

### 4. Một số ứng dụng phổ biến của cron

- Lên lịch backup vào buổi đêm
- Đặt thời gian phần cứng dựa trên thời gian hệ thống
- Tạo ra các tin nhắn để thông báo về các thông số như disk usage,...

### 5. Cách sử dụng Crontab Linux 

Cron hoạt động dựa trên các lệnh được chỉ định trong cron table (crontab). Mỗi người dùng, kể cả root, đều có thể có 1 file cron. Các file này theo mặc định sẽ không tồn tại. Nhưng ta có thể tạo nó trong thư mục ```/var/spool/cron``` bằng cách dùng lệnh ```crontab -e```. Ngoài ra, lệnh này cũng có thể được dùng để chỉnh sửa 1 file cron. **Không nên chỉnh sửa file cron bằng các text editor khác**. Vì lệnh crontab không chỉ cho phép chỉnh sửa file, nó còn khởi động lại crond daemon khi ta lưu và thoát trình editor. Lệnh crontab sử dụng Vi làm editor cơ bản của nó, vì Vi luôn luôn khả dụng

Các file cron mặc định sẽ trống, do đó lệnh cần phải được thêm từ đầu. Cấu trúc cơ bản của 1 lệnh cron như sau:

```sh
<phút> <giờ> <ngày trong tháng> <tháng> <ngày trong tuần> <tên user> <lệnh cần thực thi>
```

**VD:**

```sh
#crontab -e
SHELL=/bin/bash
MAILTO=root@example.com
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

# Backup sử dụng rsbu đến ổ 4TB HDD và ổ ngoại vi 4TB
01 01 * * * /usr/local/bin/rsbu -vbd1 ; /usr/local/bin/rsbu -vbd2

# Thiết lập thời gian phần cứng đồng bộ với thời gian hệ thống
03 05 * * * /sbin/hwclock --systohc

# Thực hiện update vào mỗi ngày đầu tiên của tháng
25 04 1 * * /usr/bin/dnf -y update
```

Trong đó, 3 dòng đầu tiên có nhiệm vụ thiết lập môi trường mặc định. Môi trường phải được thiết lập phù hợp với nhu cầu của người dùng. Bởi vì cron không cung cấp 1 môi trường cụ thể nào cả. Biến ```SHELL``` chỉ định shell để sử dụng khi các câu lệnh được thực thi. Trong ví dụ này, shell ```Bash``` được chỉ định. Biến ```MAILTO``` đặt địa chỉ mail nhận các kết quả của cronjob. Các mail này có thể cung cấp trạng thái của các cronjob (backup, update,...). Đồng thời bao gồm cả output mà người dùng muốn khi chạy chương trình thủ công từ cmd. ```PATH``` để thiết lập path (chứ sao nữa?).

### 6. Một số mẹo trong việc lên lịch với crontab linux

Câu lệnh dưới đây cho job chạy trong vòng 1 phút, mỗi giờ 1 lần, từ 9h01 đến 17h01

```sh
01 09-17 * * * /usr/local/bin/hourlyreminder.sh
```

Đôi khi, có những job cần được thực hiện sau mỗi 2, 3 hay 4 giờ. Khi đó, ta có thể lấy thương số của giờ và khoảng thời gian mong muốn. Chẳng hạn như */3, tương đương với job sau mỗi 3 giờ. Hay 6-18/3 để chạy job mỗi 3 tiếng từ 6h sáng đến 18h chiều. Các khoảng thời gian khác cũng có thể được chia tương tự. Lấy ví dụ, biểu thức */15 ở vị trí phút có nghĩa là "chạy job sau mỗi 15p"

```sh
*/5 08-18/2 * * * /usr/local/bin/mycronjob.sh
```

Có 1 điều cần lưu ý: các biểu thức chia phải cho ra kết quả có phần dư bằng 0, khi đó job mới có thể chạy. Do đó, trong ví dụ này, job được thiết lập để chạy 5 phút 1 lần trong các giờ chẵn từ 8h sáng đến 18h chiều.

### 7. Giới hạn truy cập cron trong crontab linux

Việc thường xuyên sử dụng cron có thể dẫn đến 1 số lỗi, chẳng hạn như tài nguyên hệ thống (bộ nhớ, CPU,...) bị sử dụng quá nhiều. Do đó, sysadmin có thể giới hạn quyền truy cập của người dùng để hạn chế lỗi xảy ra. Cụ thể, ta có thể tạo file ```/etc/cron.allow```, chứa danh sách người dùng có quyền tạo cronjob. Tuy nhiên, người dùng root không thể bị chặn sử dụng cron.

Do đã ngăn người dùng non-root tạo cronjob, người dùng root có thể xem xét thêm 1 vài cronjob vào crontab của mình. Tuy nhiên, những cronjob này sẽ không chạy dưới quyền root. VD sau đây cho thấy 1 định nghĩa job, chạy dưới quyền người dùng "student":

```sh
04 07 * * * student /usr/local/bin/myronjob.sh
```

Nếu không có người dùng được chỉ định, job sẽ chạy theo người dùng sở hữu file crontab. Trong trường hợp này chính là root

### 8. cron.d

Thư mục ```/etc/cron.d``` là nơi chứa các ứng dụng, như SpamAssassin, sysstat, file cài đặt cron,.... Vì không có người dùng SpamAssassinn hay sysstat, các chương trình này cần 1 nơi để lưu trữ các file cron. Do đó, chúng sẽ được đặt ở trong ```/etc/cron.d```

File ```/etc/cron.d/sysstat``` chứa các cronjob liên quan đến báo cáo hoạt động hệ thống (SAR). Các file cron này có cùng định dạng với file cron của người dùng

```sh
# Chạy công cụ báo cáo hoạt động hệ thống mỗi 10 phút
*/10 * * * * root /usr/lib64/sa/sa1 1 1

# Tạo 1 báo cáo tổng kết tiến trình trong ngày vào lúc 23h53
53 23 * * * root /usr/lib64/sa/sa2 -A
```

Cron file sysstat trên gồm 2 dòng lệnh để thực hiện các task. Dòng thứ nhất chạy lệnh ```sa1``` mỗi 10p để thu thập dữ liệu trong các file nhị phân đặc biệt, được đặt ở thư mục ```/var/log/sa```. Sau đó, mỗi tối vào 23h53, chương trình ```sa2``` sẽ chạy để tạo 1 bản tóm tắt hàng ngày

### 9. anacron

Chương trình anacron thực hiện các chức năng tương tự như crond. Nhưng nó có thể chạy các job đã bị bỏ qua, chẳng hạn như khi máy tính đã tắt hoặc không thể chạy job trong 1 thời gian nhất định. Công cụ này rất hữu ích với người dùng laptop hoặc các máy tính thường xuyên được đưa vào chế độ Sleep

Ngay sau khi máy tính được khởi động, anacron sẽ kiểm tra các job đã được cấu hình có bỏ lỡ lịch chạy nào không. Nếu có, các job này sẽ được chạy ngay lập tức. Nhưng các job sẽ chỉ chạy 1 lần, bất kể bao nhiêu lần nó bị bỏ lỡ

Bên cạnh đó, chương trình anacron cung cấp 1 số tùy chọn dễ dàng để chạy các task được lên lịch thường xuyên. Chỉ cần cài đặt các script vào trong thư mục ```/etc/cron.[hourly|daily|weekly|monthly]```, tùy vào tần suất ta muốn các job chạy

**Cách thức vận hành của anacron:**

1. Dịch vụ crond chạy các cronjob được chỉ định trong ```/etc/cron.d/0hourly```

```sh
# Chạy job hàng giờ
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root
01 * * * * root run=parts /etc/cron.hourly
```

2. Cronjob được chỉ định trong ```/etc/cron.d/0hourly``` chạy chương trình ```run-parts``` mỗi giờ 1 lần

3. Chương trình ```run-parts``` sẽ chạy tất cả script có trong thư mục ```/etc/cron.hourly```

4. Thư mục ```/etc/cron.hourly``` chứa script ```0anacron```, script này sẽ chạy chương trình anacron bằng config file ```/etc/anacrontab``` ở dưới đây:

```sh
SHELL=/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root
# Thời gian trễ tối đa được thêm vào thời gian trễ cơ bản của job
RANDOM_DELAY=45
# Job sẽ được chạy trong những khoảng thời gian này
START_HOURS_RANGE=3-22
#<khoảng thời gian (tính theo ngày)> <trễ (tính theo phút)> <định danh job> <lệnh>
1 5 cron.daily nice run-parts /etc/cron.daily
7 25 cron.weekly nice run-parts /etc/cron.weekly
@monthly 45 cron.monthly nice run-parts /etc/cron.monthly
```

5. Cuối cùng, chương trình anacron chạy các chương trình có trong ```/etc/cron.daily``` hàng ngày, ```/etc/cron.weekly``` hàng tuần, ```/etc/cron.monthly``` hàng tháng. Lưu ý là thời gian delay ở mỗi dòng giúp các job này không bị trùng nhau

Tóm lại, anacron không được thiết kế để chạy theo thời gian cụ thể. Mà nó sẽ chạy các chương trình tại những khoảng thời gian xác định với thời gian bắt đầu xác định. Chẳng hạn như 3h sáng hàng ngày, vào Chủ Nhật, vào ngày đầu tháng. Nếu có bất kỳ job nào bị bỏ lỡ, anacron sẽ chạy bù cho chúng 1 lần 

### 10. Shortcut trong crontab linux

File ```/etc/anacrontab``` ở trên cho ta thấy cách các shortcut có thể được sử dụng, chỉ định 1 số thời gian phổ biến. Các shortcut thời gian này có thể thay thế đến 5 trường thường dùng để chỉ định thời gian. Ký tự @ dùng để xác định shortcut cho cron. Bên dưới là danh sách 1 số shortcut và ý nghĩa của chúng

- @reboot: chạy sau khi reboot
- @yearly: chạy hàng năm (0 0 1 1 *)
- @annually: chạy hàng năm
- @monthly: chạy hàng tháng (0 0 1 * *)
- @weekly: chạy hàng tuần (0 0 * * 0)
- @daily: chạy hàng ngày (0 0 * * *)
- @hourly: chạy hàng giờ (0 * * * *)

Các shortcut này có thể được sử dụng trong nhiều file crontab linux khác nhau, chẳng hạn như ```/etc/cron.d```