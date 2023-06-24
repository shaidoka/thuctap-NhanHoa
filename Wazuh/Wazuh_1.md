# Giám sát log file với Wazuh

## I. Giám sát log trong Linux

### 1. Basic usage

Cách thu thập dữ liệu log được cấu hình trong file ```/var/ossec/etc/ossec.conf``` (Linux) và ```C:\Program Files (x86)\ossec-agent\ossec.conf``` (Windows) ở phần ```localfile```, ```remote``` hoặc ```global```. Thiết lập thu thập log cũng có thể được làm thông qua ```agent.conf``` để tập trung phân phối những cấu hình này cho agents.

Cơ bản nhất, ta chỉ cần cung cấp tên của file cần giám sát theo format như sau:

```sh
<localfile>
  <location>/var/log/messages</location>
  <log_format>syslog</log_format>
</localfile>
```

### 2. Giám sát log sử dụng wildcard pattern cho tên file

Wazuh hỗ trợ POSIX wildcard pattern. Ví dụ, để phân tích mọi file mà kết thúc với ```.log``` trong đường dẫn ```/var/log```, ta sử dụng thiết lập sau:

```sh
<localfile>
    <location>/var/log/*.log</location>
    <log_format>syslog</log_format>
</localfile>
```

### 3. Giám sát date-based logs

Với những log file mà thay đổi theo ngày, ta có thể chỉ định 1 định dạng **strftime** để thay thế cho ngày, tháng, năm,.... Ví dụ, để giám sát log file như ```C:\Windows\app\log-08-12-15.log```, trong đó ```08``` là năm, ```12``` là tháng và ```15``` là ngày, cấu hình như sau:

```sh
<localfile>
    <location>C:\Windows\app\log-%y-%m-%d.log</location>
    <log_format>syslog</log_format>
</localfile>
```

### 4. Sử dụng biến môi trường

Biến môi trường như ```%WinDir%``` có thể sử dụng trong location pattern. Cấu hình sau đây là ví dụ đọc log từ IIS Server

```sh
<localfile>
    <location>%SystemDrive%\inetpub\logs\LogFiles\W3SVC1\u_ex%y%m%d.log</location>
    <log_format>iis</log_format>
</localfile>
```

### 5. Sử dụng nhiều output

*Không cần thiết lắm?*

Dữ liệu log có thể được gửi đến agent socket theo mặc định, nhưng cũng có thể chỉ định socket khác làm output. ```wazuh-logcollector``` sử dụng socket UNIX type để giao tiếp cho phép giao thức TCP hoặc UDP.

Để thêm 1 output socket mới ta cần chỉ định tag ```<socket>``` như ví dụ dưới đây

```sh
<socket>
    <name>custom_socket</name>
    <location>/var/run/custom.sock</location>
    <mode>tcp</mode>
    <prefix>custom_syslog: </prefix>
</socket>

<socket>
    <name>test_socket</name>
    <location>/var/run/test.sock</location>
</socket>
```

Khi socket được định nghĩa xong, ta có thể thêm socket đích vào mỗi localfile như thế này:

```sh
<localfile>
    <log_format>syslog</log_format>
    <location>/var/log/messages</location>
    <target>agent,test_socket</target>
</localfile>

<localfile>
    <log_format>syslog</log_format>
    <location>/var/log/messages</location>
    <target>custom_socket,test_socket</target>
</localfile>
```

## II. Giám sát log trong Windows

Windows event có thể được thu thập và chuyển tiếp tới manager, nơi mà chúng được xử lý và cảnh báo nếu khớp với bất kỳ rule nào. Có 2 loại Windows log:
- Eventlog (được hỗ trợ ở bất kỳ phiên bản Windows nào)
- Eventchannel (cho Windows Vista và các bản sau đó)

Windows logs là những thông điệp mô tả về các sự kiện (event) xảy ra trong hệ thống. Chúng được thu thập và thể hiện ở Event Viewer, nơi mà chúng được chia ra theo nguồn gốc tạo sinh ra nó.

Eventlog và eventchannel có thể cùng được giám sát bởi Wazuh. Việc xử lý dữ liệu eventchannel của Wazuh đã được cải thiện kể từ phiên bản 3.8, trong khi vẫn giữ nguyên các tính năng và cấu hình như cũ. Bản cập nhật log format này sử dụng Windows API để lấy tất cả sự kiện được sinh ra ở log của kênh giám sát.

