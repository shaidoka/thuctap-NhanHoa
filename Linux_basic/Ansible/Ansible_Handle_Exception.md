# Xử lý ngoại lệ trong Ansible Playbooks với block và rescue

Bạn đã bao giờ thực hiện playbook của mình trong Ansible và thấy rằng mình cần phải:
1. Xử lý lỗi hoặc thực hiện một phần tasks của bạn
2. Ghi lại tổng quan kết quả với mỗi host để xem lại sau này

Nếu bạn có Ansible Automation Platform, bạn có thể sử dụng những kỹ thuật như workflow job template trong Ansible để xử lý #1, và bạn sẽ cần module như ```set_stats``` cho #2 (để duy trì các biến giữa các nút workflow)

Trong bài viết này, mình sẽ giới thiệu về tính năng block/rescue của Ansible. 

## I. Block là gì?

Một block là 1 nhóm logic các tasks trong 1 playbook mà có thể thực thi như 1 đơn vị riêng lẻ. Điều này khiến việc quản lý các playbook phức tạp dễ dàng hơn bằng cách chia chúng thành các thành phần nhỏ, có thể quản lý được.

Bạn có thể sử dụng block để áp dụng tùy chọn vào 1 nhóm cá tasks, từ đó tránh việc lặp lại code. Ví dụ

```sh
tasks:
- name: Install, configure, and start Apache
  block: 
  - name: Install httpd and memcached
    yum:
      name:
      - httpd
      - memcached
      state: present

  - name: Apply the foo config template
    template:
      src: templates/src.j2
      dest: /etc/foo.conf

  - name: Start service bar and enable it
    service:
      name: bar
      state: started
      enabled: True
  when: ansible_facts['distribution'] == 'CentOS'
  become: true
  become_user: root
  ignore_errors: true
```

## II. Cách sử dụng block và rescue trong Ansible

Blocks và rescue kết hợp với nhau giúp ta có thể xử lý lỗi trong Ansible. Sử dụng rescue keyword cùng với 1 block để định nghĩa 1 tập hợp các tasks mà sẽ thực thi nếu 1 lỗi xảy ra trong block. Bạn có thể sử dụng rescue tasks để xử lý lỗi, log messages, hoặc thực hiện hành động khác để khôi phục từ lỗi gặp phải.

Ví dụ:

```sh
- hosts: <hosts>
  tasks:
  - block:
    - <task1>
    - <task2>
    - <task3>
    rescue:
    - <rescue_task1>
    - <rescue_task2>
    - <rescue_task3>
    always:
    - <always_task>
```

Bạn định nghĩa tasks bên dưới **block** keyword, hoặc bạn có thể kết hợp nhiều tasks lại với nhau và bao gồm vào đó nhiều role.

Rescue keyword là nơi mà lệnh thực thi playbook sẽ được gửi, cho mỗi host, nếu có bất kỳ lỗi nào trong block.

Cuối cùng, phần **always** thực thi với tất cả các node, không quan trọng nếu chúng thành công hay không.

Ý tưởng của cấu trúc này là:
1. **rescue** và **always** là các tính năng tùy chọn, mình sử dụng chúng cho mục đích trình bày về logic "khôi phục và tóm tắt".
2. Khi playbook chạy với số lượng host đáng kể, xử lý kết quả cho từng host sẽ khó hơn rất nhiều. Đó là lý do mà ý tưởng này được đưa ra.

Ví dụ:

```sh
- name: Test block/rescue
  hosts: nodes
  gather_facts: false
  tasks:
  - name: Main block
    block:
    - name: Role 1
      include_role:
        name: role1
    
    - name: Role 2
      include_role:
        name: role2

    - name: Accumulate success
      set_fact:
        _result:
          host: "{{ inventory_hostname }}"
          status: "OK"
          interfaces: "{{ ansible_facts['interfaces'] }}"
    
    rescue:
    - name: Accumulate failure
      set_fact:
        _result:
          host: "{{ inventory_hostname }}"
          status: "FAIL"
    
    always:
    - name: Tasks that will always run after the main block
      block: 
      - name: Collect results
        set_fact:
          _global_result: "{{ (_global_result | default([])) + [hostvars[item]['_result']] }}"
          loop: "{{ ansible_play_hosts }}"

      - name: Classify results
        set_fact:
          _result_ok: "{{ _global_result | selectattr('status', 'euqalto', 'OK') | list }}"
          _result_fail: "{{ _global_result | selectattr('status', 'equalto', 'FAIL') | list }}"
    
      - name: Display results OK
        debug:
          msg: "{{ _result_ok }}"
        when: (_result_ok | length ) > 0

      - name: Display results FAIL
        debug:
          msg: "{{ _result_fail }}"
        when: (_result_fail | length ) > 0
      delegate_to: localhost
      run_once: true
```

