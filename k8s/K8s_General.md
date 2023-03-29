# Tổng quan về Kubernetes

Kubernetes hay K8s là một nền tảng điều phối container mã nguồn mở. Ta có thể dùng Kubernetes để tự động hóa nhiều quy trình thủ công liên quan đến việc deploy, quản lý và mở rộng các ứng dụng trong container. Nói cách khác, ta có thể tập hợp các nhóm host đang chạy Linux container với nhau. Từ đó, Kubernetes có thể giúp dễ dàng quản lý các nhóm đó một cách hiệu quả nhất.

Ngoài ra, cluster Kubernetes có thể mở rộng các host trên các cloud tại chỗ public, private hay hybrid. Do đó, Kubernetes là một nền tảng lý tưởng để host các ứng dụng cloud-native yêu cầu khả năng mở rộng nhanh chóng. Chẳng hạn như truyền dữ liệu theo thời gian thực thông qua Apache Kafka.

Ban đầu, Kubernetes được phát triển và thiết kế bởi các kỹ sư tại Google. Do đó, Google chính là một trong những người đóng góp đầu tiên cho công nghệ container của Linux. Đây cũng chính là công nghệ đằng sau các dịch vụ cloud của Google. Tính đến nay, Google tạo ra đến hơn 2 tỷ container mỗi tuần. Tất cả đều được cung cấp bởi nền tảng nội bộ Borg - tiền thân của K8s.

## Ứng dụng của Kubernetes

Ưu điểm chính của việc sử dụng Kubernetes là nó cung cấp nền tảng để lên lịch và chạy các container trên những cluster máy vật lý hoặc máy ảo (VM). Việc này đặc biệt hữu ích nếu ta muốn tối ưu hóa việc dev app cho cloud.

Nói rộng hơn, sử dụng Kubernetes giúp ta triển khai đầy đủ hơn và dựa trên cơ sở hạ tầng container-based trong môi trường sản xuất. Ngoài ra, Kubernetes chủ yếu dùng để tự động hóa các task. Do đó ta có thể làm nhiều việc tương tự nhau mà các nền tảng ứng dụng hay hệ thống quản lý khác cho phép.

Bên cạnh đó, các developer cũng có thể tạo ra những ứng dụng cloud-native làm nền tảng runtime bằng các mẫu Kubernetes. Trong đó, các mẫu này là những công cụ mà một Kubernetes developer cần để build những ứng dụng hoặc dịch vụ container-based

**Ta có thể sử dụng Kubernetes để:**
- Sắp xếp các container trên nhiều host
- Sử dụng phần cứng hiệu quả hơn. Nhằm tối đa hóa tài nguyên cần thiết để chạy các ứng dụng doanh nghiệp
- Kiểm soát và tự động hóa việc triển khai, cập nhật ứng dụng
- Mount và thêm bộ nhớ để chạy ứng dụng có trạng thái
- Mở rộng quy mô và các ứng dụng trong container, cũng như tài nguyên của chúng
- Quản lý các dịch vụ một cách cụ thể, rõ ràng. Từ đó đảm bảo các ứng dụng đã deploy luôn chạy đúng theo kế hoạch
- Kiểm tra tình trạng tự phục hồi ứng dụng với tính năng tự thay thế, tự restart, tự nhân bản và tự động mở rộng

Để sử đụng đầy đủ các tính năng trên cũng như tận dụng tối đa sức mạnh của K8s, ta cần phải thêm 1 và project mã nguồn mở như:
- Registry: thông qua dự án như Docker Registry
- Networking: qua OpenvSwitch và Intelligent edge routing
- Telemetry: thông qua Kibana, Hawkular hoặc Elastic
- Bảo mật: với LDAP, SELinux, RBAC, OAUTH với multitenancy layers
- Tự động hóa bằng cách bổ sung Ansible playbook để cài đặt và quản lý vòng đời của các Cluster
- Dịch vụ: thông qua một catalog chứa nhiều mẫu app phổ biến