Thông tin này được thu thập bởi Windows agent, bao gồm mô tả event, trường ```system``` tiêu chuẩn và thông tin ```eventdata``` đặc thù từ event. Khi event được gửi đến manager. Nó được xử lý và translated thành dạng JSON, thứ mà sẽ dễ để querying và filtering trường event.

Eventlog sử dụng Windows API để lấy được event từ Windows log và trả thông tin này theo 1 định dạng nhất định.

### 1. Windows Eventlog vs Windows Eventchannel 

Eventlog được hỗ trợ ở mọi phiên bản của Windows và có thể giám sát bất kỳ log nào trừ log của Ứng dụng hay Dịch vụ cụ thể, điều này nghĩa là thông tin mà có thể thu thập được giảm xuống còn System, Application, và Security

Mặt khác, Eventchannel được duy trì từ bản Windows Vista và có thể giám sát Application, Service logs cùng với Windows logs cơ bản. Thêm vào đó, việc query để filter theo bất kỳ field nào được hỗ trợ cho định dạng log này.

Với những thay đổi về định dạng log của ```eventchannel``` trong phiên bản v3.8 trở đi, số lượng field decoded đã tăng lên. Thêm vào đó, Windows ruleset cũng đã được cập nhật, mở rộng, và tổ chức lại theo nguồn của channel.

Hơn nữa, những sửa đổi này tạo thuận lợi cho quá trình tạo rule cũng như kích hoạt cảnh báo do sự kiện hiện được thu thập ở định dạng JSON.

### 2. Giám sát Windows Event Log với Wazuh

Để giám sát 1 Windows event log, ta cần chỉ định format là "eventlog", và location là tên của event log đó

```sh
<localfile>
    <location>Security</location>
    <log_format>eventlog</log_format>
</localfile>
```

Những log này được thu thập thông qua việc gọi đến Windows API và gửi nó cho manager, nơi mà chúng sẽ được cảnh báo nếu khớp bất kỳ rule nào.

### 3. Giám sát Windows Event Channel với Wazuh

Windows event channel có thể được giám sát bằng cách đặt tên của chúng và trường location và "eventchannel" ở localfile. Ví dụ như sau:

```sh
<localfile>
    <location>Microsoft-Windows-PrintService/Operational</location>
    <log_format>eventchannel</log_format>
</localfile>
```

Trong đó dấu ```/``` trong ```Microsoft-Windows-PrintService/Operational``` dùng để thay thế cho dấu ```%```

**Các channel và provider khả dụng:**

|Source|Channel location|Provider name|Description|
|:-|:-|:-|:-|
|Application|Application|Any|Log này thu thập tất cả event liên quan đến quản lý ứng dụng hệ thống và là một trong các channel chính bên cạnh Security và System|
|Security|Security|Any|Channel này thu thập thông tin liên quan đến hoạt động tạo người dùng và gropup, login, logoff, và phát hiện khi chính sách về audit bị thay đổi|
|System|System|Any|System channel thu thập event liên quan đến kernel và service|
|Sysmon|Microsoft-Windows-Sysmon/Operational|Microsoft-Windows-Sysmon|Sysmon giám sát hoạt động hệ thống như việc tạo và hủy process, kết nối mạng và file thay đổi|
|Windows Defender|Microsoft-Windows-Windows Defender/Operational|Microsoft-Windows-Windows Defender|Windows Defender log file cho thấy thông tin về các lần quét, malware detection, và hành động đã thực hiện với chúng|
|McAfee|Application|McLogEvent|Nguồn này đưa ra kết quả scan của McAfee, virus detection, và hành động đã thực hiện với chúng|
|EventLog|System|Eventlog|Nguồn này lấy thông tin về audit và Windows logs|
|Microsoft Security Essentials|System|Microsoft Antimalware|Phần mềm này cho thông tin về real-time protection cho hệ thống, malware-detection scans, và antivirus settings|

Và 1 vài channel nữa như Remote Access, Terminal Service, Powershell.

### 4. Windows ruleset redesign

