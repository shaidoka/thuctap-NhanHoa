# Building Octavia Amphora Images

## Prerequisites

Python pip và các module trong file ```requirements.txt``` cần phải được cài đặt, hãy thực hiện các lệnh sau đây:

```sh
git clone https://opendev.org/openstack/octavia.git
yum -y install python-pip python-virtualenv
virtualenv octavia_disk_image_create
source octavia_disk_image_create/bin/activate
cd octavia/diskimage-create
pip install -r requirements.txt
```

Cache directory của bạn cần có ít nhất 1GB dung lượng, working directory sẽ cần 1.5GB, và image destination cần khoảng 500MB.

Script này sẽ sử dụng phiên bản diskimage-builder được cài đặt trên hệ thống của bạn hoặc nó có thể được overridden bằng cách khai báo biến môi trường như thế này:

```sh
DIB_REPO_PATH = /<some directory>/diskimage-builder
DIB_ELEMENTS = /<some directory>/diskimage-builder/elements
```

Cài đặt các gói cần thiết:

Trong **CentOS 7**

```sh
yum install qemu-img git e2fsprogs policycoreutils-python-utils -y
```

Trong **Ubuntu**

```sh
apt install qemu-utils git kpartx debootstrap -y
```

### Test Prerequisites

Trong bài này chúng ta sẽ sử dụng ```tox``` image test, và nó yêu cầu ```libguestfs-tools``` phiên bản 1.24 hoặc mới hơn. Libguestfs cho phép kiểm tra Amphora image mà không phải có root privileges. Trên Ubuntu systems, bạn cũng cần cấp quyền đọc kernels cho user mà thực hiện tests:

```sh
sudo chmod 0644 /boot/vmlinuz*
```

## Usage

Lưu ý là nếu cloud của bạn có nhiều cấu trúc phần cứng khác nhau cho nova, hãy cài đặt thuộc tính ```hw-architecture``` tương ứng trên image khi tải nó vào glance. Ví dụ, khi tải 1 amphora image sử dụng cho ```amd64```, bạn sẽ cần thêm ```--property hw_architecture='x86_64'``` vào lệnh ```openstack image create```

Script này sẽ sử dụng biến môi trường để tùy chỉnh build ngoài những biến mặc định của Octavia project, chẳng hạn như adding elements.

Cú pháp lệnh:

```sh
$ diskimage-create.sh
        [-a **amd64** | armhf | aarch64 | ppc64le ]
        [-b **haproxy** ]
        [-c **~/.cache/image-create** | <cache directory> ]
        [-d **jammy**/**9-stream**/**9** | <other release id> ]
        [-e]
        [-f]
        [-g **repository branch** | stable/train | stable/stein | ... ]
        [-h]
        [-i **ubuntu-minimal** | fedora | centos-minimal | rhel | rocky ]
        [-k <kernel package name> ]
        [-l <log file> ]
        [-m]
        [-n]
        [-o **amphora-x64-haproxy** | <filename> ]
        [-p]
        [-r <root password> ]
        [-s **2** | <size in GB> ]
        [-t **qcow2** | tar ]
        [-v]
        [-w <working directory> ]
        [-x]
        [-y]

    '-a' is the architecture type for the image (default: amd64)
    '-b' is the backend type (default: haproxy)
    '-c' is the path to the cache directory (default: ~/.cache/image-create)
    '-d' distribution release id (default on ubuntu: jammy)
    '-e' enable complete mandatory access control systems when available (default: permissive)
    '-f' disable tmpfs for build
    '-g' build the image for a specific OpenStack Git branch (default: current repository branch)
    '-h' display help message
    '-i' is the base OS (default: ubuntu-minimal)
    '-k' is the kernel meta package name, currently only for ubuntu-minimal base OS (default: linux-image-virtual)
    '-l' is output logfile (default: none)
    '-m' enable vCPU pinning optimizations (default: disabled)
    '-n' disable sshd (default: enabled)
    '-o' is the output image file name
    '-p' install amphora-agent from distribution packages (default: disabled)
    '-r' enable the root account in the generated image (default: disabled)
    '-s' is the image size to produce in gigabytes (default: 2)
    '-t' is the image type (default: qcow2)
    '-v' display the script version
    '-w' working directory for image building (default: .)
    '-x' enable tracing for diskimage-builder
    '-y' enable FIPS 140-2 mode in the amphora image
```

## Building Images for Alternate Branches

Mặc định, ```diskimage-create.sh``` sẽ build 1 amphora image sử dụng Octavia Git branch của repository. Nếu bạn cần 1 image cho branch cụ thể, chẳng hạn như ```stable/train```, bạn cần chỉ định tùy chọn ```-g``` với tên branch. Ví dụ:

```sh
diskimage-create.sh -g stable/train
```

## Environment Variables

Tham khảo tại bài viết gốc: [Amphora Image](https://docs.openstack.org/octavia/latest/admin/amphora-image-build.html)

## Building in a virtualenv with tox

Để sử dụng virtualenv của Python, bạn có thể chạy ```tox```. Lưu ý rằng bạn vẫn cần phải cài đặt các phụ thuộc trên host để có thể build image.

Nếu bạn muốn tùy chỉnh build, hãy chỉnh sửa file ```tox.ini``` để truyền vào các biến môi trường hoặc đối số tương tự như sử dụng diskimage-create.sh

## Container Support

Lệnh Docker để import 1 tar file đã được tạo với script này là:

```sh
docker import - image:amphora-x64-haproxy < amphora-x64-haproxy.tar
```