# How to interact with web services using Python

## Giới thiệu

1 API, hay Application Programming Interface, là 1 giao diện mà giúp chúng ta thu thập và gửi dữ liệu sử dụng code. Chúng ta sử dụng APIs nhiều nhất khi thu thập dữ liệu, và điều đó sẽ được đề cập đến trong bài viết này.

Khi chúng ta muốn thu thập dữ liệu từ API, chúng ta cần tạo 1 **request**. **Requests** được sử dụng ở hầu hết mọi website. Ví dụ, khi bạn truy cập bài viết này, trình duyệt của bạn gửi 1 request đến server của Nhân Hòa, thứ mà sẽ phản hồi lại nội dung của trang web bao gồm bài viết.

API request hoạt động với cách thức chính xác như vậy: bạn tạo 1 request đến API server để lấy dữ liệu, và server trả về cho bạn thứ bạn muốn.

## Các phương thức HTTP khác và Mã Trạng Thái

Có nhiều phương thức HTTP cho REST APIs. Những phương thức này giúp API biết được cần phải thực hiện điều gì với dữ liệu. Trong khi có nhiều phương thức HTTP, 5 phương thức HTTP dưới đây được sử dụng hầu hết trong REST APIs:

|HTTP METHOD|DESCRIPTION|
|:-|:-|
|```GET```|Thu thập dữ liệu|
|```POST```|Thêm dữ liệu mới|
|```PUT```|Cập nhật dữ liệu đã tồn tại|
|```PATCH```|Cập nhập dữ liệu của 1 phần chỉ định|
|```DELETE```|Xóa dữ liệu|

Mỗi khi REST API nhận và xử lý HTTP request, nó trả về response với HTTP status code. Mã trạng thái này cung cấp thông tin về response và giúp ứng dụng client biết loại của response.

Mã trạng thái dựa trên bảng phân loại dưới đây:

|CODE RANGE|CATEGORY|
|:-|:-|
|```1xx```|Thông tin response|
|```2xx```|Thực thi thành công|
|```3xx```|Chuyển hướng|
|```4xx```|Lỗi phía client|
|```5xx```|Lỗi phía máy chủ|

## API Endpoints

API Endpoint là URLs công khai bởi server mà 1 ứng dụng client sử dụng để truy nhập vào tài nguyên và dữ liệu

Trong bài này chúng ta sử dụng dữ liệu giả, chi tiết trong bảng sau:

|HTTP METHOD|API ENDPOINT|DESCRIPTION|
|:-|:-|:-|
|```GET```|```/products```|Lấy danh sách sản phẩm|
|```GET```|```/products?limit=x```|Lấy sản phẩm x|
|```GET```|```/products/<product_id>```|Lấy sản phẩm theo id|
|```POST```|```/products```|Tạo 1 sản phẩm mới|
|```PUT```|```/products/<product_id>```|Cập nhật 1 sản phẩm|
|```PATCH```|```/products/<product_id>```|Cập nhật 1 thành phần của sản phẩm|
|```DELETE```|```/products/<product_id>```|Xóa 1 sản phẩm|

Mỗi endpoints trên thực hiện 1 hành động khóa nhau dựa trên HTTP method, với base URL là ```https://fakestoreapi.com```

Trước khi bắt đầu, hãy cahwsc chắn là đã cài đặt thư viện ```requests``` của Python

```sh
pip install requests
```

## GET Request

Đây là phương thức HTTP request phổ biến nhất, nó là 1 **read-only** operation mà chỉ cho phép người sử dụng thu thập dữ liệu từ API.

Hãy thử GET request trên endpoint đầu tiên chúng ta đề cập ở trên mà phản hồi lại 1 danh sách sản phẩm

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

