# Cinder Scheduler

## I. Giới thiệu về Cinder-scheduler

Giống với ```nova-scheduler```, cinder cũng có 1 daemon chịu trách nhiệm cho việc quyết định xem sẽ tạo cinder volume ở đâu khi mô hình có hơn 1 backend storage. Mặc định nếu người dùng không chỉ rõ host để tạo máy ảo thì ```cinder-scheduler``` sẽ thực hiện filter và weight theo những tùy chọn sau:

```sh
# Which filter class names to use for filtering hosts when not specified in the
# request. (list value)
#scheduler_default_filters = AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter

# Which weighter class names to use for weighting hosts. (list value)
#scheduler_default_weighters = CapacityWeighter
```

Ta sẽ buộc phải kích hoạt tùy chọn ```filter_scheduler``` để sử dụng multiple-storage backends.

## II. Cinder Scheduler Filters

- ```AvailabilityZoneFilter```: Filter bằng availability zone
- ```CapabilitiesFilter```: Filter theo tài nguyên (máy ảo và volume)
- ```CapacityFilter```: Filter dựa vào công suất sử dụng của volume backend
- ```DifferentBackendFilter```: Lên kế hoạch đặt các volume ở các backend khác nhau khi có 1 danh sách các volume
- ```DriverFilter```: Dựa vào ```filter function``` và metrics
- ```InstanceLocalityFilter```: Lên kế hoạch cho các volume trên cùng 1 host. Để có thể dùng filter này thì ```Extended Server Attributes``` cần được bật bởi nova và user sử dụng phải được khai báo xác thực trên cả nova và cinder
- ```JsonFilter```: Dựa vào ```JSON-based grammar``` để chọn lựa backends
- ```RetryFilter```: Lọc ra các máy chủ đã được thử trước đó
   - Host có thể bỏ qua filter này nếu nó chưa được cố gắng thử scheduling trước đó. Scheduler sẽ cần phải thêm các host đã được thử trước đó vào retry key của ```filter_properties``` để có thể làm việc 1 cách chính xác. VD:
   
   ```sh
   {
    'retry': {
        'backends': ['backend1', 'backend2'],
        'num_attempts': 3,
    }
   }
   ```
- ```SameBackendFilter```: Lên kế hoạch đặt các volume có cùng backend như những volume khác

## III. Cinder Scheduler Weights

- ```AllocatedCapacityWeigher```: Allocated Capacity Weighter sẽ tính trọng số của host bằng công suất được phân bổ. Nó sẽ đặt volume vào host được khai báo chiếm ít tài nguyên nhất
- ```CapacityWeigher```: Trạng thái công suất thực tế chưa được sử dụng
- ```ChanceWeigher```: Tính trọng số random, dùng để tạo các volume khi các host gần giống nhau
- ```GoodnessWeigher```: Gán trọng số dựa vào goodness function. Goodness rating

```sh
0 -- host is a poor choice
.
.
50 -- host is a good choice
.
.
100 -- host is a perfect choice
```

- ```VolumeNumberWeigher```: Tính toán trọng số của các host bởi số lượng volume trong backends

## IV. Quản lý Block Storage Scheduling

Đối với admin, ta có thể quản lí việc volume sẽ được tạo theo backend nào. Ta có thể affinity hoặc anti-affinity giữa 2 volumes
- ```Affinity```: Ưu tiên cùng backend
- ```Anti-affinity```: Ưu tiên đặt trên các backend khác nhau

**Một số ví dụ:**
1. Tạo 1 volume cùng backend với Volume_A

```sh
openstack volume create --hint same_host=Volume_A-UUID --size SIZE VOLUME_NAME
```

2. Tạo 1 volume khác backend với Volume_A

```sh
openstack volume create --hint different_host=Volume_A-UUID --size SIZE VOLUME_NAME
```

3. Tạo volume cùng backend với Volume_A và Volume_B

```sh
openstack volume create --hint same_host=Volume_A-UUID --hint same_host=Volume_B-UUID --size SIZE VOLUME_NAME
```

4. Tạo volume khác backend với Volume_A và Volume_B

```sh
openstack volume create --hint different_host=Volume_A-UUID --hint different_host=Volume_B-UUID --size SIZE VOLUME_NAME
```

hoặc

```sh
openstack volume create --hint different_host="[Volume_A-UUID, Volume_B-UUID]" --size SIZE VOLUME_NAME
```