## Cách hoạt động của Kubernetes

Trong phần này, ta sẽ tìm hiểu cách hoạt động của Kubernetes là gì. Trước tiên, cần biết rằng mỗi triển khai của một Kubernetes đang hoạt động được gọi là 1 cluster. Ta có thể hình dung cluster gồm 2 phần: 1 control plane và 1 compute machine (hay node)

![](./images/K8s_cluster_model.png)

Mỗi node là một môi trường Linux của chính nó, đó có thể là một máy vật lý hay máy ảo. Mỗi node sẽ chạy các pod được tạo từ những container.

Control plane có nhiệm vụ duy trì trạng thái mong muốn của cluster. Chẳng hạn như ứng dụng đang chạy hay container image đang được sử dụng. Còn compute machine sẽ chạy các ứng dụng và workload.

Kubernetes control plane nhận các lệnh từ admin (hay DevOps team) và chuyển tiếp các lệnh đó đến compute machine. Việc này sẽ hoạt động với vô số dịch vụ để tự động quyết định node phù hợp nhất cho task. Tiếp đến, nó sẽ phân bổ tài nguyên và chỉ định các pod trong node để hoàn thành công việc được yêu cầu.

Trạng thái mong muốn của một cluster sẽ xác định các ứng dụng hoặc workload nên chạy. Cùng với đó là quyết định những image nào sẽ sử dụng, các tài nguyên nào nên được cung cấp và nhiều chi tiết cấu hình khác. 

Xét về cơ sở hạ tầng, có rất ít thay đổi với cách ta quản lý container. Quyền kiểm soát container chỉ xảy ra ở một cấp độ cao hơn, giúp kiểm soát tốt hơn mà không cần phải quản lý vi mô từng container hay node riêng biệt.

Công việc của ta liên quan đến việc cấu hình Kubernetes, xác định node, pod và container bên trong chúng. Còn Kubernetes sẽ xử lý việc sắp xếp các container.

Ta có thể tự do lựa chọn nơi sử dụng Kubernetes. Có thể là trên bare metal server, máy ảo, nhà cung cấp public cloud/private cloud hay môi trường hybrid cloud. Một trong những ưu điểm chính của Kubernetes là nó có thể hoạt động trên nhiều cơ sở hạ tầng khác nhau.

## Những khái niệm cơ bản trong Kubernetes

Một số thuật ngữ phổ biến của Kubernetes bao gồm

### Pod

Pod là đơn vị nhỏ nhất để schedule, deploy và cô lập runtime của một hoặc nhiều container liên quan tới nhau. Các container trong cùng một pod sẽ luôn được schedule trên cùng một node và cùng nhau chia sẻ tài nguyên. Nếu node đó đột nhiên dừng hoạt động, các Pod nằm trên Node đó sẽ được schedule lại trên một Node khác trong Cluster. Application của bạn sẽ chạy trong Pod, nhưng thực tế bạn sẽ không truy cập trực tiếp vào Pod mà thay vào đó sẽ sử dụng một object khác gọi là Service

Hiểu đơn giản, Pod là 1 cấp độ cao hơn của Container, nó thể chứa nhiều container cùng xử lý 1 loại công việc. Các container sẽ có chung một địa chỉ IP, chia sẻ cùng 1 volume

### Node

Node là thành phần của phần cứng. Một node có thể là một máy ảo host bởi nhà cung cấp cloud, hay là một máy vật lý trong các data center. Tuy nhiên, để nghĩ về node một cách đơn giản hơn, ta có thể xem nó như các tài nguyên CPU/RAM được sử dụng bởi Kubernetes cluster, thay vì chỉ là các máy đơn lẻ. Sở dĩ vì các pod không bị giới hạn với bất kỳ máy nhất định nào, tại mọi thời điểm. Do đó, chúng sẽ di chuyển trên tất cả tài nguyên có sẵn để đạt được trạng thái mong muốn của ứng dụng.

