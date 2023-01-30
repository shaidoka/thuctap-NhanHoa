# Cài đặt MacOS trên nền tảng ảo hóa KVM

Trong bài viết này sẽ hướng dẫn từng bước tạo 1 hệ thống Hackintosh ảo

Yêu cầu:
- 1 bản phân phối Linux mới như Ubuntu 22.04 LTS
- QEMU >= 6.2.0
- 1 CPU với Intel VT-x hoặc AMD hỗ trợ SVM (check bằng lệnh ```grep -e vmx -e svm /proc/cpuinfo```)
- 1 CPU hỗ trợ SSE4.1 cho macOS Sierra hoặc AVX2 cho macOS Mojave

## Chuẩn bị cài đặt

- Cài đặt QEMU và các package khác

```sh
sudo apt-get install qemu uml-utilities virt-manager git wget libguestfs-tools p7zip-full make dmg2img -y
```

*Lưu ý các gói/lệnh cài đặt sẽ tùy thuộc vào bản phân phối bạn đang sử dụng*

- Thêm người dùng hiện tại vào group ```kvm``` và ```libvirt```

```sh
sudo usermod -aG kvm $(whoami)
sudo usermod -aG libvirt $(whoami)
sudo usermod -aG input $(whoami)
```

