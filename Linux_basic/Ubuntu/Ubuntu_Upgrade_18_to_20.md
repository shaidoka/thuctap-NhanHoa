# Nâng cấp Ubuntu 18.04 lên 20.04 LTS

LTS hay Long Term Support, 1 bản LTS mới được ra mắt mỗi 2 năm và hỗ trợ cập nhật các gói phần mềm cũng như bản vá trong vòng 5 năm sau đó. Trong bài này sẽ hướng dẫn cách upgrade từ Ubuntu 18.04 LTS Bionic lên Ubuntu 22.04 Focal Fossa.

## I. Tóm tắt các bước cần thực hiện

Trước khi thực hiện Upgrade phiên bản, hãy chắc chắn là đã thực hiện các công việc sau:

1. Backup toàn bộ dữ liệu cần thiết

2. Nâng cấp tất cả gói phần mềm đã cài đặt

```sh
sudo apt update -y && sudo apt upgrade -y
```

3. Khởi động lại server

```sh
sudo reboot
```

4. Cài đặt bộ công cụ cập nhật của Ubuntu

```sh
sudo apt install update-manager-core
```

5. Khởi chạy quá trình upgrade

```sh
sudo do-release-upgrade
```

6. Khởi động lại hệ thống 1 lần nữa

```sh
sudo reboot
```

7. Kiểm tra tính toàn vẹn của dữ liệu và dịch vụ

## II. Chi tiết

Hãy đi vào chi tiết các bước cần thực hiện

### 1. Backup toàn bộ dữ liệu

Đây chắc chắn là bước quan trọng nhất, không chỉ khi upgrade server mà bất kể khi nào thì 1 bản backup cũng đem lại sự an tâm hơn rất nhiều.

Và cũng đừng quên copy những dữ liệu đó sang một hệ thống khác hoặc máy tính local, đề phòng khi server chết thì lại đặt ra câu hỏi "Where's the backup"

### 2. Upgrade toàn bộ gói phần mềm đã cài đặt 

Sử dụng các lệnh sau

```sh
sudo apt update -y
sudo apt list --upgradable
sudo apt upgrade
```