Để dễ dàng bổ sung các quy tắc mới, eventchannel ruleset được phân chia theo channel mà chúng thuộc về. Điều này sẽ chắc chắn 1 cách đơn giản hơn để tổ chức ruleset và tìm 1 vị trí tốt hơn cho các custom rules. Để đạt được điều này, 1 vài thay đổi đã được thêm vào:
- Mỗi event channel có 1 hoặc nhiều file với rule riêng cho nó. Ví dụ, ta có thể tìm rule đặc thù cho ```System``` channel trong file ```0590-win-system_rules.xml```
- 1 file cơ sở bao gồm mọi parent rule lọc theo kênh giám sát đặc thù
- Rules được update và cải thiện để khớp với JSON event, cho thấy thông tin thích hợp trong rules description và tối ưu cách lọc chúng
- Nhiều channel rule mới được thêm vào. Mặc định, channel được giám sát là System, Security, và Application. Những channel này giờ có file riêng của chúng và bao gồm 1 tập rule hợp lý
- Mọi file có dải rule ID của nó để có thể được sắp xếp. Có khoảng 100 trăm ID set cho base rule và khoảng 500 cho mỗi channel file
- Nếu một vài rule không thể được phân loại, hoặc có quá ít thuộc 1 channel nào đó, chúng sẽ được bao gồm trong generic Windows rule file.

Để có 1 cái nhìn hoàn thiện về event nào tương đương với ```eventlog``` cũ nào và các phiên bản trước của ```eventchannel```, bảng này phân loại mọi rule theo nguồn của chúng, bao gồm dải rule ID và file nơi chúng được mô tả

|Source|Rule IDs|Rule file|
|:-|:-|:-|
|Base rules|60000 - 60099|0575-win-base_rules.xml|
|Security|60100 - 60599|0580-win-security_rules.xml|
|Application|60600 - 61099|0585-win-application_rules.xml|
|System|61100 - 61599|0590-win-system_rules.xml|
|Sysmon|61600 - 62099|0595-win-sysmon_rules.xml|
|Windows Defender|62100 - 62599|0600-win-wdefender_rules.xml|
|McAfee|62600 - 63099|0605-win-mcafee_rules.xml|
|Eventlog|63100 - 63599|0610-win-ms_logs_rules.xml|
|Microsoft Security Essentials|63600 - 64099|0615-win-ms-se_rules.xml|
|Others|64100 - 64599|0620-win-generic_ruules.xml|
|Powershell|91801 - 92000|0915-win-powershell.xml|

### 5. Use case

Phần này sẽ mô tả 1 use case cơ bản khi 1 event về cài đặt xảy ra.

Log cài đặt sẽ được thu thập ở Application channel. Để giám sát logs tạo ra bởi nguồn này với định dạng eventchannel, file cấu hình cần phải bao gồm:

```sh
<localfile>
  <location>Application</location>
  <log_format>eventchannel</log_format>
</localfile>
```

Bước tiếp theo là cài đặt 1 ứng dụng mới. Một khi nó được cài đặt, Wazuh manager sẽ tạo 1 JSON event liên quan đến tiến trình cài đặt:

```sh

```

Event này có thể được lọc field by field trong trường hợp 1 cảnh báo muốn kích hoạt khi nó xảy ra. Trong use case này, bộ lọc sử dụng sẽ là tên nhà cung cấp và event ID như sau đây:

```sh
<rule id="60612" level="3">
    <field name="win.system.providerName">MsiInstaller</field>
    <field name="win.system.eventID">^11707$|^1033$</field>
    <options>alert_by_email</options>
    <description>Application Installed $(win.eventdata.data)</description>
    <options>no_full_log</options>
</rule>
```

**Lọc event từ Windows Event Channel với query**

Event từ Windows Event channel có thể được lọc như dưới đây. Chỉ những event có level nhỏ hơn hoặc bằng 3 được kiểm tra trong ví dụ này

```sh
<localfile>
  <location>System</location>
  <log_format>eventchannel</log_format>
  <query>Event/System[EventID=7040]</query>
</localfile>
```

Người dùng có thể filter event với level khác nhau bằng cú pháp

```sh
<localfile>
    <location>System</location>
    <log_format>eventchannel</log_format>
    <query>
        \<QueryList\>
            \<Query Id="0" Path="System"\>
                \<Select Path="System"\>*[System[(Level&lt;=3)]]\</Select\>
            \</Query\>
        \</QueryList\>
    </query>
</localfile>
```