# Tạo bản ghi DKIM cho tên miền trong mailserver Kerio

- ```Configuration``` -> ```Domains``` -> Chuột phải vào domain muốn tạo DKIM -> ```Edit``` 

![](./images/kerio_edit_domain.png)

- Tại tab ```General``` -> ```DomainKeys Identified Mail (DKIM)``` -> ```Sign outgoing messages from this domain with DKIM signature``` -> ```Show public key```

![](./images/kerio_dkim_value.png)

- Tạo DNS bản ghi với DKIM trên

![](./images/kerio_dkim_record.png)

- Kiểm tra 

![](./images/kerio_dkim_test.png)

