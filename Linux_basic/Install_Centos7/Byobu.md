# Hướng dẫn sử dụng Byobu

#### 1. Byobu là gì?

Byobu là 1 trình hỗ trợ terminal. Nó mang đến nhiều chức năng hữu ích như chia đôi màn hình, mở tab nhanh,...

#### 2. Tác dụng của Byobu

Khi bạn cần phải SSH vào nhiều server, cần tạo nhiều session trên server đó. Tuy nhiên, khi đang dở việc mà phải tắt máy hay sập điện, các phiên SSH bị tắt đi coi như đứt

Byobu có thể giúp ta khắc phục nhược điểm đó. Ta có thể truy cập đến server mà không phải SSH nhiều lần. Khi công việc vẫn đang thực hiện mà phải tắt máy thì Byobu vẫn chạy. Khi mở lại thì công việc vẫn được tiếp tục

#### 3. Cài đặt

**Trên Ubuntu**

```sh
apt-get install -y byobu
```

**Trên CentOS**

```sh
yum install -y byobu
```

#### 4. Sử dụng Byobu

Để vào giao diện byobu, ta gõ trên terminal: byobu

Ta thấy có 1 dòng dưới cùng có các thông tin về các tab đang mở, ngày giờ, CPU, RAM,...

Để biết cách sử dụng, ta bấm phím F1 rồi chọn ```Help```

Ta sẽ thấy các phím tắt cùng chức năng của nó 

Một vài chức năng đáng chú ý:

- **Mở thêm tab mới:** để mở tab mới, ta nhấn phím **F2**
- **Chuyển qua lại giữa các tab:** dùng phím **F3**/**F4** hoặc tổ hợp **Alt + mũi tên trái/phải**
- **Chia đôi màn hình:** nhấn tổ hợp **Ctrl F2**, để đổi qua lại giữa các màn hình nhấm **Shift + mũi tên trái/phải**
- **Đóng 1 cửa sổ hay tab:** gõ lệnh ```exit```
- **Di chuyển xem log:** nếu đang tail 1 đoạn log và muốn di chuyển lên để xem, thay vì dùng chuột thì có thể nhấn **F7** và dùng các phím mũi tên, phim **Page Up**/**Page Down** để xem
- **Đổi tên tab:** nhấn phím **F8** rồi đặt tên cho tab

