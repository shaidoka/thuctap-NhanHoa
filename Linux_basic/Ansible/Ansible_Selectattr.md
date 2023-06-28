# Thuộc tính selectattr trong playbook

Ansible cung cấp nhiều cách thức tuyệt vời để lọc dữ liệu, giúp người dùng viết ra những task hiệu quả và dễ dàng hơn. Trong số đó, mình sử dụng ```selectattr``` rất nhiều để lọc dữ liệu dạng danh sách dựa trên 1 vài thuộc tính nhất định.

Trong bài này, hãy cùng Nhân Hòa đi qua 1 vài ví dụ để hiểu cách sử dụng ```selectattr``` nhé.

## 1. Ví dụ 1 - Sử dụng bộ lọc selectattr

Playbook:

```sh
- name: Simple selectattr filter example
  hosts: localhost
  gather_facts: no
  vars:
    fruits:
    - name: apple
      color: red
    - name: banana
      color: yellow
    - name: cherry
      color: red

  tasks:
  - name: Display red fruits
    debug:
      msg: "{{ item.name }} is red."
    loop: "{{ fruits | selectattr('color', 'equalto', 'red') | list }}"
```

Kết quả:

```sh
PLAY [Simple selectattr Filter Example] *******************************

TASK [Display red fruits] *****************************************
ok: [127.0.0.1] => (item={'name': 'apple', 'color': 'red'}) => {
    "msg": "apple is red."
}
ok: [127.0.0.1] => (item={'name': 'cherry', 'color': 'red'}) => {
    "msg": "cherry is red."
}

PLAY RECAP ********************************************************
127.0.0.1                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Giải thích:
- ```loop: "{{ fruits | selectattr('color', 'equalto', 'red') | list }}"``` - dòng này định nghĩa 1 vòng lặp mà duyệt qua các phần tử là "fruits" có màu "đỏ"
- ```selectattr('color', 'equalto', 'red')``` - lọc danh sách đầu vào với tiêu chí là "color" và giá trị bằng "red"
- ```|``` - "pipe symbol", thường được sử dụng trong Linux để nối tiếp lệnh
- ```list``` - chuyển đổi đầu ra của bộ lọc trước đó của selectattr từ iterable object thành list object

## 2. Ví dụ 2 - Tạo 1 List mới

Playbook:

```sh
- name: Simple selectattr Filter Example
  hosts: localhost
  gather_facts: no
  vars:
    fruits:
      - name: apple
        color: red
      - name: banana
        color: yellow
      - name: cherry
        color: red

  tasks:
    - name: Create a list of red fruits
      set_fact:
        red_fruits: "{{ fruits | selectattr('color', 'equalto', 'red') | list }}"

    - name: Display red fruits
      debug:
        var: red_fruits
```

Kết quả:

```sh
PLAY [Simple selectattr Filter Example] **********************************

TASK [Create a list of red fruits] *******************************************
ok: [127.0.0.1]

TASK [Display red fruits] **********************************************
ok: [127.0.0.1] => {
    "red_fruits": [
        {
            "color": "red",
            "name": "apple"
        },
        {
            "color": "red",
            "name": "cherry"
        }
    ]
}

PLAY RECAP **************************************
127.0.0.1                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Trong ví dụ trên, ta sử dụng bộ lọc ```selectattr``` để tạo 1 danh sách gọi là ```red_fruits``` chứa thông tin về các trái cây có màu đỏ.

## 3. Ví dụ 3 - Tạo 1 list mới nhưng với thuộc tính tùy chọn

Playbook:

```sh
- name: Simple selectattr and map Filter Example
  hosts: localhost
  gather_facts: no
  vars:
    fruits:
      - name: apple
        color: red
      - name: banana
        color: yellow
      - name: cherry
        color: red

  tasks:
    - name: Create a list of red fruit names
      set_fact:
        red_fruit_names: "{{ fruits | selectattr('color', 'equalto', 'red') | map(attribute='name') | list }}"

    - name: Display red fruit names
      debug:
        var: red_fruit_names
```

Trong ví dụ này, ta sử dụng thêm bộ lọc ```map``` để lấy thông tin về "name" bằng cú pháp ```map(attribute='name')```.

Kết quả:

```sh
PLAY [Simple selectattr and map Filter Example] **********************************

TASK [Create a list of red fruit names] *************************************
ok: [127.0.0.1]

TASK [Display red fruit names] ******************************************
ok: [127.0.0.1] => {
    "red_fruit_names": [
        "apple",
        "cherry"
    ]
}

PLAY RECAP *********************************
127.0.0.1                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## 4. Tổng kết

Hy vọng qua bài viết này, các bạn có thể phần nào hiểu được cách thức sử dụng 1 công cụ rất thông dụng trong ansible playbook là ```selectattr```.