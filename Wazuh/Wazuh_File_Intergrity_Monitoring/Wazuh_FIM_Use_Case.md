# FIM module use case

Trong bài này sẽ mô tả 1 vài trường hợp sử dụng của FIM module (cho mục đích tham khảo, và cũng là tóm tắt các bài trước)

## 1. Phát hiện malware ở folder startup

Attacker bằng 1 cách nào đó, có thể thêm các script nguy hiểm hoặc chương trình nào đó vào startup folder trên Windows. Những chương trình này sau đó sẽ được thực thi khi 1 người dùng đăng nhập vào hệ thống. 

Bằng cách giám sát Windows startup folder, ta có thể phát hiện sự kiện đáng ngờ xảy ra ngay lập tức. Nhờ đó đưa ra các phương án khắc phục hợp lí

```sh
<syscheck>
  <directories realtime="yes">%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup</directories>
</syscheck>
```

## 2. Phát hiện thay đổi SSH key

Việc quản lý tài khoản bao gồm tạo, thay đổi, hoặc xóa tài khoản người dùng. Giám sát hoạt động này rất quan trọng trong bảo mật của doanh nghiệp. 

Để duy trì truy nhập ngay cả khi người dùng thay đổi mật khẩu, kẻ tấn công có thể thay đổi SSH key lưu ở ```authorized_keys``` file trong Linux. File này chứa public key mà người dùng sử dụng để đăng nhập vào tài khoản của họ.

Ta có thể thiết lập giám sát file này, trigger 1 alert khi nó bị thay đổi để giám sát credential của user, trong khi giám sát file ```/etc/passwd``` cho phép ta biết được khi các sự kiện thêm/ xóa người dùng được thực hiện.

```sh
<syscheck>
  <directories whodata="yes">/home/*/.ssh/authorized_keys</directories>
</syscheck>
```

## 3. Giám sát file với interval chỉ định

Trong các tiêu chuẩn về bảo mật dữ liệu như PCI DSS, ta cần phải giám sát truy nhập và phát hiện thay đổi đến các file quan trọng, file cấu hình, và file nội dung.

Điều này là quan trọng để bảo mật các dữ liệu nhạy cảm của tổ chức và phát hiện khi có vi phạm về bảo mật.

Ta có thể chạy schedule scans với FIM module để phát hiện thay đổi này. Ví dụ:

```sh
<syscheck>
  <frequency>300</frequency>
  <directories>/Users/*/user_details.txt</directories>
</syscheck>
```

## 4. Báo cáo nội dung thay đổi

Wazuh hoàn toàn có thể phát hiện nội dung được thay đổi trong báo cáo của mình, để thực hiện điều này, ta có thể thêm thuộc tính như sau:

```sh
<syscheck>
  <directories realtime="yes" report_changes="yes">/appfolder</directories>
  <nodiff>/appfolder/private-file.conf</nodiff>
</syscheck>
```

Trong đó file ```private-file.conf``` là ngoại lệ và sẽ không được báo cáo về nội dung mà bị thay đổi.

## 5. Báo cáo thay đổi cấu hình

Ta có thể cấu hình để FIM module giám sát những file cấu hình và báo cáo nếu có bất kỳ điều gì thay đổi, Wazuh FIM module sử dụng ```whodata``` và ```report_changes``` để ghi lại thông tin về:
- Ai login và tạo ra thay đổi
- Thời điểm thay đổi
- Tiến trình mà người dùng sử dụng để thay đổi
- Nội dung thay đổi

```sh
<syscheck>
  <directories check_all="yes" report_changes="yes" whodata="yes">/etc/app.conf</directories>
</syscheck>
```

## 6. Giám sát Windows Registry

Windows Registry là 1 thành phần quan trọng trong Windows OS. Nó là 1 database mà lưu trữ thông tin cấu hình cho chương trình và phần cứng cài đặt trên Windows. Khi ta cài đặt 1 chương trình, Windows tạo 1 subkey mới trong registry. Subkey chứa thông tin như vị trí của chương trình, phiên bản, và các chỉ dẫn khởi động.

Wazuh có thể giám sát và gửi về báo cáo về registry y hệt các file khác, bằng cách cấu hình như sau:

```sh
<syscheck>
  <windows_registry>HKEY_LOCAL_MACHINE\Software\Classes\batfile\TestKey1</windows_registry>
  <windows_registry check_sum="no">HKEY_LOCAL_MACHINE\Software\Classes\batfile\TestKey2</windows_registry>
  <windows_registry check_mtime="no">HKEY_LOCAL_MACHINE\Software\Classes\batfile\TestKey3</windows_registry>
</syscheck>
```