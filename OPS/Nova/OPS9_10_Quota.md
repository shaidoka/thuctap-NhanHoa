# Quota

## I. Update quota class default

Update các giá trị quota cho class default
- Các project mới được tạo sẽ nhận quota theo class default này
- Các project hiện có mà chưa sửa quota cũng sẽ thay đổi quota theo giá trị của class default này

```sh
openstack quota set --instance 50 --class default
```

Show giá trị quota của class default

```sh
openstack quota show --class default
```

## II. Set quota for project

Câu lệnh set quota cho project chỉ định

```sh
openstack quota set 
    # Compute settings 
    [--cores <num-cores>] 
    [--fixed-ips <num-fixed-ips>] 
    [--floating-ips <num-floating-ips>] 
    [--injected-file-size <injected-file-bytes>] 
    [--injected-files <num-injected-files>] 
    [--instances <num-instances>] 
    [--key-pairs <num-key-pairs>] 
    [--properties <num-properties>] 
    [--ram <ram-mb>] 
    [--server-groups <num-server-groups>] 
    [--server-group-members <num-server-group-members>] 
    # Block Storage settings 
    [--backups <new-backups>] 
    [--backup-gigabytes <new-backup-gigabytes>] 
    [--gigabytes <new-gigabytes>] 
    [--per-volume-gigabytes <new-per-volume-gigabytes>] 
    [--snapshots <new-snapshots>] 
    [--volumes <new-volumes>] 
    [--volume-type <volume-type>] 
    # Network settings 
    [--floating-ips <num-floatingips>] 
    [--secgroup-rules <num-security-group-rules>] 
    [--secgroups <num-security-groups>] 
    [--networks <num-networks>] 
    [--subnets <num-subnets>] 
    [--ports <num-ports>] 
    [--routers <num-routers>] 
    [--rbac-policies <num-rbac-policies>] 
    [--subnetpools <num-subnetpools>] 
    <project>
```

## III. Một số lệnh thường dùng

List ID project (mỗi ID trên 1 dòng)

```sh
openstack project list -f value -c ID
```

Show quota project

```sh
openstack quota show <project_name | project_ID>
```