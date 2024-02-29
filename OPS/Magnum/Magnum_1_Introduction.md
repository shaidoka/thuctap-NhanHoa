# Magnum

Magnum là 1 dự án Openstack mà cung cấp container orchestration engines cho vệc triển khai và quản lý containers như 1 first class resources trong OpenStack. Magnum sử dụng Heat để điều phối 1 OS image mà chứa Docker và K8s và chạy image đó trong VM hoặc bare metal.

- **Free software**: Apache là đơn vị nắm giữ bản quyền
- **Source**: https://opendev.org/openstack/magnum
- **Blueprints**: https://blueprints.launchpad.net/magnum
- **Bugs**: https://bugs.launchpad.net/magnum
- **REST Client**: https://opendev.org/openstack/python-magnumclient

## Architecture

Có nhiều loại objects khác nhau trong hệ thống của magnum:

- **Cluster:** 1 tập hợp của những node nơi mà workload được lập lịch tới
- **ClusterTemplate:** 1 object lưu trữ thông tin template về cluster, thứ sẽ giúp tạo những cluster mới

2 binaries cùng hoạt động để tạo nên magnum system. Binary đầu tiên (được truy cập bởi python-magnumclient) là magnum-api REST server. REST server sẽ chạy như 1 process hoặc nhiều processes. Khi 1 REST request được gửi đến client API, request này được gửi thông qua AMQP đến magnum-conductor process. REST server là 1 đối tượng có thể horizontally scalable. Ở thời điểm hiện tại, conductor bị giới hạn ở 1 process, nhưng điều này có thể thay đổi trong tương lai.

## Feature

- Abstractions for Cluster
- Integration with K8s for backend container technology
- Integration with Keystone for multi-tenant security
- Integration with Neutron for K8s multi-tenancy network security
- Integration with Cinder to provide volume service for containers

## Container Infrastructure Management service overview

Container Infrestructure Management service chứa các thành phần sau đây:

- ```magnum``` (**command-line client**): 1 CLI mà giao tiếp với magnum-api để tạo và quản lý các cụm container. End developers có thể trực tiếp sử dụng magnum REST API
- ```magnum-api``` (**service**): 1 OpenStack-native API mà xử lý API requests bằng cách gửi chúng đến ```magnum-conductor``` thông qua AMQP
- ```magnum-conductor``` (**service**): Chạy trên 1 controller machine và kết nối đến heat để điều phối 1 cluster. Thêm vào đó, nó kết nối đến 1 K8s API endpoint.