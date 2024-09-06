# Hướng dẫn xử lý manual evacuate compute

1. Login iDRAC, ILO vào node lỗi chụp lại màn hình console lúc lỗi --> Thực hiện Power Off

2. Kiểm tra lại các service nova trên compute lỗi off hoàn toàn

```sh
nova service-list
```

3. Thực hiện list ID các vm đang chạy trên compute bị lỗi ra file

```sh
for i in `openstack server list --all-project --host <failed_compute> | tail -n +4 | awk '{print $2}'`; do echo -e "$i" >> <filename>; done
 
for i in `openstack server list --all-project --host compute01 | tail -n +4 | awk '{print $2}'`; do echo -e "$i" >> evacuate-compute01; done
```

4. Thực hiện list các vm đang chạy trên compute bị lỗi và xuất ra file excel để kiểm soát --> thông báo cho sale

Truy cập Dashboard > Project admin > Tab Admin > Compute > Instances > Filter Hostname = <failed_host> > Copy toàn bộ vào excel

5. Thực hiện chạy host evacuate cho compute bị lỗi

```sh
nova host-evacuate <failed_compute>
 
nova host-evacuate compute01
```

6. Script mỗi 30s lấy trạng thái vm list 1 lần kèm thời gian --> lưu tên file theo tgian

```./check-status-30s.sh```
 
```sh
#/bin/bash
 
read -p "Input name of failed_host: " failed_host
vm_exist_failed_host=$(openstack server list --all-projects --host $failed_host --long --fit-width | grep -i "$failed_host" | wc -l)
 
while [ $vm_exist_failed_host -gt 0 ]
do
  openstack server list --all-projects --host $failed_host --long --fit-width | sed 1d | sed 2d | head -n -1 | tr "|" "," > /home/fcideploy/$failed_host-$(date +%H%M%S_%d%m%Y).csv
  sleep 30
done
 
echo "Progress Evacuate Host $failed_host Is Finished !!!"
```

7. Sau khi quá trình host evacuate hoàn tất, thực hiện chạy script kiểm tra trạng thái của các vm và vm đang ở host nào

```./final-report.sh```

```sh
#/bin/bash
 
read -p "Input full path file failed_host ID: " file_id
read -p "Input name of failed_host: " failed_host
 
list_id=$(cat $file_id)
 
count=0
 
echo -e "VM_NAME, PROJECT_NAME, HOST_NAME, STATUS, POWER_STATE, UPTIME" > /home/fcideloy/final-report_$failed_host-$(date +%d%m%Y).csv
for a in $list_id;
do
  vm_name=$(openstack server show $a | grep -i "\bname" | head -n 1 | cut -d "|" -f 3 | cut -d " " -f 2)
  host=$(openstack server show $a | grep -iE "OS-EXT-SRV-ATTR:host" | cut -d "|" -f 3 | cut -d " " -f 2)
  power_state=$(openstack server show $a | grep -i "power_state" | cut -d "|" -f 3 | cut -d " " -f 2)
  state=$(openstack server show $a | grep -i "status" | cut -d "|" -f 3 | cut -d " " -f 2)
  project_id=$(openstack server show $a | grep -iE "project_id" | cut -d "|" -f 3 | cut -d " " -f 2)
  project_name=$(openstack project list | grep -i "$project_id" | cut -d "|" -f 3 | cut -d " " -f 2)
  uptime=$(openstack server show $a | grep -i "updated" | cut -d "|" -f 3 | cut -d " " -f 2)
  let count+=1
  if [[ "$power_state" == "Running" ]]; then
    echo "$count - VM $vm_name Is Running"
    echo "$vm_name, $project_name, $host, $state, $power_state, $uptime" >> /home/fcideloy/final-report_$failed_host-$(date +%d%m%Y).csv
  else
    until [[ "power_state" == "Running" ]]
    do
      echo "$count - Checking VM $vm_name"
      sleep 10
    done
    echo "$vm_name, $project_name, $host, $state, $power_state, $uptime" >> /home/fcideloy/final-report_$failed_host-$(date +%d%m%Y).csv
  fi
done
```

8. Kiểm tra khi vm lên hoàn toàn trích xuất các file csv report để có tgian down time chính xác

```sh
<thời gian UPTIME file final-report> - <thời gian host down>
```