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
|:-|:-|:-|
|$GITLAB_HOME/data|/var/opt/gitlab|Lưu trữ dữ liệu ứng dụng|
|$GITLAB_HOME/logs|/var/log/gitlab|Lưu trữ logs|
|$GITLAB_HOME/config|/etc/gitlab|Lưu trữ tệp cấu hình của GitLab|

## Installation

GitLab có thể được cài đặt bằng nhiều cách khác nhau: Docker Engine, Docker Compose, Docker swarm mode. Trong bài này sẽ sử dụng Docker Engine.

### Install Gitlab with Docker Engine

Để cài đặt Docker Engine, các bạn có thể tham khảo bài viết sau: [Cài đặt Docker Engine trên Ubuntu 22.04](https://wiki.nhanhoa.com/kb/cai-dat-docker-tren-ubuntu-22-04/)

Ta có thể điều chỉnh các đường dẫn dưới đây sao cho phù hợp với yêu cầu. Khi đã setup xong tham số ```GITLAB_HOME```, ta có thể chạy image:

```sh
sudo docker run --detach \
  --hostname gitlab.baotrung.xyz \
  --publish 443:443 --publish 80:80 --publish 22:22 \
  --name gitlab \
  --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab \
  --volume $GITLAB_HOME/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/data:/var/opt/gitlab \
  --shm-size 256m \
  gitlab/gitlab-ee:latest
```

Lệnh này sẽ download và khởi động GitLab container và công khai ports cân để truy cập SSH, HTTP, và HTTPS. Tất cả GitLab data sẽ được lưu trữ như subdirectories của ```$GITLAB_HOME```. Container sẽ tự động ```restart``` sau khi hệ thống reboot.

Nếu server của bạn sử dụng SELinux, chạy lệnh dưới đây:

```sh
sudo docker run --detach \
  --hostname gitlab.baotrung.xyz \
  --publish 443:443 --publish 80:80 --publish 22:22 \
  --name gitlab \
  --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab:Z \
  --volume $GITLAB_HOME/logs:/var/log/gitlab:Z \
  --volume $GITLAB_HOME/data:/var/opt/gitlab:Z \
  --shm-size 256m \
  gitlab/gitlab-ee:latest
```

Điều này sẽ đảm bảo tiến trình Docker có đủ permission để tạo tệp cấu hình trong volumes được mount.

Quá trình khởi tạo có thể tốn nhiều thời gian. Ta có thể kiểm tra bằng lệnh

```sh
sudo docker logs -f gitlab
```

Sau khi khởi động container, ta có thể truy cập ```gitlab.baotrung.xyz``` trên trình duyệt để truy cập ứng dụng. Tuy nhiên sẽ tốn 1 khoảng thời gian ngắn trước khi Docker container có thể phản hồi lại các truy vấn.

Truy cập Gitlab URL, đăng nhập với username ```root``` và password từ lệnh sau:

```sh
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

![](./images/K8s_Gitlab.png)