response = requests.get(f"{BASE_URL}/products")
print(response.json())
```

Script bên trên sử dụng phương thức ```requests.get()``` để gửi GET request đến API endpoint ```/products```. Nó phản hồi với 1 danh sách tất cả các sản phẩm. Chúng ta sau đó gọi ```.json()``` để xem kết quả dưới dạng JSON.

```sh
[
  {
    "id": 1,
    "title": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
    "price": 109.95,
    "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
    "category": "men's clothing",
    "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
    "rating": {
      "rate": 3.9,
      "count": 120
    }
  },
  {
    ...
```

Nếu ta nhìn kỹ hơn, JSON response trông rất giống Python ditionaries. JSON là 1 định dạng trao đổi dữ liệu rất phổ biến cho REST APIs.

Ta cũng có thể in ra mã trạng thái của response bằng thuộc tính

```sh
print(response.status_code)

## OUTPUT
>>> 200
```

Như đã đề cập ở trên, mã trạng thái 200 có nghĩa là phản hồi thành công

Trong khi ```/products``` endpoint trả về rất nhiều dữ liệu, hãy giới hạn nó lại thành 3 products

Để làm điều này, hãy gọi tới endpoint ```/products?limit=x``` nơi mà x là số nguyên dương. ```limit``` được gọi là tham số truy vấn. Hãy xem cách chúng ta có thể thêm tham số truy vấn này vào request

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

query_params = {
    "limit":3
}

response = requests.get(f"{BASE_URL}/products",params=query_params)
print(response.json())
```

Phương thức ```requests.get()``` lấy tham số gọi là ```params``` nơi mà chúng ta có thể chỉ định tham số truy vấn trong định dạng 1 Python dictionary. Theo đó, chúng ta tạo 1 dictionary gọi là ```query_params``` và đưa vào đó key ```limit``` và value ```3```. Chúng ta đưa tham số ```query_params``` vào ```requests.get()```.

Giờ chúng ta có dữ liệu response được giới hạn thành 3 sản phẩm. Hãy thử lấy dữ liệu của sản phẩm có ```id``` 18

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

response = requests.get(f"{BASE_URL}/products/18")
print(response.json())
```

## POST Request

Chúng ta sử dụng POST request để thêm 1 dữ liệu mới vào REST API. Dữ liệu được gửi đến server dưới dạng JSON, thứ mà sẽ tương tự như Python dictionary. Theo tài liệu của API mà chúng ta sử dụng trong bài này, 1 sản phẩm có các thuộc tính sau đây: ```title```, ```price```, ```description```, ```image``` và ```category```. Vì vậy, 1 sản phẩm mới sẽ có trông như sau:

```sh
new_product = {
    "title": "test product",
    "price": 13.5,
    "description": "lorem ipsum set",
    "image": 'https://i.pravatar.cc',
    "category": "electronic"
}
```

Giờ hãy gửi POST request này sử dụng ```requests.post()``` như sau:

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

new_product = {
    "title": "test product",
    "price": 13.5,
    "description": "lorem ipsum set",
    "image": 'https://i.pravatar.cc',
    "category": "electronic"
}

response = requests.post(f"{BASE_URL}/products", json=new_product)
print(response.json())
```

Trong phương thức ```requests.post()```, chúng ta truyền vào dữ liệu JSON sử dụng đối số ```json```. Sử dụng đối số ```json``` tự động thiết lập ```Content-Type``` thành ```Application/JSON``` trong request header.

Một khi chúng ta tạo 1 POST request trên ```/products``` endpoint, chúng ta có thể lấy đối tượng product với id trong phản hồi, nó có dạng như sau:

```sh
{
  "_id": "61b45067e087f30012c45a45",
  "id": 21,
  "title": "test product",
  "price": 13.5,
  "description": "lorem ipsum set",
  "image": "https://i.pravatar.cc",
  "category": "electronic"
}
```

Nếu chúng ta không sử dụng đối số ```json```, chúng ta phải tạo 1 POST request có dạng như sau:

```sh
import requests
import json

BASE_URL = 'https://fakestoreapi.com'

new_product = {
    "title": 'test product',
    "price": 13.5,
    "description": 'lorem ipsum set',
    "image": 'https://i.pravatar.cc',
    "category": 'electronic'
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(f"{BASE_URL}/products", data=json.dumps(new_product), headers=headers)
print(response.json())
```

## PUT Request

Chúng ta thường cần cập nhật dữ liệu đã tồn tại trong API. Sử dụng PUT request, chúng ta có thể cập nhật dữ liệu hoàn chỉnh. Điều này có nghĩa là khi chúng ta tạo 1 PUT request, nó thay thế dữ liệu cũ với dữ liệu mới.

Trong POST request, chúng ta tạo 1 sản phẩm mới với ```id``` là 21. Giờ hãy cập nhật nó:

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

updated_product = {
    "title": 'updated_product',
    "category": 'clothing'
}

response = requests.put(f"{BASE_URL}/products/21", json=updated_product)
print(response.json())
```

Sau đó, ta sẽ nhập về phản hồi như này:

```sh
{
  "id": "21",
  "title": "updated_product",
  "category": "clothing"
}
```

## PATCH Request

Đôi khi, chúng ta không cần phải thay thế hoàn toàn dữ liệu cũ, mà chỉ muốn thay đổi chỉ 1 trường nhất định trong đó. Trong trường hợp này, PATCH request nên được sử dụng.

Hãy cập nhật category của sản phẩm trước đó từ clothing thành electronic:

```sh
import requests

BASE_URL = 'https://fakestoreapi.com'

updated_product = {
    "category": 'electronic'
}

response = requests.patch(f"{BASE_URL}/products/21", json=updated_product)
print(response.json())
```

Trong trường hợp này, chúng ta có thể sử dụng phương thức ```requests.patch()```, thứ mà sẽ trả về 1 phản hồi như thế này:

```sh
{
  "id": "21",
  "title": "updated_product",
  "category": "electronic"
}
```

## DELETE Request

Đúng như cái tên, nếu chúng ta cần xóa 1 tài nguyên từ API, chúng ta có thể sử dụng 1 DELETE request, ví dụ như thế này:

```sh
import requests

BASE_URL= 'https://fakestoreapi.com'

response = requests.delete(f"{BASE_URL}/products/21")
print(response.json())
```

Phương thức ```requests.delete()``` giúp chúng ta tạo 1 DELETE request trên ```/products/<product_id>``` endpoint