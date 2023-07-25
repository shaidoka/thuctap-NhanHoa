# Network IDS integration

Wazuh tích hợp với 1 Network-based intrusion detection system (NIDS) để nâng cao khả năng phát hiện mối đe dọa bằng cách giám sát network traffic

Trong trường hợp này, chúng ta sẽ giới thiệu cách để sử dụng Suricata với Wazuh. Suricata có thể cung cấp thêm thông tin về bảo mật trong hệ thống mạng với tính năng phân tích network traffic của nó

Bài này sẽ sử dụng endpoint là Ubuntu 22.04

## Configuration

Thực hiện các bước sau để cấu hình Suricata trên Ubuntu endpoint và gửi log được khởi tạo đến Wazuh server.

1. Cài đặt Suricata trên Ubuntu endpoint:

```sh
add-apt-repository ppa:oisf/suricata-stable
apt-get update -y
apt-get install suricata -y
```

2. Tải và giải nén Emerging Threats Suricata ruleset

```sh
cd /tmp/ && curl -LO https://rules.emergingthreats.net/open/suricata-6.0.8/emerging.rules.tar.gz
tar -xvzf emerging.rules.tar.gz
mkdir -p /etc/suricata/rules/
mv rules/*.rules /etc/suricata/rules/
chmod 640 /etc/suricata/rules/*.rules
```

3. Chỉnh sửa Suricata settings trong file ```/etc/suricata/suricata.yaml``` với những tham số sau:

```sh
HOME_NET: "<UBUNTU_IP>"
EXTERNAL_NET: "any"

default-rule-path: /etc/suricata/rules
rule-files:
- "*.rules"

# Global stats configuration
stats:
  enabled: no

# Linux high speed capture support
af-packet:
  - interface: eth0
```

4. Restart Suricata service

```sh
systemctl restart suricata
```

5. Thêm cấu hình sau đây vào ```/var/ossec/etc/ossec.cof``` của Wazuh agent. Điều này cho phép Wazuh agent đọc Suricata logs file:

```sh
<ossec_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/suricata/eve.json</location>
  </localfile>
</ossec_config>
```

## Giả định attack

Wazuh tự động thu thập dữ liệu từ ```/var/log/suricata/eve.json``` và khởi tạo cảnh báo liên quan trên Wazuh dashboard

Ta chỉ cần thử ping đến agent thôi là được:

```sh
ping -c 20 "<UBUNTU_IP>"
```

## Visualize