Trong ví dụ trên:
- Main block không hề làm gì cả, mình chỉ ví dụ rằng bạn sẽ đưa vào đó những công việc cụ thể sau. Nếu 1 node thành công, sẽ có tham số ```interfaces``` trong biến ```_result```, còn nếu thất bại thì không.
- Với mỗi host: Nếu hành động thực hiện mà không có lỗi, task "Accumulate success" sẽ thực thi, nếu bất kể role nào lỗi, rescue block sẽ thực thi với host đó.
- Phần **always** thu thập kết quả và lưu vào biến ```_result```:
   - Lúc này, mỗi host đều có biến trong cấu trúc **hostvars** của nó
   - Trong task **Collect results**, nó thu thập kết quả và thêm nó vào danh sách ```_global_result```
   - Vòng lặp được thực hiện bởi biến ```ansible_play_hosts_all```, chứa 1 danh sách các host được thực hiện trong playbook này
   - **Classify result** thực hiện 1 vài filter để tạo 1 list host OK và FAIL.

Dưới đây là 1 ví dụ về kết quả của playbook này

```sh
PLAY [Test block/rescue] *******************************************************

TASK [Role 1] ******************************************************************

TASK [role1 : Execution of role 1] *********************************************
ok: [node1] => {
    "changed": false,
    "msg": "All assertions passed"
}
fatal: [node2]: FAILED! => {
    "assertion": "inventory_hostname in nodes_ok",
    "changed": false,
    "evaluated_to": false,
    "msg": "Assertion failed"
}
fatal: [node3]: FAILED! => {
    "assertion": "inventory_hostname in nodes_ok",
    "changed": false,
    "evaluated_to": false,
    "msg": "Assertion failed"
}

TASK [Role 2] ******************************************************************

TASK [role2 : Execution of role 2] *********************************************
ok: [node1]

TASK [role2 : Show network information] ****************************************
skipping: [node1]

TASK [Accumulate success] ******************************************************
ok: [node1]

TASK [Accumulate failure] ******************************************************
ok: [node2]
ok: [node3]

TASK [Collect results] *********************************************************
ok: [node1 -> localhost] => (item=node1)
ok: [node1 -> localhost] => (item=node2)
ok: [node1 -> localhost] => (item=node3)

TASK [Classify results] ********************************************************
ok: [node1 -> localhost]

TASK [Display results OK] ******************************************************
ok: [node1 -> localhost] => {
    "msg": [
        {
            "host": "node1",
            "interfaces": [
                "enp7s0",
                "enp1s0",
                "lo"
            ],
            "status": "OK"
        }
    ]
}

TASK [Display results FAIL] ****************************************************
ok: [node1 -> localhost] => {
    "msg": [
        {
            "host": "node2",
            "status": "FAIL"
        },
        {
            "host": "node3",
            "status": "FAIL"
        }
    ]
}

PLAY RECAP *********************************************************************
node1   : ok=7    changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
node2   : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=1    ignored=0   
node3   : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=1    ignored=0
```

## III. Tổng kết

Mình mong rằng bài viết này đã cho các bạn 1 vài ý tưởng về cách Ansible xử lý ngoại lệ trong playbook

Bạn có thể cũng có thể nghĩ về 1 vài hành động bạn muốn trong rescue section, như hiển thị 1 tin nhắn nào đó hay 1 công việc "undo" chẳng hạn.

Cuối cùng, bạn có thể thực thi **always** section với mỗi host, như trong ví dụ của mình.