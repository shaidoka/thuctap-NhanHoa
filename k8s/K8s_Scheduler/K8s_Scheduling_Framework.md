# Khung lập lịch 

Khung lập lịch (scheduling framework) là một kiến trúc có thể mở rộng (theo dạng plugin) được cho K8s Scheduler giúp tùy chỉnh scheduler dễ dàng. Nó thêm các API "plugin" mới vào scheduler hiện có. Các plugin được biên dịch vào scheduler. Các API cho phép hầu hết các tính năng lập lịch được triển khai dưới dạng plugin, trong khi vẫn giữ cho "lõi" lập lịch đơn giản và dễ bảo trì. 

## Framework workflow

Khung lập lịch xác định một số điểm mở rộng (**extension point**). Các plugin của scheduler đăng ký để được gọi tại một hoặc nhiều điểm mở rộng. Một số plugin này có thể thay đổi quyết định lập lịch và một số plugin chỉ mang tính thông tin.

Mỗi nỗ lực lập lịch cho một Pod được chia thành 2 giai đoạn:
- Chu kỳ lập lịch (scheduling cycle)
- Chu kỳ liên kết (binding cycle)

### Chu kỳ lập lịch và Chu kỳ liên kết

Chu kỳ lập lịch (scheduling cycle) có trách nhiệm lựa chọn một node cho Pod và chu kỳ liên kết (binding cycle) áp dụng quyết định đó cho cluster. Cùng với nhau, chu kỳ lập lịch và chu kỳ liên kết được gọi là "ngữ cảnh lập lịch" (scheduling context)

Các chu kỳ lập lịch được chạy nối tiếp, trong khi các chu kỳ liên kết có thể chạy đồng thời.

Một chu kỳ lập lịch hoặc liên kết có thể bị hủy bỏ nếu Pod được xác định là không thể lập lịch dược hoặc nếu có lỗi nội bộ. Pod sẽ được đưa trở lại hàng đợi và thử lại.

### Các điểm mở rộng

Hình bên dưới cho thấy ngữ cảnh lập lịch của Pod và các điểm mở rộng mà khung lập lịch trưng bày (expose) ra. Trong hình này "Filter" là tương đương với "Predicate" và "Scoring" là tương đương với "Priority function"

Một plugin có thể đăng ký tại nhiều điểm mở rộng để thực hiện các tác vụ phức tạp hơn hoặc tác vụ có trạng thái (stateful)

![](./images/Scheduler_6.png)

1. QueueSort

Các plugin này được sử dụng để sắp xếp cá cPod trong hàng đợi lập lịch. Một plugin queuesort về cơ bản cung cấp hàm ```less(Pod1, Pod2)```. Tại 1 thời điểm chỉ có thể bật một plugin queuesort.

2. PreFilter

Các plugin này được sử dụng để xử lý trước (tiền xử lý) thông tin về Pod hoặc để kiểm tra các điều kiện nhất định mà cluster hoặc Pod phải đáp ứng. Nếu một plugin PreFilter trả về lỗi thì chu kỳ lập lịch (scheduling cycle) sẽ bị hủy bỏ.

3. Filter

Các plugin này được sử dụng để lọc ra các node không thể chạy Pod. Đối với mỗi node, scheduler sẽ gọi các filter plugin theo thứ tự đã được cấu hình. Nếu bất kỳ filter plugin nào đánh dấu node là không khả thi thì các plugin còn lại sẽ không được gọi cho node đó. Các node có thể được đánh giá (bởi filter plugin) đồng thời.

4. PreScore

Các plugin này được sử dụng để thực hiện công việc "pre-scoring" (trước khi tính điểm), tạo ra trạng thái có thể chia sẻ cho các Score plugin sử dụng. Nếu một PreScore plugin trả về lỗi thì chu kỳ lập lịch (scheduling cycle) sẽ bị hủy bỏ.

5. Score

Các plugin này được sử dụng để xếp hạng các node đã qua được giai đoạn lọc (filter ở trên). Scheduler sẽ gọi từng score plugin cho mỗi node. Sẽ có một dãy số nguyên được xác định rõ để đại diện cho điểm tối thiểu (min) và tối đa (max). Sau giai đoạn **NormalizeScore**, scheduler sẽ tổng hợp điểm của node từ tất cả các plugin theo trọng số plugin đã được cấu hình.

6. NormalizeScore

Các plugin này được sử dụng để sửa đổi điểm số (score) trước khi scheduler tính toán xếp hạng các Node lần cuối. Một plugin đăng ký cho điểm mở rộng này sẽ được gọi với Score kết quả từ cùng 1 plugin. Việc này được gọi một lần cho mỗi plugin trong mỗi chu kỳ lập lịch (scheduling cycle).

Ví dụ: giả sử một plugin ```BlinkingLightScorer``` xếp hạng các Node dựa trên số lượng đèn nhấp nháy mà chúng có

```sh
func ScoreNode(_ *v1.pod, n *v1.Node)(int, error){
    return getBlinkingLightCount(n)
}
```

Tuy nhiên, số lượng đèn nhấp nháy tối đa có thể nhỏ so với ```NodeScoreMax```. Để khắc phục điều này, ```BlinkingLightScorer``` cũng nên đăng ký cho điểm mở rộng này.