Có 2 loại node khác nhau là **worker** và **master**:
- **Master node:** đóng vai trò là control của cụm cluster, máy điều khiển các kubernetes node. Đây là nơi tất cả các nhiệm vụ được giao
- **Worker node:** các máy này thực hiện các tác vụ được yêu cầu, là nơi khởi chạy trực tiếp của các ứng dụng, Kubernetes master điều khiển chúng

### Cluster

Các cluster chạy các ứng dụng nằm trong container do Kubernetes quản lý. Một cluster là một chuỗi các node được liên kết với nhau.

Bằng cách kết hợp với nhau, những node này có thể tổng hợp tài nguyên của chúng. Từ đó làm cho cluster mạnh hơn nhiều so với những máy riêng lẻ. Kubernetes di chuyển các pod xung quanh cluster khi những node được thêm hay xóa

Một cluster có thể chứa nhiều node worker, và phải có ít nhất một node master

### Services

Các Pod sẽ có IP, hostname riêng chứa các container của ứng dụng. Client có thể kết nối đến các Pod để tương tác bằng IP hay hostname tương ứng. Tuy nhiên, có một vấn đề là các Pod có thể bị crash hay lỗi bất ngờ, khi Replication Controller tạo lại Pod mới thay thế thì các thông số như địa chỉ IP, hostname cũng thay đổi. Hơn nữa một ứng dụng triển khai trên Kubenetes có nhiều Pod chạy cùng lúc, client không nên và cũng không cần thiết lưu trữ 1 tá các địa chỉ IP, hostname của các Pod

Do đó Kubernetes Service ra đời cho phép tạo một điểm truy cập duy nhất đến các Pod cung cấp cùng 1 dịch vụ. Mỗi Service có địa chỉ IP và port không đổi. Client có thể mở các kết nối đến IP và port của service, sau đó chúng sẽ được điều hướng đến các Pod để xử lý

### Replication Controller

Trong thực tế, các Pod khi được chạy trên các cluster Kubernetes hoàn toàn có thể bị lỗi, đột tử với nhiều lý do khác nhau. Với Replication Controller, nó sẽ đảm bảo tạo lại Pod mới thay thế khi Pod cũ lỗi (hay các node cũ lỗi). Một cách đầy đủ hơn, Replication Controller sẽ duy trì số Pod đang chạy với số lượng được chỉ định trước (ít hơn thì tạo thêm pod mới, thừa thì xóa bớt pod đi)

### ReplicaSets

ReplicaSets trong Kubernetes cũng có vai trò tương tự như ReplicationController, nói chính xác hơn thì ReplicaSets được giới thiệu nhằm thay thế ReplicationController

### Deployment

Deployment quản lý một nhóm các Pod - các Pod được nhân bản, nó tự động thay thế các Pod bị lỗi/không phản hồi bằng Pod mới nó tạo ra. Như vậy, deployment đảm bảo ứng dụng của bạn có một (hay nhiều) pod để phục vụ các yêu cầu

Từ trước đến nay, thành phần đầu tiên cần phải khởi tạo trong một hệ thống Kubernetes không gì khác là Pod. Và như chúng ta đã biết, để quản lý trạng thái của các Pod thì cần tạo thêm các Replication Controller để quản lý các Pod đó, thao tác khá cồng kềnh. Và hãy tưởng tượng ở một hệ thống lớn đến hàng trăm, ngàn Pod thì việc tạo ReplicationController để quản lý Pod/label sẽ rất tốn công

Kubernetes giới thiệu Deployment giúp đơn giản hóa quá trình trên. Với Deployment, chúng ta chỉ cần định nghĩa cấu hình và tạo 1 Deployment thì hệ thống sẽ tự động tạo ra 1 hay nhiều Pod tương ứng và ReplicaSet để quản lý trạng thái của Pod. 

