# Đôi nét về Container và Docker

## Container

**Đặt vấn đề:** Những vấn đề phát sinh liên quan đến sự phụ thuộc của phần mềm vào môi trường của hệ thống khi chuyển giao sản phẩm, ứng dụng là rất lớn -> Cần giải pháp giảm thiểu rủi ro này

Container là giải ảo hóa, giúp giải quyết vấn đề làm sao để chuyển giao phần mềm một cách đáng tin cậy (không phát sinh lỗi) giữa các môi trường máy tính khác nhau. Chẳng hạn như giữa máy tính của lập trình viên với máy của tester, giữa môi trường staging (môi trường tiền thực tế) với môi trường thực tế hay thậm chí giữa máy chủ riêng đặt tại trung tâm dữ liệu với máy ảo trên Cloud

Container giải quyết vấn đề trên bằng cách tạo ra một môi trường bị cô lập (isolated) chứa mọi thứ mà phần mềm cần để có thể chạy được bao gồm mã nguồn, các thư viện runtime, các thư viện hệ thống, các công cụ hệ thống,... (gọi là sự phụ phuộc hoặc các phụ thuộc) mà không bị các yếu tố liên quan đến môi trường hệ thống làm ảnh hưởng tới cũng như không làm ảnh hưởng tới các phần còn lại của hệ thống

Thông thường các container cho người dùng sự cải thiện về hiệu suất. Bằng cách tránh các hệ điều hành riêng biệt và thay vì sử dụng một share core, người dùng có thể tối đa hóa CPU, dung lượng lưu trữ và hiệu quả bộ nhớ

## Docker

Docker là bộ công cụ cho phép users tạo container images, đẩy hoặc kéo images từ các registries bên ngoài, chạy và quản lý container trong nhiều môi trường khác nhau

Docker là một ứng dụng mã nguồn mở cho phép đóng gói các ứng dụng, các phần mềm phụ thuộc lẫn nhau vào trong cùng một container. Container này sau đó có thể mang đi triển khai trên bất kỳ một hệ thống Linux phổ biến nào. Các container này hoàn toàn độc lập với các container khác nhưng đều dùng chung một số bin/lib và kernel của Host OS

Docker có 2 phiên bản phổ biến:
- Docker Community Edition (CE): là phiên bản miễn phí và chủ yếu dựa vào các sản phẩm nguồn mở khác
- Docker Enterprise (EE): phiên bản dành cho các doanh nghiệp, khi sử dụng phiên bản này sẽ nhận được sự support của nhà phát hành, ngoài ra còn có thêm các tính năng quản lý và bảo mật

Các thành phần của Docker Engine:
- **Docker Daemon:** chạy trên host, đóng vai trò là server, nhận các RESTful request từ Docker Client và thực thi nó. Là một lightweight runtime giúp build, run và quản lý các container và các thành phần liên quan khác
- **Docker Client (CLI):** cung cấp giao diện dòng lệnh cho người dùng, đồng thời cũng gửi request đến Docker daemon
- **Docker Registry:** Nơi lưu trữ Docker image. Docker Hub là một registry công khai mà bất cứ ai cũng có thể sử dụng và Docker được cấu hình để tìm kiếm image trên Docker Hub theo mặc định. Bạn thậm chí có thể chạy registry riêng của mình. Có 2 loại registry là public và private registry

Storage trong Docker là một tính năng quản lý data của Docker. Data ở đây có thể hiểu là các file được sinh ra trong quá trình chạy ứng dụng, ví dụ như log, data, report,...

Docker Storage có 3 option là volumes, bind mounts, tmpfs mounts. Tùy vào nhu cầu mà chúng ta có thể sử dụng option phù hợp với ngữ cảnh của mình:
- **Volumes:** mount-point nằm ở /var/lib/docker/volumes/ của Docker Host và được quản lý bằng Docker
- **bind mounts:** mount-points có thể nằm ở bất kỳ đâu trong Docker Host mà không bị quản lý bởi Docker
- **tmpfs mounts:** data sẽ được lưu vào memory của Docker Host và sẽ mất đi khi khởi động lại hoặc stop container

