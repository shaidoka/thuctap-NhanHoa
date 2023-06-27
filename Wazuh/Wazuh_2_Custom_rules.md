# Custom rules and decoders

## Thêm mới decoders và rules

*Lưu ý: Sử dụng ID nằm trong khoảng 100000 và 120000 cho custom rules*

Hãy theo dõi ví dụ dưới đây để biết cách tạo mới decoders và rules. Ví dụ ta có 1 đoạn log như sau:

```sh
Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100'
```

1. Thêm 1 decoder mới vào ```/var/ossec/etc/decoders/local_decoder.xml``` để decode thông tin log:

```sh
<decoder name="example">
  <program_name>^example</program_name>
</decoder>

<decoder name="example">
  <parent>example</parent>
  <regex>User '(\w+)' logged from '(\d+.\d+.\d+.\d+)'</regex>
  <order>user, srcip</order>
</decoder>
```

2. Thêm rule sau vào ```/var/ossec/etc/rules/local_rules.xml```

```sh
<group name="custom_rules_example,">
  <rule id="100010" level="0">
    <program_name>example</program_name>
    <description>User logged</description>
  </rule>
</group>
```

3. Chạy lệnh ```/var/ossec/bin/wazuh-logtest``` để kiểm tra decoder và rule:

```sh
Type one log per line

Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100'

**Phase 1: Completed pre-decoding.
        full event: 'Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100''
        timestamp: 'Dec 25 20:45:02'
        hostname: 'MyHost'
        program_name: 'example'

**Phase 2: Completed decoding.
        name: 'example'
        dstuser: 'admin'
        srcip: '192.168.1.100'

**Phase 3: Completed filtering (rules).
        id: '100010'
        level: '0'
        description: 'User logged'
        groups: '['custom_rules_example']'
        firedtimes: '1'
        mail: 'False'
```