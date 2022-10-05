# Biến, kiểu dữ liệu số và string

### 1. Biến

- Trong lập trình, biến (variable) là tên của 1 vùng nhớ trong RAM, được sử dụng để lưu trữ thông tin. Có thể gán thông tin cho 1 biến, và lấy thông tin đó ra để sử dụng. Khi 1 biến được khai báo, 1 vùng trong bộ nhớ sẽ dành cho các biến. Biến cực kỳ quan trọng và không thể thiếu trong bất cứ chương trình lớn nhỏ nào

- Đặc điểm của biến:
    - Tên biến không được bắt đầu bằng số
    - Tên biến không được trùng với các từ khóa của python
    - Tên biến chỉ chứa các chữ cái, số và dấu "_"
    - Tên biến có phân biệt chữ hoa chữ thường

- Khởi tạo 1 biến:

```sh
[tên biến] = [giá trị của biến]
```

- VD: ```abc = "xyz"``` hay ```x = 123```

- Khởi tạo nhiều biến

```sh
[tên biến 1], [tên biến 2], [...] = [giá trị biến 1], [giá trị biến 2], [...]
```

- Các kiểu dữ liệu của biến: không như đa số các ngôn ngữ lập trình khác khi khai báo biến phải đi kèm với kiểu dữ liệu. Trong python thì kiểu dữ liệu của biến sẽ tự được hiểu tự động khi gán giá trị cho biến

- Các kiểu dữ liệu có thể bao gồm: numbers, string, list, tuple, dictionary

- Để kiểm tra kiểu dữ liệu của 1 biến đã khởi tạo, ta sử dụng

```sh
type([tên biến])
```

### 2. Kiểu dữ liệu số trong python

- Trong python hỗ trợ rất nhiều kiểu dữ liệu số (numeric). Trong đó có: số nguyên (integer), số thực (floating-point), phân số (fraction), số thức (complex)

- Số thực trong python có độ chính xác xấp xỉ 15 chữ số thập phân, nếu muốn kết quả chính xác hơn ở dạng decimal thì dùng

```sh
# import toàn bộ nội dung của thư viện decimal
from decimal import *
# Lấy tối đa 20 chữ số phần nguyên và phần thập phân
getcontext().prec = 20
```

- Phân số: để tạo 1 phân số trong python, ta sử dụng hàm Fraction

```sh
Fraction(<tử_số>,<mẫu_số>)
```

- Số phức: để tạo 1 số phức, sử dụng hàm Complex với cú pháp sau

```sh
complex(<phần_thực>, <phần_ảo>)
```

- Gán giá trị số phức cho 1 biến

```sh
<tên_biến> = <phần_thực> + <phần_ảo>j
```

- Xuất ra từng phần của số phức

```sh
# phần thực
<tên_biến>.real
# phần ảo
<tên_biến>.imag
```

- Các kiểu toán tử:

|Biểu thức|Mô tả|
|:-|:-|
|X + Y|Tổng của X và Y|
|X - Y|Hiệu của X và Y|
|X * Y|Tích của X và Y|
|X / Y|Thương của X và Y (luôn là 1 số thực)|
|X // Y|Thương nguyên của X với Y (kết quả luôn nhỏ hơn hoặc bằng X / Y)|
|X % Y|Chia lấy dư của phép chia X cho Y|
|X ** Y|Lũy thừa mũ Y với cơ số X (X^Y)|

- Thư viện math trong python: thư viện math trong python hỗ trợ rất nhiều hàm tính toán liên quan đến toán học

- Để sử dụng 1 thư viện nào đó, ta dùng lệnh

```sh
import <tên_thư_viện>
```

- Muốn sử dụng hàm nào đó của thư viện, ta sử dụng cú pháp

```sh
<tên_thư_viện>.<tên_hàm>
```

- Dưới đây là 1 số hàm thường được dùng trong việc tính toán cơ bản

|Tên hàm|Công dụng|
|:-|:-|
|.trunc(x)|Trả về 1 số nguyên là phần nguyên của số x|
|.floor(x)|Làm tròn xuống số x|
|.ceil(X)|Làm tròn lên số x|
|.fabs(x)|Trả về giá trị tuyệt đối của số x|
|.sqrt(x)|Trả về 1 số thực là căn bậc 2 của số x|
|.gcd(x, y)|Trả về 1 số nguyên là ước chung lớn nhất của 2 số x và y|

### Kiểu dữ liệu chuỗi trong Python

- Trong python, chuỗi (string) là những thứ được đặt trong cặp dấu '' hoặc ""

- Docstring: Docstring là 1 dạng chú thích nhiều dòng, hay xuất hiện ở đầu file python, sau 1 dòng định nghĩa class hoặc hàm. Đây cũng là 1 trong những chuẩn ước về định dạng, trình bày code python

```sh
'''
Những dòng nằm giữa 3 dấu nháy đơn
đều bị comment lại hết
hehe
'''
print("Hello_World!")
```

- Escape Sequence là 1 chuỗi đặc biệt gồm 1 ký tự theo sau dấu "\" có công dụng cụ thể

|Tên|Ký hiệu|Giải thích|
|:-|:-|:-|
|Alert|```\a```|Phát ra tiếng bíp|
|Backspace|```\b```|Đưa con trỏ về lại 1 ký tự|
|Newline|```\n```|Đưa con trỏ tới dòng tiếp theo|
|Horizontal tab|```\t```|In 1 tab ngang|
|Single quote|```\'```|In ra ký tự '|
|Double quote|```\"```|In ra ký tự "|
|Blackslash|```\\```|In ra ký tự \|

