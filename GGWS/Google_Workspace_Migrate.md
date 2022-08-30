# Hướng dẫn các bước chuyển dữ liệu bằng Google Workspace Migrate

Nếu bạn muốn di chuyển dữ liệu của mình tới Google Workspace (hay còn biết tới là G-Suite). Hay bạn muốn chuyển dữ liệu cá nhân từ Office 365 đến GGWS, hoặc đơn giản là bạn muốn di chuyển email giữa các miền G-Suite.

Không quan trọng bạn muốn làm gì, việc di chuyển dữ liệu sẽ khá là khó khăn. Một sai lầm có thể dẫn tới hậu quả nghiêm trọng như mất dữ liệu hay rò rỉ thông tin mật. Bởi vậy, việc di chuyển dữ liệu cho tổ chức cần phải thực hiện theo đúng quy trình nhất có thể.

Trong bài hướng dẫn này, chúng ta hãy cùng đi tìm hiểu các bước để di chuyển dữ liệu của Google Workspace một cách đúng đắn. Cũng như tìm hiểu thêm về những công cụ của bên thứ 3 giúp bỏ qua những giới hạn của giải pháp truyền thống.

## Công cụ di chuyển dữ liệu Google Workspace

Google cung cấp công cụ của chính họ ở trong trung tâm điều khiển Google Workspace của admin. Công cụ này cho phép người quản trị kiểm soát được dữ liệu của nhân viên. Người quản trị có thể dùng nó để di chuyển dữ liệu từ Google Workspace hoặc Office 365 đến một miền của Google Workspace.

Tuy nhiên, công cụ di chuyển dữ liệu của Google Workspace có 1 vài giới hạn khiến người quản trị không thể thực hiện di chuyển dữ liệu 100%. Vì điều này, quản trị viên phải đối mặt với những phức tạp không cần thiết trong quá trình chuyển dịch dữ liệu, khiến nó trở nên kém hiệu quả và thiếu liền mạch.

Mặc dù vậy, công cụ di chuyển dữ liệu của Google Workspace là 1 ứng dụng build-in tốt để di chuyển 1 vài loại dữ liệu cụ thể. Ở bài viết này, chúng tôi sẽ hướng dẫn bạn các bước để thực hiện di chuyển dữ liệu. Trong trường hợp bạn thấy giải pháp này không hiệu quả, vậy thì chúng tôi vẫn có những tiện ích mở rộng hiệu quả và thuận tiện hơn. Hãy đọc toàn bộ hướng dẫn để biết thêm về nó!

## Từng bước hoạt động của dịch vụ di chuyển dữ liệu của Google Workspace

1. Để bắt đầu việc di dời dữ liệu, đầu tiên, mở bảng quản trị của Google Workspace và chọn **"Data Migration"**

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/1-1.png)

2. Ở cửa sổ tiếp theo, nhấn vào nút **"SET UP DATA MIGRATION"** để tiếp tục hoặc nhấn **"Learn more"** để có thêm thông tin về quá trình di chuyển dữ liệu

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/2-1.png)

3. Cửa sổ di chuyển dữ liệu sẽ mở và ở đây bạn cần phải chọn nền tảng nguồn

- **Google Workspace:** nếu nền tảng nguồn là GGWS thì phần còn lại của trường dữ liệu sẽ bị làm mờ đi
- **Office 365(Microsoft 365):** nếu nền tảng nguồn là Office 365 thì chọn:
    - **Type of Item to Migrate:** email/contact/calendar (chỉ được chọn 1 loại 1 thời điểm)
    - **Giao thức kết nối:** Auto Select (recommended)
    - Ở phần Xác thực (Authorization), nhấn chọn nút **"Authorise"**
- Sau khi hoàn thành xác thực, bạn sẽ được đưa trở về giao diện quản trị Google Workspace của admin

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/microsoft-4-1024x450.png)

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/microsoft-5.png)

4. Ở cửa sổ tiếp theo, thiết lập **"Migration Start Date"** và chọn **"Migration Option"**. Sau đó, nhấn **"Select User"** để tiếp tục

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/4.png)

5. Bây giờ, để ánh xạ tài khoản người dùng ở nền tảng nguồn và đích, có 2 lựa chọn:

- **Add User:** lựa chọn này có thể sử dụng để ánh xạ tài khoản người dùng ở 1 nguồn và đích. Cung cấp chi tiết về tài khoản nguồn và chọn đích là tài khoản GGWS

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/8.png)

- **Bulk Upload CSV:** lựa chọn này cho phép 1 tệp tin CSV mà chứa danh sách được ánh xạ của tài khoản người dùng nguồn và đích ở định dạng: <địa chỉ email nguồn>, <địa chỉ đích>, <mật khẩu>. Chọn **Attach File** để tải lên và bắt đầu quá trình chuyển dữ liệu

