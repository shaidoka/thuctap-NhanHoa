# Cấu hình cơ bản

Ta có thể thiết lập FIM capability trên Wazuh server và Wazuh agent. 1 file cấu hình FIM mặc định tồn tại ở cả Wazuh server hay agent, do đó ta có thể đơn giản chỉnh sửa file này để phù hợp với nhu cầu.

### Real-time monitoring

Thuộc tính ```realtime``` giúp kích hoạt giám sát real-time/continous directories trên Windows và Linux endpoint.

Để theo dõi file trong thời gian thực, cấu hình FIM module với thuộc tính ```realtime``` trong tùy chọn ```directories```. Giá trị cho phép của ```realtime``` là ```yes``` hoặc ```no```, và nó chỉ hoạt động với directories, không phải với files. Phát hiện thay đổi thời gian thực được tạm dừng khi FIM module thực hiện quét định kỳ và tái kích hoạt ngay sau khi đợt scan này hoàn thành.

Ví dụ:

```sh
  <syscheck>
    <directories realtime="yes">FILEPATH/OF/MONITORED/DIRECTORY</directories>
  </syscheck>
```

Restart wazuh-agent

```sh
# Linux
systemctl restart wazuh-agent
# Windows
Restart-Service -Name wazuh
```

### Record file attributes

Khi cấu hình FIM module để giám sát file và directory chỉ định, nó ghi lại metadata của file và giám sát chúng. Ta có thể sử dụng tùy chọn ```directories``` để thiết lập file metadata chỉ định mà FIM module phải thu thập và bỏ qua. Tùy chọn ```directories``` hỗ trợ một vài thuộc tính như sau

|Attribute|Default value|Allowed value|Description|
|:-|:-|:-|:-|
|check_all|yes|yes,no|Ghi lại giá trị của tất cả thuộc tính bên dưới|
|check_sum|yes|yes,no|Ghi lại giá trị băm MD5, SHA-1 và SHA-256 của tệp|
|check_sha1sum|yes|yes,no|Ghi lại giá trị băm SHA-1 của tệp|
|check_md5sum|yes|yes,no|Ghi lại giá trị băm MD5 của tệp|
|check_sha256sum|yes|yes,no|Ghi lại giá trị băm SHA-256 của tệp|
|check_size|yes|yes,no|Ghi lại size của tệp|
|check_owner|yes|yes,no|Ghi lại owner của file trong Linux|
|check_group|yes|yes,no|Ghi lại group owner của file/directory. Trong Windows, ```gid``` luôn là 0 và group name trống|
|check_perm|yes|yes,no|Ghi lại permission của file/directory. Trên Windows, 1 danh sách cho hoặc không cho phép permission sẽ được ghi lại với mỗi người dùng hoặc group. Nó hoạt động trên Linux và Windows với phân vùng NTFS|
|check_attrs|yes|yes,no|Ghi lại thuộc tính của tệp trong Windows|
|check_mtime|yes|yes,no|Ghi lại thời gian thay đổi của tệp|
|check_inode|yes|yes,no|Ghi lại inode trong Linux|

Khi có conflict giữa các tùy chọn trên cùng 1 thuộc tính, giá trị cuối cùng sẽ được chấp nhận. Ví dụ, cấu hình sau thiết lập tùy chọn ```check_mtime``` thành ```yes```

```sh
<directories check_all="no" check_mtime="yes">/etc</directories>
```

Trong khi dưới đây thì ngược lại

```sh
<directories check_mtime="yes" check_all="no">/etc</directories>
```

Ta có thể thấy dưới đây 1 ví dụ cấu hình về cách ta disable check giá trị băm SHA-1 của file

```sh
  <syscheck>
    <directories check_sha1sum="no">FILEPATH/OF/MONITORED/FILE</directories>
  </syscheck>
```

### Scheduled scans

Để thay đổi lịch trình quét của FIM module, ta có thể cấu hình tùy chọn ```<frequency>``` của Wazuh FIM module. Tùy chọn này định nghĩa khoảng thời gian giữa 2 lần scan. Ta có thể thay đổi cấu hình để chạy ở 1 thời điểm nhất định trong ngày, trong tuần với tùy chọn ```scan_time``` hay ```scan_day```. Quét định kỳ giúp tránh làm tràn cảnh báo nếu ta cứ update file liên tục.

