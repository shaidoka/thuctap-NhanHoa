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

4. Restart Wazuh service

```sh
systemctl restart wazuh-manager
```

## Thay đổi rule đã có sẵn

**Warning:** Thay đổi bất kỳ rule nào trong đường dẫn ```/var/ossec/ruleset/rules``` sẽ mất khi thực hiện update. Do đó hãy làm theo các bước được đề cập dưới đây

Ta có thể thay đổi các rule Wazuh mặc định. Để làm điều đó, wazuh khuyến khích copy chúng đến đường dẫn ```/var/ossec/etc/rules/```, thực hiện thay đổi, và thêm thẻ ```overwrite="yes"``` vào rule được thay đổi.

Ví dụ:

1. Mở rule file ```/var/ossec/ruleset/rules/0095-sshd_rules.xml```

2. Tìm và sao chép rule id ```5710```

```sh
<group name="syslog,sshd,">
  <rule id="5710" level="5">
    <if_sid>5700</if_sid>
    <match>illegal user|invalid user</match>
    <description>sshd: Attempt to login using a non-existent user</description>
    <mitre>
      <id>T1110</id>
    </mitre>
    <group>invalid_login,authentication_failed,pci_dss_10.2.4,pci_dss_10.2.5,pci_dss_10.6.1,gpg13_7.1,gdpr_IV_35.7.d,gdpr_IV_32.2,hipaa_164.312.b,nist_800_53_AU.14,nist_800_53_AC.7,nist_800_53_AU.6,tsc_CC6.1,tsc_CC6.8,tsc_CC7.2,tsc_CC7.3,</group>
  </rule>
</group>
```

3. Paste rule đã copy vào ```/var/ossec/etc/rules/local_rules.xml```. Thay đổi giá trị ```level```, và thêm thẻ ```overwrite="yes"```

```sh
<group name="syslog,sshd,">
  <rule id="5710" level="10" overwrite="yes">
    <if_sid>5700</if_sid>
    <match>illegal user|invalid user</match>
    <description>sshd: Attempt to login using a non-existent user</description>
    <mitre>
      <id>T1110</id>
    </mitre>
    <group>invalid_login,authentication_failed,pci_dss_10.2.4,pci_dss_10.2.5,pci_dss_10.6.1,gpg13_7.1,gdpr_IV_35.7.d,gdpr_IV_32.2,hipaa_164.312.b,nist_800_53_AU.14,nist_800_53_AC.7,nist_800_53_AU.6,tsc_CC6.1,tsc_CC6.8,tsc_CC7.2,tsc_CC7.3,</group>
  </rule>
</group>
```

Restart service

```sh
systemctl restart wazuh-manager
```

## Thay đổi decoder có sẵn

Vấn đề xảy ra với decoder tương tự như với rule mà đã được đề cập ở bên trên. Do đó để thay đổi 1 decoder thì ta thực hiện theo bước như ví dụ sau:

1. Sao chép file decoder ```/var/ossec/ruleset/decoders/0310-ssh_decoders.xml``` vào folder ```/var/ossec/etc/decoders```. 

2. Thực hiện chỉnh sửa file cấu hình ```/var/ossec/etc/ossec.conf```, thiết lập ```<decoder_exclude>``` loại trừ decoder file cũ ```ruleset/decoders/0310-ssh_decoders.xml```. Bằng cách này, Wazuh sẽ sử dụng cấu hình decoder lưu tại user folder chứ không phải default folder

```sh
<ruleset>
  <!-- Default ruleset -->
  <decoder_dir>ruleset/decoders</decoder_dir>
  <rule_dir>ruleset/rules</rule_dir>
  <rule_exclude>0215-policy_rules.xml</rule_exclude>
  <list>etc/lists/audit-keys</list>

  <!-- User-defined ruleset -->
  <decoder_dir>etc/decoders</decoder_dir>
  <rule_dir>etc/rules</rule_dir>
  <decoder_exclude>ruleset/decoders/0310-ssh_decoders.xml</decoder_exclude>
</ruleset>
```

3. Thực hiện chỉnh sửa decoder ```/var/ossec/etc/decoders/0310-ssh_decoders.xml```

4. Restart Wazuh manager

```sh
systemctl restart wazuh-manager
```

