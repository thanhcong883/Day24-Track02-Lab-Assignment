# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure) — endpoint DELETE `/api/patients/{id}`
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256-GCM at rest (SimpleVault), TLS 1.3 in transit | ✅ Done | Infra Team |
| Audit logging | FastAPI access logs + API request/response logging middleware | ✅ Done | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus + Grafana alert rules) | ✅ Done | Security Team |

## F. Technical Solutions cho các mục "Todo"

### Audit Logging
- Triển khai **FastAPI middleware** ghi lại mọi request: timestamp, user, endpoint, HTTP status.
- Lưu log vào **CloudWatch / ELK Stack** (Elasticsearch + Logstash + Kibana).
- Mỗi API call đến `/api/patients/*` đều được log kèm `user_id`, `role`, `action`, `resource_id`.
- Retention policy: giữ log tối thiểu 12 tháng theo NĐ13/2023.

```python
# Ví dụ middleware audit log trong FastAPI
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "user": request.headers.get("Authorization", "anonymous"),
        "status_code": response.status_code,
    })
    return response
```

### Breach Detection
- Cài đặt **Prometheus** scrape metrics từ FastAPI (số request 4xx/5xx, tần suất login thất bại).
- Tạo **Grafana alert rule**: nếu số lượng request 401/403 tăng đột biến trong 5 phút → gửi alert qua PagerDuty/Slack.
- Tích hợp **SIEM** (ví dụ Wazuh hoặc AWS Security Hub) để phát hiện bất thường (data exfiltration, privilege escalation).
- Thực hiện **pen test** định kỳ 6 tháng/lần và báo cáo kết quả cho DPO.
- Quy trình xử lý sự cố: phát hiện → cách ly → điều tra → vá lỗi → báo cáo cơ quan trong **72 giờ**.