Ngoài ra, Deployment còn có cơ chế giúp người quản lý hệ thống dễ dàng cập nhật, rollback phiên bản của ứng dụng (phiên bản container chạy trong các Pod)

### Kubeadm

Kubeadm là một công cụ cài đặt khởi động nhanh dành cho Kubernetes

Nó giúp tạo một cluster khả thi tối thiểu, với một master node duy nhất, Kubeadm rất nhanh và dễ sử dụng. Thêm vào đó, nó đảm bảo các cluster tuân theo những phương pháp tốt nhất. Do đó, Kubeadm là một công cụ tuyệt vời với những người mới sử dụng Kubernetes. Ngoài ra, ta cũng có thể dùng Kubeadm trong việc kiểm thử các ứng dụng

### Minikube

Minikube là một phiên bản nhẹ hơn của Kubernetes. Đồng thời nó cũng dễ sử dụng nội bộ hơn. Nó sẽ tạo một máy ảo (VM) trên máy cục bộ, tại đó ta có thể chạy một single-node cluster. Việc này cũng rất hữu ích cho việc thử nghiệm

### Label

Label cung cấp metadata nhận dạng cho các object trong Kubernetes. Label cho phép người dùng tổ chức và nhóm các object trong Cluster. Mỗi object có nhiều Label và mỗi Label có thể được gán cho nhiều object khác nhau. Người dùng có thể sử dụng Label để lọc được các đối tượng trong Cluster một cách dễ dàng

Tác dụng của Label là hỗ trợ người quản trị trong việc quản lý các Pod

### Desired state và Declarative model

**Desired state**: trạng thái mong muốn là một đặc tả của hệ thống hoặc ứng dụng mà bạn muốn đạt được. Trong Kubernetes, bạn sẽ định nghĩa trạng thái mong muốn của ứng dụng thông qua các đối tượng như Deployments, Services, ConfigMaps và Secrets. Kubernetes sẽ sau đó cố gắng đạt được trạng thái này bằng cách tạo, cập nhật hoặc xóa các tài nguyên liên quan.

**Declarative Model**: mô hình khai báo là phương pháp dùng để định nghĩa trạng thái mong muốn của hệ thống hoặc ứng dụng mà không cần chỉ định cách thức thực hiện. Thay vì chỉ rõ từng bước để đạt được mục tiêu, bạn chỉ cần mô tả trạng thái cuối cùng mà bạn muốn hệ thống đạt được. Khi sử dụng Kubernetes, bạn sẽ tạo ra các tệp YAML hoặc JSON để mô tả trạng thái mong muốn của ứng dụng theo mô hình khai báo. Ví dụ, để triển khai một ứng dụng web với 3 bản sao (replica), bạn tạo 1 file YAML với cấu hình replicas là 3, như vậy khi áp dụng file YAML này vào hệ thống, Kubernetes sẽ tự động điều chỉnh (thông qua kubectl) số pod để đạt được 3 như mong muốn.

Ưu điểm của mô hình khai báo này là đơn giản hóa quá trình quản lý ứng dụng, giảm thiểu lỗi và tăng tính tự động hóa. Hơn nữa, Kubernetes sẽ tiếp tục giám sát trạng thái hiện tại của ứng dụng và tự động điều chỉnh khi cần thiết.

## Khái niệm về master node và các thành phần

Master node là nơi đảm nhiệm tất cả các tác vụ quản trị chịu trách nhiệm quản lý cụm Kubernetes. Có thể có nhiều hơn một node chính trong cụm để tăng khả năng chịu lỗi. Việc có nhiều hơn một node master giúp cụm Kubernetes có tính sẵn sàng cao

