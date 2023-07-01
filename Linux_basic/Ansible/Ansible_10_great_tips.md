# Top 10 tips dành cho người dùng Ansible

Ansible làm cho việc tạo, chia sẻ, và quản lý tự động hóa dễ dàng hơn rất nhiều, nhưng cũng như bất kỳ công cụ nào, có vài lời tips giúp ta sử dụng Ansible tốt hơn nhiều.

## 1. Sử dụng version control

Sử dụng version control là 1 tiêu chuẩn của lập trình, và Ansible không phải ngoại lệ. Hãy chắc chắn là luôn giữ các playbook, role, inventory, và variable ở Git hoặc bất kỳ hệ thống version control nào khác.

## 2. Sử dụng khoảng trắng và comment

Ansible sử dụng YAML để viết playbook, và ký tự khoảng trắng được YAML dùng để định nghĩa cấu trúc document và đánh dấu sự lồng ghép.

Ví dụ:

```sh
foo: bar
  dah: dum
  lah:
    dee: dah
    dah: dee
```

Sẽ được dịch sang Python (bằng thư viện PyYAML) là:

```sh
foo: bar
dah: dum
lag: {'dee': 'dah', 'dah':'dee'}
```

Sử dụng dấu **comments** là 1 cách tốt để mô tả ý nghĩa của dòng code. Nhưng cố gắng đừng lạm dụng nó nhé! Trong YAML thì ta dùng ký tự ```#``` để comment

```sh
# Đây là comment
```

## 3. Đặt cho biến những cái tên có ý nghĩa

Đặt tên 1 biến bằng tên vai trò của chúng để tránh bị *lú* khi lâu lâu đọc lại code:

```sh
apache_max_keepalive: 25
apache_port: 80
tomcat_port: 8080
```

Thay vì:

```sh
max_keepalive: 25
port: 80
port: 8080
```

## 4. Sử dụng role để giúp playbook gọn hơn

Trong khi có rất nhiều cách để tổ chức nội dung trong playbook, 1 cách tốt hơn thảy đó là sử dụng **roles** trong Ansible. Chúng ta sẽ có 1 bài riêng để nói về **roles** sau, ví dụ đây là 1 cấu trúc thư mục sử dụng role:

```sh
site.yml
webservers.yml
fooservers.yml
roles/
    common/
        tasks/
        handlers/
        files/
        templates/
        vars/
        defaults/
        meta/
    webservers/
        tasks/
        defaults/
        meta/
```

## 5. Kiểm thử ansible playbook

Nếu bạn đang tìm kiếm 1 cách để kiểm thử playbook trước khi thực sự sử dụng nó, thì dưới đây là 1 vài cách để làm điều này:
- ```-vvvv```: kiểm tra kết nối
- ```--step```: ansible sẽ hỏi liệu bạn có muốn tiếp tục trước mỗi task
- ```--check```: ansible sẽ chỉ dự đoán kết quả khi chạy playbook chứ không thực hiện thay đổi nào cả
- ```--diff```: ansible sẽ cung cấp sự khác nhau giữa trước và sau play
- ```--start-at-task```: bắt đầu playbook ở 1 task chỉ định nào đó

## 6. Sử dụng cú pháp block

Cú pháp block đã được nhắc đến ở phần 11, nó giúp ta dễ dàng thiết lập dữ liệu hoặc chỉ thị cho 1 tập các task dùng chung mục đích. Cùng với đó là cho phép rollback khi gặp phải thay đổi nghiêm trọng.

```sh
tasks:
   - name: Install, configure, and start Apache
     block:
       - name: install httpd and memcached
         yum:
           name:
           - httpd
           - memcached
           state: present

       - name: apply the foo config template
         template:
           src: templates/src.j2
           dest: /etc/foo.conf
       - name: start service bar and enable it
         service:
           name: bar
           state: started
           enabled: true
     when: ansible_facts['distribution'] == 'CentOS'
     become: true
     become_user: root
     ignore_errors: yes
```

## 7. Sử dụng cấu trúc tệp inventory riêng cho môi trường staging và production

Bạn sẽ không muốn thực hiện các thay đổi thử nghiệm lên trên các server production đâu. Để tránh điều này, hãy sử dụng các tệp inventory tách biệt cho môi trường staging và production. Như thế này chẳng hạn:

```sh
|----inventories/   
|    |--dev/
|    |  |--group_vars/...
|    |  |--host_vars/...
|    |--prod/
|       |--group_vars/...
|       |--host_vars/
|            |--my_playbook_hostname_vars.yml
|----roles/...     
|----hosts.yml    
|----my_playbook.yml  
|
```

## 8. Hiểu về từ khóa ```serial```

Bạn có thể kiểm soát số lượng máy chủ được thực hiện cùng 1 lúc với từ khóa ```serial```. Mặc định, Ansible sẽ cố gắng quản lý tất cả hệ thống được sử dụng trong play đó song song với nhau. Tuy nhiên ta có thể chỉ định số lượng host thực hiện play đồng thời bằng từ khóa ```serial```

```sh
- name: test play
  hosts: webservers
  serial: 2
  gather_facts: False

  tasks:
    - name: task one
      command: hostname
    - name: task two
      command: hostname
```

## 9. Sử dụng modules đúng với mục đích

Mục đích của Ansible là khiến mọi thứ đơn giản và thuận tiện nhất có thể. Vì vậy khi bạn có thể sử dụng lệnh như ```command```, ```shell```, ```raw``` và ```script``` để thực hiện các hoạt động trên terminal, thì cũng đừng nên làm vậy. Hãy sử dụng module của ansible để thực hiện nó.

Ví dụ 1 service hoàn toàn có thể được restart bằng lệnh ```systemctl restart foo.bar``` thì hãy sử dụng module ```service``` của ansible để thay thế

```sh
- name: Restart service foo
  service:
    name: foo.bar
    state: restarted
```

## 10. Hạn chế debug quá nhiều

Trong khi debugging rất tiện dụng, debug module lại có thể khiến đầu ra khi chạy playbook bị lộn xộn. Ví dụ ta có thể debug ra chỉ khi playbook được chạy với ```verbosity``` là 3

```sh
- debug:
   msg: "I always display!"

- debug:
   msg: "I only display with ansible-playbook -vvv+"
   verbosity: 3
```

## Tổng kết

Có nhiều cách để sử dụng Ansible, trên đây chỉ là những tips mình rút ra trong quá trình làm việc với nó. Đừng coi đây là 1 tôn chỉ gì cả, hãy nghĩ đơn giản nó là 1 lời khuyên thôi.