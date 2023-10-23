# File log của Keystone

File cấu hình log của Keystone nằm tại ```/etc/keystone/logging.conf```. Trong đó có 3 kiểu log có thể cấu hình:

1. Formatter_minimal

```sh
format=%(message)s
```

2. Formatter_normal

```sh
format(%(name)s): %(asctime)s %(levelname)s %(message)s
```

3. Formatter_debug

```sh
format=(%(name)s): %(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s
```

Mặc định, log của keystone sẽ được ghi tại ```/var/log/keystone/keystone.log```

## Một vài log thường gặp

1. Đăng nhập đúng user - đúng pass

```sh
2020-07-09 15:47:30.541 2378 WARNING keystone.server.flask.application [req-6570f6d3-399a-4564-82a6-666692b2bd5d 294c5c6181d442c68a13d5b615c4f031 - - default -] Authorization failed. The request you have made requires authentication. from 10.10.31.166: Unauthorized: The request you have made requires authentication.
```

2. Đăng nhập đúng user - sai pass

```sh
2020-07-09 16:04:21.195 2382 WARNING keystone.server.flask.application [req-54da289c-53be-4f52-a77e-8028f820ae5b - - - - -] Authorization failed. The request you have made requires authentication. from 10.10.31.166: Unauthorized: The request you have made requires authentication.
```

3. Đăng nhập sai user

```sh
2020-07-09 16:06:55.123 2379 WARNING keystone.auth.plugins.core [req-9ca76628-2a93-4ab5-89c5-2328d3f430cd - - - - -] Could not find user: ad.: UserNotFound: Could not find user: ad.
2020-07-09 16:06:55.141 2379 WARNING keystone.server.flask.application [req-9ca76628-2a93-4ab5-89c5-2328d3f430cd - - - - -] Authorization failed. The request you have made requires authentication. from 10.10.31.166: Unauthorized: The request you have made requires authentication.
```

4. Khởi tạo máy ảo

```sh
[req-25b17d71-277c-429b-b61c-658a7147d7a6 4be5d5ed900f4386a5f9268927c46ecb af57453a686740f18e48a8c4cf4ac994 - default default]
```

Trong đó:
- ```req-25b17d71-277c-429b-b61c-658a7147d7a6```: mã request
- ```4be5d5ed900f4386a5f9268927c46ecb```: ID user (khi khởi tạo máy ảo thì user này là Nova)
- ```af57453a686740f18e48a8c4cf4ac994```: ID project (project trong trường hợp này là Service)
- ```default default```: DomainID và DomainName