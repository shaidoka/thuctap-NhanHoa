# Triển khai HAProxy Pacemaker cho Cluster Galera 3 node trên CentOS 7

## Chuẩn bị

Server có cấu hình và IP như sau:

|Hostname|Hardware|Interface|
|:-|:-|:-|
|node1|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.153 - private: 192.168.60.153|
|node2|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.154 - private: 192.168.60.154|
|node3|2 vCPU - 2 GB RAM - 100 GB Disk|public: 172.16.6.155 - private: 192.168.60.155|

Mô hình

