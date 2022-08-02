# Tìm hiểu cơ bản về GIT

### 1. Giới thiệu chung

GIT là một hệ thống quản lý mã nguồn phân tán. Nó cung cấp cho lập trình viên kho lưu trữ (Repository) nơi chứa cơ sở dữ liệu tất cả những thông tin cần thiết để duy trì và quản lý các sửa đổi hay lịch sử dự án.

### 2. Một số thuật ngữ trong Git

**Repository**
Kho lưu trữ (Repo) là nơi tập hợp các mã nguồn. Repo chứa các commit của dự án hoặc một tập hợp các tham chiếu các commit.

**Commit**
Một commit ghi lại một loạt các thay đổi bạn đã thực hiện đối với một file trong repo.

**Branch**
Branch là các nhánh, tương ứng với mỗi phiên bản cụ thể trong repo. Mỗi repo có thể có một hoặc nhiều branch, branch chính được gọi là branch master.

**Fork**
Fork là bản sao của Repo. Lập trình viên có thể tận dụng fork để chạy thử nghiệm các thay đổi mà không làm ảnh hưởng đến dự án.

**Head**
Head đại diện cho commit mới nhất của repository mà bạn đang làm việc

**Merge**
Thêm các thay đổi từ nhánh này sang nhánh khác

**Pull**
Pull request thể hiện các đề xuất thay đổi trong nhánh chính

**Push**
Dùng để cập nhật các nhánh từ xa với những thay đổi mới nhất mà bạn mới commit

### 3. Một số lệnh Git cơ bản

**Git config**
Dùng để kiểm tra hoặc thay đổi username và email

```sh
$ git config --global user.email "email"
$ git config --global user.name "username"
```

**Git init**
Dùng để tạo 1 repo hay 1 project mới

```sh
git init
```

**Git add**
Dùng để thêm các file vào stage/index

```sh
# Thêm toàn bộ file
$ git add .
# Thêm 1 file được chỉ định
$ git add index.html
# Thêm 1 thư mục
$ git add css
```

**Git commit**
Dùng để ghi lại những thay đổi vào local repository.

```sh
$ git commit -m "Commit message in quotes"
```

**Git status**
Sử dụng lệnh này để trả về trạng thái tại Repo

```sh
$ git status 
```

**Git branch**
Để xác định nhánh nào trong local repository, thêm hoặc xóa một nhánh mới

```sh
# Tạo 1 branch
$ git branch <branch_name>
# Liệt kê tất cả remote và branch
$ git branch -a
# Xóa 1 branch
$ git branch -d <branch_name>
```

**Git merge**
Kết hợp các thay đổi từ nhánh này sang nhánh khác

```sh
# Kết hợp các thay đổi đến nhánh hiện tại
$ git merge <branch_name>
```

**Git pull**
Tải phiên bản mới nhất của repository sang máy tính cục bộ

```sh
$ git pull <branch_name> <remote_URL/remote_name>
```

**Git push**
Gửi commit đến kho lưu trữ từ xa

```sh
git push <remote_URL/remote_name> <branch>
```
