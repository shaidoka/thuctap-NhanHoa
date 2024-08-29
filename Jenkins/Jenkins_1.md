# Jenkins Pipeline

Trong series này, chúng ta sẽ tìm hiểu về các nội dung sau đây:

- Getting started with Pipeline: bao gồm cách định nghĩa 1 Jenkins pipeline qua Blue Ocean, classic UI
- Create and use a Jenkinsfile: bao gồm cách tạo và xây dựng Jenkinsfile cho từng trường hợp cụ thể
- Work with branches and pull requests
- Use Docker with Pipline: bao gồm cách Jenkins gọi Docker containers trên agents/nodes (từ Jenkinsfile) để xây dựng Pipeline
- Extend Pipeline with shared libraries
- Sử dụng các công cụ phát triển khác nhau để đơn giản hóa việc tạo Pipeline
- Work with Pipeline syntax: đây là các đường dẫn đến nơi mà bạn có thể tìm kiếm mọi thứ về cú pháp trong Pipeline

## What is Jenkins Pipeline?

Jenkins pipeline (hay đơn giản là "Pipeline" với chữ "P" viết hoa) là một bộ công cụ mà hỗ trợ bạn triển khai và tích hợp *continuous delivery pipelines* vào Jenkins.

1 *continuous delivery* là 1 cách biểu diễn tự động hóa của tiến trình mà ứng dụng của bạn được đưa đến người dùng từ các công cụ version control. Mọi thay đổi với ứng dụng của bạn sẽ được đưa vào 1 tiến trình phức tạp trước khi được thực sự phát hành. Tiến trình này liên quan đến xây dựng phần mềm mà đảm bảo tính tin cậy và có thể lặp lại, cũng như đưa phần mềm đã build qua nhiều strages kiểm thử và phát triển (testing and deployment).

Pipeline cung cấp 1 tập công cụ có thể mở rộng cho việc thiết kế delivery pipeline từ đơn giản đến phức tạp dưới dạng code thông qua **Pipeline domain-specific language (DSL) syntax**

Định nghĩa của 1 Jenkins Pipeline được viết thành 1 text file (gọi là Jenkinsfile) thứ mà có thể được lần lượt commit đến 1 project's source control repository. Đây là nền tảng của "Pipeline as code"; tức là coi CD pipeline như 1 phần của ứng dụng để có thể được "versioned" và "reviewed" như bất kỳ code nào khác.

Tạo 1 Jenkinsfile và commit nó vào source control sẽ giúp đem lại 1 số lợi ích như:

- Tự động tạo 1 Pipeline build process cho tất cả các branch và pull request
- Code review/iteration trên Pipeline (cùng với mã nguồn)
- Lưu vết xác thực cho Pipeline
- Tạo "Single source of truth" cho Pipeline, thứ mà có thể được xem và chỉnh sửa bởi nhiều thành viên của dự án

Mặc dù cú pháp để định nghĩa Pipeline của web UI và Jenkinsfile là như nhau, best practice là sử dụng Jenkinsfile và đưa nó vào source control.

## Declarative versus Scripted Pipeline syntax

1 Jenkinsfile có thể được viết sử dụng 2 loại syntax - Declarative và Scripted

Declarative và Scripted Pipelines được xây dựng về cơ bản là khác nhau. Declarative Pipeline là tính năng mới hơn của Jenkins Pipeline, thứ mà:

- Cung cấp cú pháp phong phú hơn