Các thành phần trong master Node:
- **API-server:** Kubernetes API là thành phần quản lý trung tâm nhận tất cả các yêu cầu REST để sửa đổi (đối với pod, service, bộ sao chép / bộ điều khiển và những thứ khác), đóng vai trò là giao diện người dùng cho cụm. Ngoài ra, đây là thành phần duy nhất giao tiếp với cụm etcd, đảm bảo dữ liệu được lưu trữ trong etcd và phù hợp với chi tiết dịch vụ của các pod được triển khai
- **Etcd:** là một kho lưu trữ giá trị khóa phân tán, đơn giản được sử dụng để lưu trữ dữ liệu cụm Kubernetes (chẳng hạn như số lượng pod, trạng thái của chúng, namespace,...), các API object và chi tiết service discovery. Nó chỉ có thể truy cập được từ API Server vì lý do bảo mật. etcd bật thông báo cho cụm về các thay đổi cấu hình với sự trợ giúp của những watcher. Thông báo là các yêu cầu API trên mỗi node của cụm etcd để kích hoạt cập nhật thông tin trong bộ nhớ của node
- **Kube Controller Manage:** là một tập hợp các controller khác nhau để theo dõi các cập nhật trạng thái của Kubernetes Cluster thông qua API và thực hiện các thay đổi đối với Cluster sao cho phù hợp
- **Cloud Controller Manager:** là một tập hợp các logic dành riêng cho Cloud Provider (GCP, AWS, Azure) cho phép bạn liên kết Kubernetes Cluster với API của Cloud Provider. Nếu bạn đang sử dụng Kubernetes on-premises hoặc môi trường dev trên máy tính cá nhân, thì mặc định Cluster sẽ không có Cloud Controller Manager
- **Scheduler:** giúp lập lịch các pod trên các node khác nhau dựa trên việc sử dụng tài nguyên. Nó đọc các yêu cầu hoạt động của dịch vụ và lên lịch trên node phù hợp nhất. Ví dụ: nếu ứng dụng cần 1GB bộ nhớ và core CPU thì các nhóm cho ứng dụng đó sẽ được lên lịch trên một node có tài nguyên phù hợp. Bộ lập lịch chạy mỗi khi có nhu cầu lập lịch nhóm. Bộ lập lịch phải biết tổng tài nguyên hiện có cũng như tài nguyên được phân bố cho khối lượng công việc hiện có trên mỗi node

## Khái niệm về Worker Node và các thành phần

Nó là một máy chủ hay bạn có thể nói là một máy ảo chạy các ứng dụng sử dụng các Pod được điều khiển bởi node Master. Trên node worker, các pod được lập lịch. Để truy cập các ứng dụng từ thế giới bên ngoài, chúng ta kết nối với chúng qua các node

Các thành phần trong Worker Node:
- **Kube-proxy:** chạy trên tất cả các node trong cluster, kube-proxy có trách nhiệm quản lý network policy trên mỗi node và chuyển tiếp hoặc lọc traffic tới node dựa trên các policy này
- **Kubelet:** là service chính trên mỗi node, thường xuyên nhận các thông số của pod mới hoặc được sửa đổi (chủ yếu thông qua kube-apiserver) và đảm bảo rằng các pod và container của chúng không có vấn đề gì và chạy ở trạng thái mong muốn. Thành phần này cũng báo cáo cho master về tình trạng của node nơi mà nó đang chạy

## Tại sao nên sử dụng Kubernetes?

Kubernetes có thể giúp ta phân phối, quản lý các ứng dụng được chứa trong container, được kế thừa, cloud-native, cũng như những ứng dụng được tái cấu trúc thành microservices

Để đáp ứng nhu cầu kinh doanh đang ngày càng biến động, các nhóm developer cần có khả năng nhanh chóng build những ứng dụng và dịch vụ mới. Quá trình phát triển cloud-native bắt đầu bằng những microservices trong container. Chúng cho phép ta develop nhanh hơn, dễ dàng chuyển đổi cũng như tối ưu hóa các ứng dụng hiện có

Các ứng dụng sản xuất có trên rất nhiều container, và những container này phải được deploy trên nhiều server host. Kubernetes cho ta khả năng điều phối và quản lý cần thiết để deploy các container cho những workload này