6. Bạn có thể nhìn tiến trình hoạt động của quá trình chuyển dữ liệu và chọn hành động sau khi quá trình này hoàn tất, **"More"** rồi **"Email Report"** hoặc **"Exit Migration"**

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/13.png)

## Những giới hạn về mặt kỹ thuật của dịch vụ di chuyển dữ liệu của Google

- Chỉ di chuyển được email giữa các tài khoản GGWS
- Di chuyền dữ liệu từ Office 365 có thể thực hiện cho email/lịch/liên lạc
- Cần phải bật IMAP cho mỗi người dùng
- Không có lựa chọn di chuyển document đến tài khoản GGWS
- Kết nối Internet kém sẽ khiến quá trình di chuyển dữ liệu thất bại

## Giải pháp di chuyển dữ liệu chuyên nghiệp của GGWS

Tiện ích nói trên từ Google có khá nhiều giới hạn về mặt kỹ thuật mà người quản trị sẽ phải đối mặt. Nếu bạn muốn di chuyển hoàn toàn hàng loạt dữ liệu từ tài khoản GGWS, tiện ích truyền thống có thể sẽ kém hiệu quả và có thể gây mất dữ liệu. Thêm vào đó, thời gian để di chuyển cũng khá lâu.

Vì vậy, những công cụ tự động của bên thứ 3 như SysTools G Suite to G Suite Migration Tool được ra đời để bù đắp những hạn chế này. Công cụ này cung cấp mã hóa đầu cuối trong quá trình chuyển dữ liệu, cho phép di chuyển email, liên lạc, lịch, dữ liệu drive 1 cách liền mạch mà chính xác.

## Từng bước hoạt động của công cụ di chuyển dữ liệu chuyên nghiệp

1. Tải công cụ

- Windows: https://systoolskart.com/download/SYS3G0S3M/434
- Linux: https://systoolskart.com/buy/SYS3S6M8L/434

2. Đầu tiên, chọn nút **Activate** để kích hoạt bản DEMO hoặc PAID của công cụ

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/1-2.png)

3. Sau khi kích hoạt hoàn tất, chọn nền tảng nguồn (G-Suite hoặc Office 365) và sau đó chọn đích là **"G Suite"**

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/2-2.png)

4. Bây giờ, cuộn xuống phần **"Workload section"** để chọn **Category** (email, contact, calendar, document) và chọn khoảng thời gian **date-range filter** cho những dữ liệu đã chọn để di chuyển. Cùng với đó là chọn quyền cho lịch và tài liệu để có thể được thông qua điều khoản truy nhập đến tài khoản đích

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/3-1.png)

5. Sau khi chọn xong đữ liệu cần di chuyển ở tab nguồn. Ta sẽ phải nhập id Admin nguồn và cung cấp id ứng dụng. Để biết cách để tạo id ứng dụng, nhấn vào **"Project Settings"**. Khi mọi trường dữ liệu đã điền xong, nhấn nút **Validate** để xác thực thông tin và chọn **Next**

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/4-1.png)

6. Bây giờ, ở tab đích, nhập id email admin GGWS, và đường dẫn file p12. Để tạo file p12 và id ứng dụng, chọn **"Project Settings"**. Cuối cùng, chọn **validate** để xác thực miền GGWS và chọn **Next**

7. Ở cửa sổ này, chọn tùy chọn để ánh xạ id người dùng từ nguồn và đích với nhau. Công cụ cho phép 2 loại ánh xạ:

- **Fetch User:** sử dụng lựa chọn này để tự động tìm nạp tất cả id người dùng từ nền tảng nguồn và liệt kê họ trên công cụ. Khi quá trình nạp hoàn tất, bạn có thể nhập id user đích ở mỗi trường để ánh xạ
- **Import Users:** sử dụng lựa chọn này để import 1 CSV file chứa danh sách tài khoản người dùng nguồn và đích đã được ánh xạ

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/6-1.png)

8. Sau khi ánh xạ hoàn tất, nhấn vào nút **Validate** để xác thực tài khoản người dùng. Cuối cùng, nhấn **Start Migration** để bắt đầu tiến trình chuyển dữ liệu

![img](https://www.datarecovery.institute/wp-content/uploads/2020/11/user-validate-screen.png)

## Tổng kết

Qua bài hướng dẫn này, chúng ta đã biết được từng bước để di chuyển dữ liệu tới hoặc giữa Google Workspace thông qua tiện ích của Google hoặc qua công cụ tự động. Chúng tôi đã giới thiệu lợi ích của từng giải pháp và cách 1 giải pháp chuyên nghiệp khắc phục tất cả các nhược điểm kỹ thuật của 1 giải pháp truyền thống. Vì vậy, giờ bạn có thể thử cả 2 phương pháp và chọn một phương pháp phù hợp với nhu cầu tổ chức của bạn