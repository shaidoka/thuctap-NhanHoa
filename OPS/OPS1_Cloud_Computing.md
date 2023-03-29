# Phần 2: Tổng quan về Cloud Computing

## I. Khái niệm cơ bản về Cloud Computing

Điện toán đám mây là sự truy cập thông qua internet đến tài nguyên điện toán - bao gồm ứng dụng, máy chủ (cả vật lý và máy ảo), kho dữ liệu, công cụ phát triển, network, và nhiều hơn nữa - được đặt tại 1 data center từ xa và được quản lý bởi 1 nhà cung cấp dịch vụ cloud (Cloud service provider - CSP).

So với các phương pháp công nghệ truyền thống, và phụ thuộc vào loại dịch vụ cloud ta sử dụng, cloud computing sẽ cho phép:
- **Giảm thiểu chi phí về công nghệ:** Cloud cho phép ta loại bỏ một vài hoặc hầu hết các chi phí và của việc mua bán, cài đặt, thiết lập, và quản lý cơ sở hạ tầng của riêng mình
- **Tăng tính linh hoạt và hiệu quả:** Với cloud, các tổ chức sẽ có thể bắt đầu sử dụng những ứng dụng doanh nghiệp với một vài phút thay vì phải chờ nhiều tuần đến nhiều tháng cho việc triển khai phần cứng cũng như cài đặt phần mềm. Cloud cũng cho phép các developer hay data scientist tự chủ về mặt phần mềm và cơ sở hạ tầng.
- **Dễ dàng mở rộng và tối ưu hóa chi phí:** Cloud cung cấp sự mềm dẻo - thay vì thanh toán một lượng tài nguyên cố định và có thể thiếu hoặc thừa tùy thuộc vào nhu cầu sử dụng tại các thời điểm khác nhau. Cloud cho phép ta tăng hoặc giảm tài nguyên theo ý muốn, từ đó chi phí cũng thay đổi cho phù hợp.

Thuật ngữ "Cloud Computing" cũng liên quan tới công nghệ được sử dụng cho cloud. Điều này bao gồm 1 vài dạng ảo hóa cơ sở hạ tầng - máy chủ, phần mềm hệ điều hành, mạng, và các cơ sở hạ tầng trừu tượng khác. Chi tiết hơn về ảo hóa đã được đề cập ở phần trước.

Việc chúng ta sử dụng máy tính hay thiết bị điện thoại di động cũng hầu như chắc chắn sử dụng một vài dạng nào đó của điện toán đám mây. Điển hình như các ứng dụng đám mây như Google, Gmail, Salesforce, phương tiện streaming như Netflix, hoặc kho dữ liệu đám mây như Dropbox.

## II. Các dịch vụ Cloud Computing

Có 3 loại hình dịch vụ cloud phổ biến là: **IaaS (Infrastructure as a Service)**, **SaaS (Software as a Service)**, **PaaS (Platform as a Service)** và sẽ không có gì lạ nếu một tổ chức sử dụng cả 3 loại này.

### 1. IaaS - Infrastructure as a Service

IaaS cung cấp truy cập đến tài nguyên điện toán - như máy chủ ảo hay vật lý, kết nối mạng và kho dữ liệu - thông qua internet trên cơ sở dùng bao nhiêu trả bấy nhiêu. IaaS cho phép người dùng cuối mở rộng hoặc thu hẹp tài nguyên tùy theo mức độ sử dụng, giảm thiểu chi phí vượt quá nhu cầu một cách không cần thiết hoặc chi trả quá tay cho phần cứng vào thời điểm mức sử dụng cao nhưng sau đó lại không tận dụng được tối ưu tài nguyên.

Đối lập với SaaS và PaaS (và thậm chí là loại hình PaaS mới như container hay serverless), IaaS cung cấp cho người dùng sự điều khiển thấp nhất của tài nguyên điện toán trong cloud.

IaaS là loại hình phổ biến nhất của cloud computing kể từ khi nó nổi lên từ những năm 2010. Mặc dù IaaS vẫn là mô hình được sử dụng cho rất nhiều loại công việc, song sự phát triển của SaaS và PaaS vẫn nhanh hơn rất nhiều.

