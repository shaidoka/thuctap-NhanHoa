# Cài đặt webserver IIS trên Windows Server 2019

## Cài đặt IIS

1. Ở giao diện quản lý của windows server, chọn ```add roles and features```

![](./images/add_roles_n_features.png)

2. Tick chọn ```Web Server (IIS)```

![](./images/tick_iis.png)

3. Next và Install, sau đó chờ quá trình cài đặt hoàn tất

![](./images/installing.png)

4. Ở đường dẫn ```C:\inetpub\wwwroot\```, tạo 1 file html để kiểm tra hoạt động của IIS

![](./images/index_html_web1.png)

5. Truy cập trang web bằng địa chỉ IP hoặc bằng tên miền của server

![](./images/web1.png)

## Tạo thêm web trong IIS

1. Ở giao diện quản lý của windows server, chọn ```IIS```, chuột phải vào server và chọn ```Internet Information Service (IIS) Manager``` để vào trình quản lý IIS

![](./images/iis_manager.png)

2. Click chuột trái chọn máy tính muốn add thêm website, sau đó chuột phải vào và chọn ```Add Website...```

![](./images/add_website.png)

3. Cấu hình thông tin website mới

![](./images/config_web2.png)

4. Tạo 1 file html ở đường dẫn của website mới để kiểm tra hoạt động

![](./images/index_html_web2.png)

5. Truy cập trang web mới tạo bằng tên miền đã cấu hình 

![](./images/web2.png)