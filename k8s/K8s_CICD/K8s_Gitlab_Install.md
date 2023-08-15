# GitLab Docker images

GitLab Docker images là monolithic image của GitLab mà chạy tất cả những dịch vụ cần thiết trong 1 container

Link Docker Hub: [Gitlab image](https://hub.docker.com/r/gitlab/gitlab-ee/)

Docker images không bao gồm 1 mail transport agent (MTA). Giải pháp khuyến khích là sử dụng 1 MTA bổ sung (như Postfix hay Sendmail) chạy trong 1 container riêng biệt. Một tùy chọn khác, ta có thể cài đặt MTA thẳng vào Gitlab container, nhưng điều này cũng làm tăng độ phức tạp khi bảo trì vì ta sẽ cần cài đặt lại MTA mỗi khi upgrade/restart

Trong ví dụ dưới đây, nếu ta muốn sử dụng RC image mới nhất, hãy sử dụng ```gitlab/gitlab-ee:rc```

Ta sẽ không muốn triển khai Gitlab Docker image trong K8s vì nó tạo 1 "single point of failure"

## Prerequisites

Điều kiện cần duy nhất là Docker cần được cài đặt.

## Set up the volumes location

Trước khi cài đặt bất kỳ điều gì, thiết lập 1 biến môi trường mới ```$GITLAB_HOME``` trỏ đến đường dẫn nơi mà cấu hình, logs, data files sẽ được đặt. Chắc chắn rằng đường dẫn đó tồn tại và có permission hợp lí.

```sh
export GITLAB_HOME=/srv/gitlab
```

GitLab container sử dụng volume được mount trên host để lưu trữ dữ liệu:

|Local location|Container localtion|Usage|
|$GITLAB_HOME/data|/var/opt/gitlab|Lưu trữ dữ liệu ứng dụng|
|$GITLAB_HOME/logs|/var/log/gitlab|Lưu trữ logs|
|$GITLAB_HOME/config|/etc/gitlab|Lưu trữ tệp cấu hình của GitLab|

## Cài đặt 

GitLab có thể được cài đặt bằng nhiều cách khác nhau: Docker Engine, Docker Compose, Docker swarm mode. Trong bài này sẽ sử dụng Docker Engine.