**Các thuật ngữ hay gặp trong Docker:**
- **Docker Image:** một Docker Image là một read-only template dùng để tạo ra các containers. Image được cấu tạo theo dạng layer và tất cả các layer đều là read-only. Một image có thể được tạo ra dựa trên một image khác với một số tùy chỉnh bổ sung. Nói ngắn gọn, Docker image là nơi lưu trữ các cài đặt môi trường như OS, package, phần mềm cần chạy
- **Dockerfile:** là một dạng file text không có phần đuôi mở rộng, chứa các đặc tả về một trường thực thi phần mềm, cấu trúc cho Docker image. Từ những câu lệnh đó, Docker sẽ build ra Docker image
- **Docker Container:** được tạo ra từ Docker Image, là nơi chứa mọi thứ cần thiết để có thể chạy ứng dụng. Là ảo hóa nhưng container lại rất nhẹ, có thể coi như là một process của hệ thống. Chỉ mất vài giây để start, stop hoặc restart một Container. Với một máy chủ vật lý, thay vì chạy được vài cái máy ảo truyền thống thì ta có thể chạy được vài chục, thậm chí vài trăm cái Docker container
- **Docker Network:** có nhiệm vụ cung cấp private network (VLAN) để các container trên một host có thể liên lạc được với nhau, hoặc các container trên nhiều hosts có thể liên lạc được với nhau
- **Docker Volume:** là cơ chế tạo và sử dụng dữ liệu của Docker, có nhiệm vụ lưu trữ dữ liệu độc lập với vòng đời của container
- **Docker Compose:** là công cụ dùng để định nghĩa và run multi-container cho Docker application. Với compose bạn sử dụng YAML để config các services cho application của bạn. Sau đó dùng command để create và run từ những config đó. Cụ thể:
  - Khai báo app's environment trong Dockerfile
  - Khai báo các services cần thiết để chạy application trong file docker-compose.yml
  - Run docker-compose up để start và run app
- **Docker Hub:** gần tương tự như github nhưng dành cho DockerFile, Docker Images. Ở đây có những DockerFile, Images của người dùng cũng như những bản chính thức từ các nhà phát triển lớn như Google, Orcale, Microsoft,... Ngoài ra còn có Docker Hub cho phép quản lý các image với những câu lệnh giống như Github như push, pull,... để bạn có thể quản lý dễ dàng image của mình

**Các câu lệnh cơ bản trong Docker:**
- List các container đang chạy: ```docker ps```
- List tất cả các container trên máy chủ: ```docker ps -a```
- Tạo mới một container: ```docker create -itd centos``` (centos là tên của image)
- Khởi chạy 1 container: ```docker run -itd centos```
- Xóa container: ```docker rm my-container```
- Xóa container chưa stop: ```docker rm -f myc-ontainer```
- Xóa tất cả các container: ```docker rm -f $(docker ps -aq)
- Start, stop và restart container: ```docker start/stop/restart my-container```
- Kiểm tra log của container: ```docker logs my-container```
- Kiểm tra thông tin chi tiết của 1 container: ```docker inspect my-container```
- Hiển thị tài nguyên đang sử dụng của container: ```docker stats my-container```
- Hiển thị các port được map: ```docker port my-container```
- Hiển thị các thay đổi trong file system kể từ lúc khởi tạo container: ```docker diff my-container```
- Thực thi 1 lệnh trong container: ```docker exec my-container free -m```
- Tạo 1 image từ container đang chạy: ```docker container commit my-container my_new_image```
- Hiển thị danh sách image đang có: ```docker image ls```
- Tải 1 image từ registry về máy chủ: ```docker image pull centos```
- Upload 1 image lên registry ```docker image push quyenbx/nginx_apache:1.0``` (trong đó quyenbx là tên tài khoản dockerhub, nginx_apache là tên image local, 1.0 là tag gán cho image)
- Lưu image thành 1 file nén: ```docker image save -o /mnt/ten_image_file.tar ten_image```
- Tạo lại image từ file nén image: ```docker image load -i my_image_file.tar```
- Xóa image: ```docker image rm my_image```

