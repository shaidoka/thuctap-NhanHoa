# Cài đặt và sử dụng Hyper-V trên hệ điều hành Windows Server 2019

### Cài đặt

- Chọn ```Add roles and features```

![](./images/hyper_step_1.png)

- Chọn ```Role-based or feature-based installation``` -> ```Next```

![](./images/hyper_step_2.png)

- Chọn host muốn thêm service vào

![](./images/hyper_step_3.png)

- Tick chọn ```Hyper-V``` -> ```Add feature``` -> ```Next```

![](./images/hyper_step_4.png)

- ```Next```

![](./images/hyper_step_5.png)

- ```Next```

![](./images/hyper_step_6.png)

- Tại phần Virtual Switches, chọn 1 card mạng -> ```Next```

![](./images/hyper_step_7.png)

- ```Next```

![](./images/hyper_step_8.png)

- Chọn vị trí cài đặt máy ảo -> ```Next```

![](./images/hyper_step_9.png)

- Nhấn ```Install``` để bắt đầu cài đặt

![](./images/hyper_step_10.png)

- Sau khi cài đặt xong thì reboot lại sv để hoàn tất

### Tạo máy ảo

- ```Tools``` -> ```Hyper-V Manager```

![](./images/hyper_step_11.png)

- Chuột phải vào Hostname muốn cài máy ảo -> ```New``` -> ```Virtual Machine```

![](./images/hyper_step_12.png)

- ```Next```

![](./images/hyper_step_13.png)

- Đặt tên cho máy ảo -> ```Next```

![](./images/hyper_step_14.png)

- Chọn ```Generation 2```

![](./images/hyper_step_15.png)

- Cấu hình ổ đĩa ảo cho VM

![](./images/hyper_step_16.png)

- Cài đặt hđh cho máy ảo, hoặc để sau

![](./images/hyper_step_17.png)

- ```Finish```

![](./images/hyper_step_18.png)

- Khi mới tạo, máy sẽ ở trạng thái Off, chuột phải vào và chọn ```Start``` để khởi động máy ảo

![](./images/hyper_step_19.png)

- Để truy cập bảng điều khiển, chuột phải vào và chọn ```Connect```

![](./images/hyper_step_20.png)

- Cài CentOS 7 lên máy ảo

![](./images/hyper_step_21.png)