Việc điều phối Kubernetes cho phép ta build những ứng dụng và dịch vụ mới. Quá trình phát triển cloud-native bắt đầu bằng những microservices trong container. Chúng cho phép ta develop nhanh hơn, dễ dàng chuyển đổi cũng như tối ưu hóa các ứng dụng hiện có

Các ứng dụng sản xuất có trên rất nhiều container, và những container này phải được deploy trên nhiều server host. Kubernetes cho ta khả năng điều phối và quản lý cần thiết để deploy các container cho những workload này

Việc điều phối Kubernetes cho phép ta build những dịch vụ ứng dụng trải rộng trên nhiều container. Đồng thời cũng có thể lên lịch cho các container đó trên một cluster, chia tỉ lệ container, quản lý tình trạng theo thời gian. Ngoài ra, sử dụng Kubernetes cũng giúp cải thiện đáng kể bảo mật.

Thêm vào đó, Kebernetes cũng cần được tích hợp networking, storage, security, telemetry và nhiều dịch vụ khác để cung cấp cơ sở hạ tầng container toàn diện nhất

Khi mở rộng sang một môi trường sản xuất cần nhiều ứng dụng, chắc chắn ta cần có nhiều container làm việc cùng nhau để có thể cung cấp những service riêng lẻ

Linux container cung cấp các ứng dụng microservice-based một đơn vị triển khai ứng dụng lý tưởng. Cùng với đó là một môi trường thực thi khép kín (self-contained). Ngoài ra, các microservice trong container cũng giúp việc điều phối dịch vụ dễ dàng hơn. Trong đó gồm cả lưu trữ, networking và bảo mật

Việc này sẽ làm tăng đáng kể số lượng container trong môi trường. Và từ đó dẫn đến độ phức tạp cũng tăng theo. Tuy nhiên Kubernetes đã khắc phục rất nhiều vấn đề phổ biến liên quan đến việc này. Cụ thể, Kubernetes phân loại những container này thành các pods. Các pod này sau đó sẽ thêm một lớp trừu tượng vào những container này. Từ đó ta có thể lên lịch các workload và cung cấp những dịch vụ cần thiết, chẳng hạn như networking hay lưu trữ cho các container này

Các phần khác của Kubernetes cũng giúp cân bằng tải trên những pod này. Đồng thời đảm bảo số lượng container phù hợp để hỗ trợ workload của mình

## So sánh giữa Kubernetes và Docker Swarm

Người dùng thường hay so sánh Kubernetes với Docker, tuy nhiên việc này không hẳn là chính xác. Nói đúng hơn, ta nên so sánh Kubernetes với Docker Swarm - vì đây là hai công nghệ container tương đương nhau. Trong đó, Docker Swarm là giải pháp điều phối container của Docker, Inc.

Swarm được tích hợp chặt chẽ với hệ sinh thái Docker và có API của riêng nó. Sự tích hợp này chính là một trong những lợi thế của Swarm so với Kubernetes. Sở dĩ vì việc chuyển đổi từ Docker sang Swarm là rất đơn giản. Còn Kubernetes thì sở hữu GUI riêng, được lựa chọn bởi những người dùng thích sử dụng GUI hơn CLI.

Nói về công cụ, Kubernetes chiếm ưu thế vì có bộ công cụ phong phú hơn. Ngoài ra còn có thể được mở rộng và tùy chỉnh nhiều hơn so với Swarm, đặc biệt khi nói đến việc giám sát hệ thống và auto-scaling

Nhìn chung, Swarm được xem là một giải pháp đơn giản hơn, dễ bắt đầu hơn và chủ yếu phù hợp cho việc phát triển. Còn K8s thì không bị ràng buộc với Docker, hỗ trợ các quy trình làm việc phức tạp hơn. Bên cạnh đó, Kubernetes cũng phổ biến hơn so với Swarm trong các môi trường sản xuất.