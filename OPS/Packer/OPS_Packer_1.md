# Build Image with Openstack Packer

Đối với vai trò nhà cung cấp dịch vụ đám mây, việc cung cấp các dịch vụ như Cloud Server nhanh chóng đòi hỏi quá trình triển khai nhanh chóng.

Quá trình build image cho Cloud Server cũng vậy. Cần tự động hóa, nâng cao bảo mật và đảm bảo sự đồng nhất trong đội ngũ quản trị.

Xây dựng images cho Cloud cũng đặt ra nhiều phương pháp:

  - Xây dựng thủ công sử dụng công cụ như virt-manager hoặc virt-install.
  - Tự động hóa bằng cách sử dụng các công cụ như Packer, Terraform, Ansible, disk-image-builder.

Packer là một công cụ phổ biến, hỗ trợ nhiều nền tảng, và nhận được sự hỗ trợ và cập nhật đầy đủ từ cộng đồng lớn.

## Install KVM/QEMU

Server dùng để cài đặt Packer cần có KVM để build image, ta có thể cài đặt nó ở **Ubuntu** với lệnh sau đây:

```sh
# Update packages
sudo apt update
 
# Install
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virt-manager
 
# Startup
sudo systemctl enable --now libvirtd
 
# Add user current to group
sudo adduser `id -un` libvirt
sudo adduser `id -un` libvirt-qemu
```

