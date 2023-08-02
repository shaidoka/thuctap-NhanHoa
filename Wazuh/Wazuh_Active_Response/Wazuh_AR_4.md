# Additional information

## White list

Ta có thể thiết lập 1 danh sách các địa chỉ IP mà sẽ không bao giờ bị chặn bởi active response bằng cách sử dụng trường ```white_list```. Nó cho phép thiết lập 1 địa chỉ IP, netblock, hoặc hostname. Dù vậy, ta vẫn phải định định chỉ 1 giá trị với mỗi thẻ ```<white_list>```, ta có thể sử dụng nhiều thẻ ```<white_list>``` để bao gồm nhiều giá trị

Để cấu hình 1 white list cho endpoint, thêm địa chỉ IP, netblock, hoặc hostname vào trường ```<white_list>``` ở phần ```global``` trong file ```/var/ossec/etc/ossec.conf``` trên Wazuh server:

```sh
<ossec_config>
  <global>
    <jsonout_output>yes</jsonout_output>
    <email_notification>no</email_notification>
    <logall>yes</logall>
    <white_list>1.2.3.4<white_list>
  </global>
</ossec_config>
```

Restart Wazuh manager

```sh
sudo systemctl restart wazuh-manager
```

## Tăng thời gian chặn cho những kẻ tái tấn công

Những kẻ tấn công thường sử dụng công cụ tự động tấn công, và chúng sẽ không quan tâm là có bị chặn hay không, bởi vậy mà việc tấn công sẽ lặp lại ngay khi Wazuh bỏ chặn những kẻ này. Thêm đoạn cấu hình sau vào file ```/var/ossec/etc/ossec.conf``` của Wazuh agent:

```sh
<ossec_config>
  <active-response>
    <repeated_offenders>10,20,30</repeated_offenders>
  </active-response>
</ossec_config>
```

**Lưu ý:** Tùy chọn này không khả dụng với Windows. Thời gian trong thẻ này có đơn vị phút, bất kể thẻ ```timeout``` có là giây đi chăng nữa. Cuối cùng, ta có thể chỉ định tối đa 5 giá trị cho thẻ này.

Restart agent

```sh
systemctl restart wazuh-agent
```

Có thể mô tả như thế này: lần đầu tiên active response trigger, nó chặn địa chỉ IP với thời gian chỉ định trong ```<timeout>```. Ở lần thứ 2 sẽ là 10 phút, lần 3 là 20 phút, và cứ như thế.

Sử dụng active response module, ta có thể đáp trả lại nhiều bối cảnh khác nhau như hạn chế hành vi khả nghi và ngăn chặn tấn công kịp thời. Cần cẩn thận khi sử dụng active response vì nó có thể khiến endpoint gặp phải những vulnerable không đáng có, vì vậy hãy tìm hiểu kỹ trước khi định nghĩa active response.