### 2. SaaS - Software as a Service

SaaS hay còn được biết tới là phần mềm dựa trên cloud hoặc ứng dụng cloud, là những phần mềm ứng dụng mà được xây dựng trên cloud, và người dùng sẽ truy nhập thông qua trình duyệt web, 1 desktop client, hay 1 API mà tích hợp với 1 hệ điều hành desktop hoặc di động. Trong hầu hết trường hợp, người dùng SaaS thanh toán chi phí sử dụng hàng tháng hoặc hàng năm, một vài trường hợp dùng bao nhiêu trả bấy nhiêu sẽ dựa trên mức độ sử dụng cụ thể.

Để tiết kiệm chi phí, tối ưu thời gian, và khả năng mở rộng quy mô của cloud, SaaS còn cung cấp thêm khả năng:
- Tự động nâng cấp: Với SaaS, người dùng có thể sử dụng các tính năng mới ngay sau khi nhà cung cấp thêm nó vào mà không cần phải diễn ra một bản nâng cấp nào cả.
- Bảo vệ khỏi mất dữ liệu: Vì SaaS lưu trữ dữ liệu ứng dụng trên đám mây cùng với ứng dụng, người dùng sẽ không bị mất dữ liệu nếu thiết bị của họ crash hay hỏng hóc.

SaaS là mô hình phân phối chính cho hầu hết các phần mềm thương mại ngày nay - có đến hàng trăm ngàn giải pháp SaaS khả dụng, từ những ứng dụng chuyên ngành đến các phần mềm doanh nghiệp và AI mạnh mẽ.

### 3. PaaS (Platform as a Service)

PaaS cung cấp cho các nhà phát triển phần mềm nền tảng theo yêu cầu — bao gồm phần cứng, bộ phần mềm hoàn chỉnh, cơ sở hạ tầng và thậm chí cả các công cụ phát triển — để triển khai, phát triển và quản lý ứng dụng mà không tốn kém, phức tạp và không linh hoạt khi duy trì nền tảng đó.

Với PaaS, nhà cung cấp cloud xây dựng mọi thứ - máy chủ, kết nối mạng, kho lưu trữ, phần mềm hệ điều hành, phần mềm trung gian, cơ sở dữ liệu - ở data center của họ. Nhà phát triển chỉ cần đơn giản lựa chọn trên một menu để tìm cho mình một server và môi trường thích hợp nhất cho việc chạy, xây dựng, kiểm thử, triển khai, duy trì, cập nhật, và mở rộng quy mô ứng dụng.

Ngày nay, PaaS thường xây dựng xoay quanh container. Container ảo hóa hệ điều hành, cho phép nhà phát triển đóng gói ứng dụng cùng với các dịch vụ trên hệ điều hành nó cần để chạy ở bất kỳ nền tảng nào mà không cần phải thay đổi hay không cần ứng dụng trung gian nào nữa

Red Hat OpenShift là một PaaS phổ biến được xây dựng xoay quanh Docker container và Kubernetes, 1 giải pháp điều hành container mã nguồn mở cho phép tự động hóa triển khai, mở rộng, cân bằng tải, và nhiều hơn nữa cho các ứng dụng dựa trên container.

### 4. Serverless computing

Serverless computing (hay gọi chung là serverless) là 1 mô hình cloud computing mà giảm tải tất cả các tác vụ quản lý cơ sở hạ tầng backend - gồm cung cấp, nhân rộng, lập lịch, vá lỗi - cho nhà cung cấp cloud, giúp người phát triển tập trung vào việc lập trình cho ứng dụng của họ

Hơn nữa, serverless chạy ứng dụng dựa trên cơ sở là từng truy vấn và tự động mở rộng hoặc thu hẹp cơ sở hạ tầng để phản hồi lại lượng truy vấn. Với serverless, khách hàng sẽ chỉ phải trả cho tài lượng tài nguyên họ sử dụng cho việc chạy ứng dụng (tức là họ sẽ không phải trả cho lượng tài nguyên rảnh rỗi)

FaaS hay Function as a Service 