FIM module quét mỗi 12h (43200s) theo mặc định. Trong ví dụ sau đây, ta sẽ cấu hình nó là 900s

```sh
<syscheck>
   <frequency>900</frequency>
</syscheck>
```

Lưu ý restart agent sau khi cấu hình.

Hoặc chỉ định ngày giờ như sau:

```sh
<syscheck>
   <scan_time>10pm</scan_time>
   <scan_day>saturday</scan_day>
</syscheck>
```

### Báo cáo nội dung thay đổi của file

Thuộc tính ```report_changes``` cho phép FIM module báo cáo chính xác nội dung nào trong file thay đổi. Điều này ghi lại text thêm vào hoặc xóa đi từ file được giám sát. Ta có thể cấu hình chức năng này bằng cách kích hoạt thuộc tính ```report_changes``` của tùy chọn ```directories```. Giá trị cho phép của thuộc tính này là ```yes``` hoặc ```no```. Nó hoạt động với cả directories và file trên Windows, macOS, Linux endpoint.

Ta phải cẩn thận khi sử dụng thuộc tính ```report_changes```, do wazuh sẽ copy tất cả file được giám sát đến 1 đường dẫn private, do đó làm tăng dung lượng sử dụng. Đường dẫn này ở các OS như sau:
- Linux: ```/var/ossec/queue/diff/local/```
- macOS: ```Library/Ossec/queue/diff/local/```
- Windows: ```C:\Program Files (x86)\ossec-agent\queue\diff\local\```

Ví dụ:

```sh
<syscheck>
   <directories check_all="yes" report_changes="yes">FILEPATH/OF/MONITORED/FILE</directories>
</syscheck>
```

Trong cấu hình bên dưới, ta có thể thấy cách sử dụng ```report_changes``` cho tất cả file ở đường dẫn```FILEPATH/OF/MONITORED/DIRECTORY```. Ta có thể thấy cách ngăn FIM module ghi lại chính xác nội dung thay đổi vào ```FILEPATH/OF/MONITORED/DIRECTORY/private.txt```.

```sh
<syscheck>
   <directories check_all="yes" report_changes="yes">FILEPATH/OF/MONITORED/DIRECTORY</directories>
   <nodiff>FILEPATH/OF/MONITORED/DIRECTORY/private.txt</nodiff>
</syscheck>
```

### Ngoại lệ

Ta có thể cấu hình FIM module để bỏ qua cảnh báo của 1 số file/directory nhất định sử dụng 1 trong 2 cách sau:

**Sử dụng tùy chọn ignore**

Ta có thể dùng tùy chọn ```ignore``` để bỏ qua 1 đường dẫn. Nó cho phép 1 entry của file hoặc directory mỗi dòng. Tuy vậy, ta có thể dùng nhiều dòng để thêm ngoại lệ cho nhiều đường dẫn.

Ví dụ:

```sh
<syscheck>
   <ignore>FILEPATH/OF/MONITORED/FILE</ignore>
   <ignore type="sregex">.log$|.tmp$</ignore>
</syscheck>
```

**Sử dụng custom rules**

Một phương pháp thay thế sử dụng rule của alert level 0. Phương pháp này bỏ qua cảnh báo của các tệp chỉ định và đường dẫn scan bởi FIM module. Alert level 0 rule được silent và Wazuh server không báo cáo về nó.

Ví dụ: Ta sẽ giám sát đường dẫn ```/var/www/htdocs``` nhưng silent cảnh báo của tệp ```/var/www/htdocs/private.html```

Ở Linux endpoint:

```sh
<syscheck>
   <directories>/var/www/htdocs</directories>
</syscheck>
```

Restart agent

```sh
systemctl restart wazuh-agent
```

Ở Wazuh server:

Tạo file ```fim_ignore.xml``` ở đường dẫn ```/var/ossec/etc/rules/```

```sh
touch /var/ossec/etc/rules/fim_ignore.xml
```

Thêm đoạn sau vào file đó:

```sh
<group name="syscheck">
  <rule id="100345" level="0">
    <if_group>syscheck</if_group>
    <field name="file">/var/www/htdocs/private.html</field>
    <description>Ignore changes to $(file)</description>
  </rule>
</group>
```

Restart wazuh service

```sh
systemctl restart wazuh-manager
```