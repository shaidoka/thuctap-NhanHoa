# Cấu hình HPA đa ứng dụng dựa trên metrics của NGINX ingress controller

Ta có thể deploy 1 ứng dụng trong nhiều pods để cải thiện tính ổn định của nó. Tuy vậy, phương thức này cũng tăng chi phí về tài nguyên và gây lãng phí vào thời giờ thấp điểm. Để giải quyết vấn đề này, ta sẽ cần đến HPA cho ứng dụng dựa trên metrics nhận về từ NGINX Ingress controller. Phương pháp này cải thiện tính ổn định của ứng dụng và giảm chi phí O&M.

## Điều kiện tiên quyết

Để cấu hình HPA như mong muốn, ta phải chuyển đổi Prometheus metric thành 1 metric được hỗ trợ bởi HPA và deploy những thành phần cần thiết:
- Cài đặt Prometheus
- 