# Kiểu dữ liệu List, Tuple, Set trong Python

### 1. Kiểu dữ liệu List

- List là 1 container được sử dụng rất nhiều trong các chương trình Python
- 1 list gồm các yếu tố sau:
    - Được giới hạn bởi cặp ngoặc ```[]```, tất cả những gì nằm trong đó là những phần tử của List
    - Các phần tử của List được phân cách nhau bởi dấu phẩy ```,```
    - List có khả năng chứa mọi giá trị, đối tượng trong Python

- Khởi tạo List:

```sh
[<value_1>, <value_2>, <value_3>,..., <value_n-1>, <value_n>]
```

- Một số toán tử với List trong Python:
    - ```+```: nối 2 list
    - ```*```: lặp list số lần n
    - ```in```: tìm kiếm trong list

- Các phương thức tiện ích:
    - Phương thức count: ```<list>.count(sub, [start, [end]])``` - trả về 1 số nguyên là số lần xuất hiện của sub trong list
        - ```sub```: là phần tử của chuỗi
        - ```start``` và ```end``` là kỹ thuật slicing (ko bắt buộc)