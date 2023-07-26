# How to configure active response

Những bước sau đây mô tả cách để cấu hình active response module để thực hiện 1 hành động trên endpoint được giám sát

## Cấu hình Wazuh server

1. Kiểm tra cấu hình của khối ```<command>``` trên file ```/var/ossec/etc/ossec.conf``` của Wazuh server. Thêm vào nếu nó chưa tồn tại.

Khối ```<command>``` thiết lập script để chạy cho 1 response khi trigger. Khi sử dụng "out-of-the-box" active response scripts, khối ```<command>``` được sử dụng cho chúng ở trên Wazuh server theo mặc định, và không cần thiết phải add thêm. Nhưng khi sử dụng **custom active response scripts**, ta sẽ cần đưa chúng vào thẻ ```<ossec_config>```, kiểu như này:

```sh
<command>
  <name>host-deny</name>
  <executable>host-deny</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>
```

Trong đó:
- ```<name>```: Tên của command. Trong trường hợp này là ```host-deny```
- ```<executable>```: Chỉ định active response script để chạy khi nó kích hoạt. Ta không cần chỉ định phần mở rộng tên file trừ khi ta có nhiều script trùng tên. Trong trường hợp này là tệp thực thi ```host-deny```
- ```<timeout_allowed>```: Cho phép timeout sau 1 khoảng thời gian. Thiết lập giá trị này thành ```yes``` giúp đảo ngược hành động sau khoảng thời gian chỉ định

Chi tiết về các tùy chọn của khối ```<command>``` ở [đây](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/commands.html)


2. Thêm 1 khối ```<active-response>``` trong thẻ ```<ossec_config>``` ở file ```/var/ossec/etc/ossec.conf``` trên Wazuh server. Khối này chỉ định khi nào và nơi 1 command được thực thi. Ví dụ, khi 1 cảnh báo khớp với bộ lọc, ví dụ như 1 rule ID, alert level, hay rule group được chỉ định. Cấu hình này cũng chỉ định command sẽ được thực thi trên endpoint, Wazuh server, hay bất kỳ đâu. Ví dụ:

```sh
<active-response>
  <command>host-deny</command>
  <location>local</location>
  <level>7</level>
  <timeout>600</timeout>
</active-response>
```

Trong đó:
- ```<command>```: Chỉ định command để cấu hình. Đây là command name mà ta dùng ở trên
- ```<location>```: Chỉ định nơi mà command phải thực thi. Các giá trị khả dụng là:
   - ```local```: thực thi trên endpoint mà tạo ra alert
   - ```server```: chạy trên Wazuh server
   - ```all```: tất cả wazuh agent
   - ```definded-agent```: thực thi agent được chỉ định. Đi kèm thẻ ```<agent_id>```, ví dụ:

```sh
<ossec_config>
  <active-response>
    <disabled>no</disabled>
    <command>host-deny</command>
    <location>defined-agent</location>
    <agent_id>001</agent_id>
    <level>10</level>
    <timeout>180</timeout>
  </active-response>
</ossec_config>
```

3. Restart Wazuh manager để áp dụng các thay đổi

```sh
systemctl restart wazuh-manager
```

## Thiết lập endpoint được giám sát

### Sử dụng "out-of-the-box" active response scripts

Không cần thiết lập thêm gì cả. Thông tin về các script mặc định này được đề cập ở [Default active response scripts](https://documentation.wazuh.com/current/user-manual/capabilities/active-response/default-active-response-scripts.html)

### Sử dụng custom active response scripts

**Linux/Unix**
- Thêm custom active response script hoặc executable vào đường dẫn ```/var/ossec/active-response/bin``` trên Linux/Unix endpoint
- Thêm quyền thực thi cho group và ownership, ví dụ

```sh
sudo chmod 750 /var/ossec/active-response/bin/<CUSTOM_SCRIPT>
sudo chown root:wazuh /var/ossec/active-response/bin/<CUSTOM_SCRIPT>
```

**macOS**
- Thêm custom active response script hoặc executable vào đường dẫn ```/Library/Ossec/active-response/bin``` trên macOS endpoint
- Thêm quyền thực thi cho group và đổi ownership như bên trên

**Windows**
- Thêm custom active response script hoặc executable vào đường dẫn ```C:\Program Files (x86)\ossec-agent\active-response\bin``` trên Windows endpoint