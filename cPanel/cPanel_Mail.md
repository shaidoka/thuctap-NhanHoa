# Tạo và đăng nhập email trên cPanel

- Đăng nhập vào trang quản trị cPanel và chọn ```Email Accounts``` để vào giao diện tạo tài khoản 

- Ở mục **EMAIL**, chọn ```Email Accounts``` để vào giao diện tạo tài khoản

![](./images/cp_76.png)

- Nhập thông tin tài khoản mật khẩu

![](./images/cp_77.png)

- Nhập dung lượng cho phép trên tài khoản, mặc định là 1 GB. Cuối cùng nhấn ```Create``` để tạo tài khoản

![](./images/cp_78.png)

- Nhấn ```Check Email``` để vào webmail client

![](./images/cp_79.png)

- ```Open```

![](./images/cp_80.png)

![](./images/cp_81.png)

- Hoặc đăng nhập bằng đường dẫn ```webmail.baotrung.xyz:2096```

![](./images/cp_82.png)

### Lấy bản ghi DKIM và SPF trên cPanel

- Tại giao diện quản trị cPanel của account, tìm đến ```EMAILS``` -> ```Email Deliverability```

![](./images/cp_85.png)

- ```Manage```

![](./images/cp_86.png)

- Tạo bản ghi DKIM trên nameserver như sau (**lưu ý là xóa dấu ";" ở cuối đi**)

![](./images/cp_87.png)

- Tương tự với SPF

![](./images/cp_88.png)

- Gửi thử email

![](./images/cp_89.png)