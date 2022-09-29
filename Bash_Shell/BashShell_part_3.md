# Tìm hiểu cơ bản về Bash Shell part 3

### 1. Các ký tự đặc biệt kiểm soát tiến trình trong Shell

#### a. "&" (Ampersand)

Dấu "&" đặt một tiến trình vào chế độ chạy nền (background process). Bản thân Unix không có khái niệm về tiến trình này là chạy nền (background) hay là tiến trình tương tác (foreground), mà việc này sẽ do Shell điều khiển. Với "&", tiến trình sẽ tự chạy và shell sẽ quay về tương tác ngay với người dùng

Ví dụ: thực hiện sort 1 file đã có sẵn và thực hiện câu lệnh với "&" để câu lệnh được chạy nền

```sh
sort test2.sh > test1 &
```

Câu lệnh sẽ in ra ID của tiến trình đang chạy ngầm. Trên thực tế, "&" được dùng để thực hiện chạy các script dưới dạng các tiến trình ngầm. Ví dụ:

```sh
sh test1.sh &
sh test2.sh &
```

Show tất cả các job đang chạy ngầm ```jobs```

Để quay lại chế độ tương tác của tiến trình 1, sử dụng: ```fg 1```

#### b. "|" (Pipe)

Shell cho phép sử dụng đầu ra của lệnh, và kết nối trực tiếp tới đầu vào của 1 lệnh khác mà không cần xử lý trung gian

VD ta có file ```hello.sh``` với nội dung sau:

```sh
#!/bin/bash
echo "Hello World\n"
adding_string_to_number="s"
v=$(expr 5 + $adding_string_to_number)
```

Thực hiện việc grep ra dòng "Hello World có trong file ```hello.sh```

```sh
cat hello.sh | grep "Hello World"
```

Kết quả nhận được:

![](./images/bash_7.png)

#### c. "\" (Backslash)

Dấu \ được dùng để giải trừ ý nghĩa đặc biệt của các dấu như "&", "?" hoặc "$"

VD: ta có 1 file ```file1&2```. Khi thực hiện đọc file này với cú pháp như sau

```sh
cat file1&2
```

Việc đọc sẽ xảy ra lỗi vì tiêu đề của file chứa ký tự đặc biệt "&". Để đọc được file như ý muốn, ta cần thực hiện như sau

```sh
cat file1\&2
```

### 2. Các biến trong Shell

#### a. Biến môi trường (environment variable)

Khi Shell khởi động, nó cung cấp 1 số biến được khai báo và có giá trị mặc định. Chúng được gọi là các biến môi trường. Các biến này thường được viết hoa để phân biệt với các biến do người dùng đặt ra (thường là các ký tự không hoa). Nội dung của các biến này thường tùy vào thiết lập của hệ thống. Một số biến môi trường phổ biến là:
