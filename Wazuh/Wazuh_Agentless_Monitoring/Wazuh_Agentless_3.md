# Cấu hình

Ta cần cấu hình Wazuh server để giám sát các agentless endpoint được liên kết. Để cấu hình tính năng agentless monitoring, ta cần cài đặt gói ```expect```, sau đó thêm agentless monitoring configuration setting trên Wazuh server

```sh
yum install -y expect
```

## Các thuộc tính được hỗ trợ

Bảng sau giải thích các thuộc tính khác nhau mà agentless monitoring module hỗ trợ

|Attribute|Allowed values|Description|
|:-|:-|:-|
|type|ssh_integrity_check_bsd, ssh_integrity_check_linux, ssh_pixconfig_diff, ssh_generic_diff|Định nghĩa loại cấu hình agentless để chạy trên endpoint|
|frequency|integer|Số giây giữa 2 lần kiểm tra agentless endpoint|
|host|username@hostname|Định nghĩa username và hostname (hoặc IP) của agentless endpoint|
|state|periodic, periodic_diff|**Periodic**: Đầu ra được phân tích với Wazuh ruleset nếu nó là log được giám sát. **Periodic_diff**: Đầu ra được so sánh với đầu ra của lần check trước, và tạo cảnh báo nếu có gì thay đổi|
|arguments|Dành cho BSD integrity check và Linux integrity check, đây là danh sách các tệp và thư mục được phân tách bằng dấu cách để được giám sát. Với generic diff setting, đây là 1 lệnh để chạy trên endpoint|Định nghĩa đối số đưa vào agentless check|

## Giám sát files, directories, hoặc configuration settings trên 1 endpoint

Setting này cho phép agentless monitoring module giám sát những thay đổi trên tệp, đường dẫn, và cấu hình của 1 endpoint. Ta có thể cấu hình điều này sử dụng các loại cấu hình agentless sau
- BSD integrity check
- Linux integrity check
- Pix config

### BSD integrity check

Ta cần thiết lập ```type``` là ```ssh_integrity_check_bsd``` cho BSD endpoints. 1 danh sách cách nhau bởi dấu cách của tệp hoặc đường dẫn có thể được tham chiếu bên trong phần cấu hình sử dụng thẻ ```<arguments>```. Sử dụng cấu hình này, Wazuh sẽ thực hiện 1 integrity check trên các tệp/đường dẫn được chỉ định của endpoint. 1 cảnh báo được tạo nếu chúng có thay đổi.

Thêm thiết lập dưới đây vào ```/var/ossec/etc/ossec.conf``` file của Wazuh server để giám sát tính toàn vẹn của ```/bin``` và ```/var```

```sh
<agentless>
  <type>ssh_integrity_check_bsd</type>
  <frequency>20000</frequency>
  <host>user@test.com</host>
  <state>periodic</state>
  <arguments>/bin /var</arguments>
</agentless>
```

Nhiều file và directory có thể được thêm vào thẻ ```<arguments>```, tách nhau bởi dấu cách

### Linux integrity check

Tương tự bên trên, thay ```<type>``` thành ```ssh_integrity_check_linux``` là được

### Pix config

Tương tự bên trên, thay ```<type>``` thành ```ssh_pixconfig_diff``` là được

## Chạy lệnh trên endpoint

Thiết lập này cho phép agentless monitoring module chạy lệnh trên endpoint được giám sát. Khi output của lệnh thay đổi, nó kích hoạt 1 cảnh báo trên Wazuh server

Ta có thể thiết lập điều này sử dụng loại cấu hình agentless là ```generic diff```

### Generic diff

Ta có thể thiết lập 1 lệnh để chạy trên 1 monitored endpoint. Wazuh sẽ cảnh báo nếu output của lệnh có gì thay đổi. Tùy chọn này, đặt ```type``` là ```ssh_generic_diff```. Trong ví dụ dưới đây, lệnh ```ls -la /etc``` được thực thi mỗi 20000s. 1 cảnh báo được tạo nếu output của lệnh có gì thay đổi

```sh
<agentless>
  <type>ssh_generic_diff</type>
  <frequency>20000</frequency>
  <host>user@test.com</host>
  <state>periodic_diff</state>
  <arguments>ls -la /etc</arguments>
</agentless>
```

**Lưu ý: để sử dụng ```su``` trong lệnh, ta phải thêm cú pháp ```use_su``` trước hostname, ví dụ thế này: ```<host>use_su user@test.com</host>```**

### Kiểm tra agentless monitoring setup

Sau khi cấu hình agentless monitoring trên Wazuh server, restart Wazuh manager với lệnh sau để áp dụng thay cấu hình

```sh
systemctl restart wazuh-manager
```

Khi package ```expect``` được cài đặt và Wazuh restart, ta có thể thấy 1 message tương tự như sau trong file ```/var/ossec/logs/ossec.log```

```sh
wazuh-agentlessd: INFO: Test passed for 'ssh_integrity_check_linux'.
```

Khi Wazuh kết nối được với endpoint, ta có thể thấy log như sau trong log file trên

```sh
wazuh-agentlessd: INFO: ssh_integrity_check_linux: user@example_adress.com: Starting.
wazuh-agentlessd: INFO: ssh_integrity_check_linux: user@example_adress.com: Finished.
```