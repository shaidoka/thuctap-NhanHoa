# Mô hình OSI
1. **Khái niệm cơ bản**
 Mô hình OSI (hay Open System Interconnection Reference Model) là một mô hình kiến trúc mạng chuẩn mang tính tham chiếu cho các hệ thống mạng. Mô hình OSI gồm 7 tầng, lý giải một cách trừu tượng kỹ thuật kết nối truyền thông giữa các máy tính và thiết kế giao thức mạng giữa chúng.

2. **Nguyên tắc**
 OSI mô tả chức năng theo dạng phân tầng. Mỗi tầng có 1 vai trò riêng, mỗi vai trò có 1 tập chức năng chuyên biệt.
Mỗi tầng chỉ tương tác với tầng trên và tầng dưới, tầng Application tương tác với user, tầng Physical tương tác với đường truyền vật lý.

3. **Vai trò của từng tầng trong mô hình OSI**
 
 ![](./images/osi.png)
 - Tầng Application: giao tiếp với user thông qua giao diện. Cung cấp các chức năng truyền thông đáp ứng nhu cầu của user.
 - Tầng Presentation: mã hóa, định dạng các bản tin dữ liệu cho phù hợp.
 - Tầng Session: quản lý phiên truyền thông giữa các máy tính, bao gồm thiết lập, duy trì, đồng bộ hóa và hủy bỏ các phiên truyền thông giữa các ứng dụng.
 - Tầng Transport: thực hiện việc chuyển giao dữ liệu giữa các ứng dụng (end-to-end), đảm bảo dữ liệu chính xác, không bị mất mát, trùng lặp.
 - Tầng Network: quy định địa chỉ IP của các máy tính trong mạng, tìm đường đi và chuyển tiếp dữ liệu từ máy gửi đến máy nhận.
 - Tầng Data-Link: Kiểm soát việc truyền dữ liệu giữa các máy tính trên đường truyền vật lý. Đóng gói dữ liệu tầng trên gửi xuống vào trong frame, gửi frame từ tầng dưới lên tầng trên, kiểm tra lỗi frame dữ liệu.
 - Tầng Physical: quản lý truy nhập đường truyền. Chuyển đổi dữ liệu thành tín hiệu vật lý và phát trên đường truyền, chuyển tín hiệu vật lý nhận được thành frame dữ liệu và gửi lên trên.

4. **Quy trình truyền gói tin trong mô hình OSI**
 a. Phía máy gửi
  - Tầng Application: user đưa thông tin cần gửi vào máy tính
  - Tầng Presentation: mã hóa và nén dữ liệu trên
  - Tầng Session: bổ sung thông tin cần thiết cho phiên giao dịch
  - Tầng Transport: tách dữ liệu thành các Segment, bổ sung thêm thông tin về phương thức vận chuyển
  - Tầng Network: tách các Segment thành nhiều Package, bổ sung thêm thông tin về định tuyến
  - Tầng Data-Link: băm nhỏ các Package thành nhiều Frame, bổ sung thêm thông tin để máy nhận kiểm tra dữ liệu
  - Tầng Physical: các frame sẽ được chuyển thành một chuỗi các bit nhị phân và truyền đến máy nhận qua đường truyền vật lý
  **Mỗi gói dữ liệu khi gửi giữa các tầng đều được gắn header của tầng đó, với tầng Data-Link thì có thêm FCS để check lỗi**
 
 b. Phía máy nhận
 - Tầng Physical: kiểm tra quá trình đồng bộ, đưa dữ liệu nhận được vào vùng đệm, thông báo với tầng Data-Link là đã nhận được dữ liệu.
 - Tầng Data-Link: kiểm tra lỗi, nếu có lỗi thì frame đó sẽ bị hủy. Sau đó kiểm tra địa chỉ MAC Address xem có đúng địa chỉ của máy nhận hay không, nếu đúng thì gỡ bỏ Header của Data-Link và chuyển tiếp lên tầng Network.
 - Tầng Network: kiểm tra địa chỉ IP  trong gói tin này xem có phải địa chỉ của máy nhận hay không, nếu đúng thì gỡ bỏ Header của nó và chuyển lên tầng Transport.
 - Tầng Transport: phục hồi và xử lý lỗi bằng cách gửi các gói tin ACK, NAK. Sau khi sửa lỗi, tầng này sắp xếp lại thứ tự của các Segment và chuyển dữ liệu lên tầng trên.
 - Tầng Session: đảm bảo dữ liệu trong gói tin nhận được toàn vẹn. Sau đó gỡ bỏ Header của tầng Session và gửi lên trê.n
 - Tầng Presentation: chuyển đổi định dạng dữ liệu cho phù hợp. Sau khi hoàn thành thì gửi lên trên.
 - Tầng Application: gỡ bỏ Header cuối cùng. Khi đó ở máy nhận sẽ nhận được dữ liệu của gói tin được truyền đi.