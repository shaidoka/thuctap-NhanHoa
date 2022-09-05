# Quản lý dịch vụ bằng dòng lệnh

### Giao diện web Plesk

- Bắt đầu dịch vụ

```sh
net start plesksrv
netstart poppassd
```

- Dừng dịch vụ

```sh
net stop plesksrv
```

### MailEnable

- Để bắt đầu dịch vụ thông qua dòng lệnh

```sh
net start meimaps && net start melcs && net start memtas && net start mepops && net start mepocs && net start mesmtpcs
```

- Để dừng dịch vụ thông qua dòng lệnh

```sh
net stop meimaps && net stop melcs && net stop memtas && net stop mepops && net stop mepocs && net stop mesmtpcs
```

### MySQL

- Để bắt đầu dịch vụ

```sh
net start plesksqlserver
```

- Để dừng dịch vụ

```sh
net stop plesksqlserver
```

### Odin Premium Antivirus

- Để bắt đầu dịch vụ

```sh
net start DrWebCom
```

- Để dừng dịch vụ

```sh
net stop DrWebCom
```

### Dịch vụ FTP

- Để dừng dịch vụ

```sh
net stop iisadmin
```

- Để bắt đầu dịch vụ

```sh
net start iisadmin
```