- 1 số toán tử với chuỗi

|Toán tử|Cú pháp|Ý nghĩa|
|:-|:-|:-|
|+|A + B|Nối A và B|
|*|A * N|Lặp lại A số lần N|
|in|s in A|Kiểm tra s có là chuỗi con của A không, trả về true hoặc false|

- Indexing: trong 1 chuỗi của python, các ký tự tạo nên chuỗi đó sẽ được đánh số từ 0 đến n-1 từ trái qua phải với n là số kí tự có trong chuỗi. Không chỉ đánh số từ trái qua phải, python còn đánh số từ phải qua trái với giá trị -1 đến -n

VD: Chuỗi s = "abc xyz" sẽ được đánh số như sau

|a|b|c|_|x|y|z|
|:-|:-|:-|:-|:-|:-|:-|
|0|1|2|3|4|5|6|
|-7|-6|-5|-4|-3|-2|-1|

- Dựa vào đây, có thể lấy bất kỳ kí tự nào trong chuỗi

```sh
s[2]
# kết quả trả về là "c"
```

- Cắt chuỗi: dựa trên indexing, python cho phép cắt chuỗi. Cú pháp:

```sh
<chuỗi>[vị_trí_bắt_đầu:vị_trí_dừng]
```

=> Khi sử dụng cú pháp này, ta sẽ nhận được 1 chuỗi. Chuỗi này chính là bản sao của chuỗi mà ta muốn cắt. Ta sẽ cắt lấy từng ký tự có vị trí từ ```[vị_trí_bắt_đầu]``` đến ```[vị_trí_dừng] - 1``` và từ trái sang phải

- Ép kiểu dữ liệu: trong trường hợp muốn chuyển chuỗi (có nội dung là số) về số để tính toán hoặc ngược lại, phải ép kiểu dữ liệu. VD: ```int([tên_biến])``` để ép biến thành số nguyên và ```float[(tên_biến)]``` để ép biến thành số thực

- Các phương thức với chuỗi

|Phương thức|Công dụng|
|:-|:-|
|<chuỗi>.capitalize()|Trả về 1 chuỗi với ký tự đầu tiên được viết hoa và viết thường tất cả ký tự còn lại|
|<chuỗi>.upper()|Trả về 1 chuỗi với tất cả ký tự viết hoa|
|<chuỗi>.lower()|Trả về 1 chuỗi với tất cả ký tự viết thường|
|<chuỗi>.swapcase()|Viết hoa thành viết thường, viết thường thành viết hoa|
|<chuỗi>.title()|Trả về 1 chuỗi mà tất cả các từ được viết hoa chữ đầu tiên, còn lại viết thường|
|<chuỗi>.center(width, [fillchar])|Trả về 1 chuỗi được căn giữa với chiều rộng width. Nếu fillchar là None thì sẽ dùng ký tự khoảng trắng (space) để căn, không thì sẽ căn bằng ký tự fillchar. Ký tự fillchar là 1 chuỗi có độ dài bằng 1|
|<chuỗi>.rjust(width, [fillchar])|Căn phải với chiều rộng width|
|<chuỗi>.ljust(width, [fillchar])|Căn trái với chiều rộng width|
|<chuỗi>.encode(encoding='utf-8', errors='strict')|Đây là phương thức dùng để encode 1 chuỗi với phương thức mã hóa mặc định là utf-8. Còn về errors mặc định sẽ là strict có nghĩa là sẽ có thông báo lỗi hiện lên nếu có vấn đề xuất hiện trong quá trình encode chuỗi|
|<ký_tự_nối>.join(<iterable>)|Trả về 1 chuỗi bằng cách nối các phần tử trong iterable bằng ký_tự_nối. Một iterable có thể là 1 tuple, list,...hoặc là 1 iterator|
|<chuỗi>.replace(old, new, [count])|Trả về 1 chuỗi với chuỗi old nằm trong chuỗi ban đầu được thay thế bằng chuỗi new. Nếu count khác none thì ta sẽ thay thế onl bằng new với số lượng count từ trái qua phải. Nếu chuỗi old không nằm trong chuỗi ban đầu hoặc count = 0 thì sẽ trả về 1 chuỗi giống y đúc chuỗi ban đầu|
|<chuỗi>.strip([chars])|Trả về chuỗi với phần đầu và phần đuôi của chuỗi được bỏ đi các ký tự chars. Nếu chars bị bỏ trống thì mặc định các ký tự bỏ đi là dấu space và các escape sequence|
|<chuỗi>.rstrip()|Strip phần đuôi|
|<chuỗi>.lstrip()|Strip phần đầu|
|<chuỗi>.rsplit(sep=None, maxsplit=-1)|Tương tự như split(), khác là tách từ bên phải sang bên trái|
|<chuỗi>.partition(sep)|Trả về 1 tuple với 3 phần tử. Các phần tử đó lần lượt là chuỗi_trước_sep, sep, và chuỗi_sau_sep. Trong trường hợp không tìm thấy sep trong chuỗi, mặc định trả về giá trị đầu tiên là chuỗi ban đầu và 2 giá trị kế tiếp là chuỗi rỗng|