```sh
func NormalizeScores(scores map[string]int){
    highest := 0
    for _, score := range scores {
        highest = max(highest, score)
    }
    for node, score := range scores {
        scores[node] = score*NodeScoreMax/highest
    }
}
```

Nếu bất kỳ plugin NormalizeScore nào trả về lỗi thì chu kỳ lập lịch (scheduling cycle) sẽ bị hủy bỏ.

7. Reserve

Đây là một điểm mở rộng thông tin. Các plugin duy trì trạng thái runtime (hay còn gọi là "stateful plugin") nên sử dụng điểm mở rộng này để được scheduler cảnh báo khi tài nguyên trên một node đang được dành riêng (reserve) cho một Pod nhất định. Điều này xảy ra trước khi scheduler thực sự liên kết (bind) Pod với Node và nó tồn tại để ngăn chặn race condition trong khi scheduler chờ đợi việc bind thành cong.

Đây là bước cuối cùng trong một chu kỳ lập lịch (scheduling cycle). Một khi Pod ở trạng thái dự trữ (reserve), nó sẽ kích hoạt các plugin Unreserve (khi thất bại) hoặc plugin PostBind (khi thành công) vào cuối chu kỳ liên kết (binding cycle)

8. Permit

Các Permit plugin được gọi vào cuối chu kỳ lập lịch (scheduling cycle) của mỗi Pod để ngăn chặn hoặc trì hoãn việc liên kết (bind) của node ứng viên. Một permit plugin có thể thực hiện một trong 3 điều sau:
- ```approve```: (phê duyệt) khi tất cả các plugin Permit đều phê duyệt (approve) một Pod, nó sẽ được gửi đi để liên kết (bind).
- ```deny```: (từ chối) nếu bất kỳ plugin Permit nào từ chối một Pod, nó sẽ được trả về hàng đợi lập lịch. Điều này sẽ kích hoạt Unreserve plugin
- ```wait```: (chờ đợi với thời gian chờ - timeout) nếu một plugin Permit trả về "wait", thì Pod được giữ trong danh sách các Pod "waiting" nội bộ và chu kỳ liên kết (binding cycle) của Pod này bắt đầu nhưng trực tiếp ngăn chặn cho đến khi nó được phê duyệt (approve). Nếu thời gian chờ (timeout) đã hết thì **wait** sẽ trở thành **deny** và Pod được đưa trở lại hàng đợi lập lịch, kích hoạt các plugin Unreserve

9. PreBind

Các plugin này được sử dụng để thực hiện bất kỳ công việc nào cần thiết trước khi Pod bị liên kết (bound). Ví dụ: một pre-bind có thể chuẩn bị (provision) một network volume và mount nó vào node đích trước khi cho phép Pod chạy ở đó.

Nếu bất kỳ plugin PreBind nào trả về lỗi thì Pod sẽ bị từ chối và trở lại hàng đợi lập lịch.

10. Bind

Các plugin này được sử dụng để liên kết (bind) Pod với Node. Các plugin Bind sẽ không được gọi cho đến khi tất cả các plugin PreBind đã hoàn thành. Mỗi plugin Bind được gọi theo thứ tự đã được cấu hình. Một plugin bind có thể lựa chọn có nên xử lý (handle) Pod đã cho hay không. Nếu một plugin bind chọn sẽ xử lý (handle) một Pod thì các plugin bind còn lại sẽ bị bỏ qua.

11. PostBind

Đây là một điểm mở rộng thông tin. Các post-bind được gọi sau khi Pod được liên kết (bind) thành công. Đây là phần cuối của một chu kỳ liên kết (binding cycle) và có thể được sử dụng để dọn dẹp các tài nguyên liên quan.

12. Unreserve

Đây là một điểm mở rộng thông tin. Nếu một Pod đã được dành riêng (reserved) và sau đó bị từ chối trong giai đoạn sau thì các plugin unreserve sẽ được cảnh báo. Các plugin unreserve sẽ xóa trạng thái được liên kết với reserved Pod.

Các plugin sử dụng điểm mở rộng này thường cũng nên sử dụng **Reserve**

## Plugin API

Có 2 bước đó với API plugin:
- Đầu tiên, các plugin phải đăng ký và được cấu hình
- Sau đó chúng sử dụng các giao diện (interface) điểm mở rộng. Các giao diện điểm mở rộng có dạng sau:

```sh
type Plugin interface {
    Name() string
}

type QueueSortPlugin interface {
    Plugin
    Less(*v1.pod, *v1.pod) bool
}

type PreFilterPlugin interface {
    Plugin
    PreFilter(context.Context, *framework.CycleState, *v1.pod) error
}
```

## Cấu hình Plugin

Ta có thể bật hoặc tắt các plugin trong cấu hình của scheduler. Nếu ta đang sử dụng K8s v1.18 trở lên, hầu hết các plugin lập lịch đều đang được sử dụng và được bật theo mặc định.

Ngoài các plugin mặc định, ta cũng có thể triển khai các plugin lập lịch của riêng mình và cấu hình chúng cùng với các plugin mặc định. Ta có thể xem scheduler-plugin để biết thêm chi tiết.

Nếu ta đang sử dụng K8s v1.18 trở lên, ta có thể cấu hình các plugin như là scheduler profile và sau đó định nghĩa nhiều profile để phù hợp với nhiều loại workload khác nhau.