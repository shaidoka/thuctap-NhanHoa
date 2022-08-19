# Add Reseller và User cho DirectAdmin

## Add Reseller

1. Trước khi tạo reseller, ta phải tạo package trước

Chọn ```Manage Reseller Packages``` -> ```Add Package```

![](./images/manager_reseller_package.png)

2. Thiết lập thông số cho Package
- **Bandwidth**: Băng thông cấp phát cho User
- **Disk space**: Dung lượng ổ cứng cấp phát cho User
- **Inodes**: Số file tối đa được phép tạo
- **Domains**: Số lượng tên miền website được tạo trên User
- **Email Accounts**: Số lượng email mà User có thể tạo

![](./images/reseller_package_setting.png)

Sau khi thiết lập xong thông số, thay đổi tên Package và chọn ```Save``` để tạo Package

*Lưu ý: Ta hoàn toàn có thể thay đổi thông số Package với menu Manage Reseller Package*

3. Tạo Reseller

Chọn ```Create Reseller``` từ màn hình menu chính

![](./images/create_reseller.png)

Thiết lập thông tin Reseller

![](./images/reseller_setting.png)

## Add User

1. Tạo Package cho User

Đăng nhập vào tài khoản Reseller, chọn ```Add Package```

![](./images/add_user_package.png)

2. Thiết lập thông số cho Package

![](./images/user_setting.png)

Ý nghĩa của các thông số giống như Reseller Package

3. Tạo User

Tại menu chính, chọn ```Add new user```

![](./images/add_new_user.png)

Nhập thông tin User

![](./images/user_setting_official.png)

