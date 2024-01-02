# Cài đặt OpenLDAP trên CentOS 7

## Các bước chuẩn bị

Cấu hình hostname

```sh
hostnamectl set-hostname "LDAP"
exec bash
```

Tắt firewalld

```sh
systemctl stop firewalld
systemctl disable firewalld
```

Tắt Selinux

```sh
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config
```

Khởi động lại máy

```sh
init 6
```

Cài đặt epel-release và cập nhật OS:

```sh
yum install epel-release -y
yum install update -y
```

## Cài đặt OpenLDAP

Tải và cài đặt các gói cần thiết:

```sh
yum install -y openldap-servers openldap-clients
```

Sao chép file cấu hình và phân quyền:

```sh
cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
chown ldap. /var/lib/ldap/DB_CONFIG
```

Khởi động slapd:

```sh
systemctl enable slapd --now
```

Thiết lập LDAP admin password, tạo mật khẩu:

```sh
slappasswd
```

Thêm mới file ```chroot.lidf```:

```sh
cat > chrootpw.ldif << EOF
dn: olcDatabase={0}config,cn=config
changetype: modify
add: olcRootPW
olcRootPW: {SSHA}R5epaosUlBGn247apRReBJYQeHUhKS0n
EOF
```

Update thông tin từ file ```chroot.ldif```:

```sh
ldapadd -Y EXTERNAL -H ldapi:/// -f chrootpw.ldif
```

Import các schemas:

```sh
ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif
ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif
ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif
```

Thiết lập Manager Password, tạo mật khẩu:

```sh
slappasswd
```

Thêm mới file ```chdomain.ldif```:

```sh
cat > chdomain.ldif << EOF
dn: olcDatabase={1}monitor,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0}to * by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"
  read by dn.base="cn=Manager,dc=nhanhoa,dc=local" read by * none

dn: olcDatabase={2}hdb,cn=config
changetype: modify
replace: olcSuffix
olcSuffix: dc=nhanhoa,dc=local

dn: olcDatabase={2}hdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=Manager,dc=nhanhoa,dc=local

dn: olcDatabase={2}hdb,cn=config
changetype: modify
add: olcRootPW
olcRootPW: {SSHA}j3WRVpZY9A+dtKmvTeGnZuDFscphmR4A

dn: olcDatabase={2}hdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {0}to attrs=userPassword,shadowLastChange by
  dn="cn=Manager,dc=nhanhoa,dc=local" write by anonymous auth by self write by * none
olcAccess: {1}to dn.base="" by * read
olcAccess: {2}to * by dn="cn=Manager,dc=nhanhoa,dc=local" write by * read
EOF
```

Update thông tin từ file ```chdomain.ldif```:

```sh
ldapmodify -Y EXTERNAL -H ldapi:/// -f chdomain.ldif
```

Thêm file ```basedomain.ldif```:

```sh
cat > basedomain.ldif << EOF
dn: dc=nhanhoa,dc=local
objectClass: top
objectClass: dcObject
objectclass: organization
o: Nhanhoa Software
dc: Nhanhoa

dn: cn=Manager,dc=nhanhoa,dc=local
objectClass: organizationalRole
cn: Manager
description: Directory Manager

dn: ou=People,dc=nhanhoa,dc=local
objectClass: organizationalUnit
ou: People

dn: ou=Group,dc=nhanhoa,dc=local
objectClass: organizationalUnit
ou: Group
EOF
```

Update thông tin basedomain:

```sh
ldapadd -x -D cn=Manager,dc=nhanhoa,dc=local -W -f basedomain.ldif
```

Sau khi thực hiện xong các bước chúng ta sử dụng lệnh sau để kiểm tra entry

```sh
slapcat
```

Để thêm mới một entry chúng ta cần tạo ra file ldif và update thông tin file ldif đó rồi dùng slapcat để kiểm tra

VD thêm về một entry user:

```sh
cat > adduser_1.ldif << EOF
dn: cn=adduser_1,ou=People,dc=nhanhoa,dc=local
objectClass: person
objectClass: inetOrgPerson
userPassword:: V2VsY29tZTEyMw==
sn: user
cn: adduser_1
EOF
```

Update file ```adduser_1.ldif``` để thông tin user được thêm vào cây LDAP

```sh
ldapadd -x -D cn=Manager,dc=nhanhoa,dc=local -W -f adduser_1.ldif
```