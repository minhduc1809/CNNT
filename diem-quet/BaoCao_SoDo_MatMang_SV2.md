# BÁO CÁO SỐ ĐO THỰC NGHIỆM, XỬ LÝ MẤT MẠNG & ĐỐI CHIẾU SEQ_NO (SV2 - CV03)
**Hệ thống Quản lý Kho Hàng Thông Minh – Đề tài 22**
- **Thời điểm thực nghiệm:** `2026-11-09 10:25:08`
- **Máy chủ đích:** `http://127.0.0.1:5000`

---

## 1. Bảng số đo thực tế tại 2 điểm quét (`SP01` & `SP02`)

| Điểm quét | IP máy trạm | `seq_no` cuối | Tổng giao dịch | Đã xác nhận (`DA_XAC_NHAN`) | Từ chối nghiệp vụ (`TU_CHOI`) | Tồn đọng (`CHO_XAC_NHAN`) | Tổng số lần gửi lại (Retry) | Độ trễ TB (ms) | Độ trễ Min / Max (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SP01** | `192.168.20.11` | `4` | 4 | 2 | 2 | 0 | 2 | `10.58 ms` | `5.18 / 16.40 ms` |
| **SP02** | `192.168.20.12` | `3` | 3 | 2 | 1 | 0 | 0 | `13.10 ms` | `9.84 / 15.32 ms` |

---

## 2. Bảng đối chiếu chi tiết từng `seq_no` giữa Điểm quét và Máy chủ CSDL

| Điểm quét | `seq_no` | Mã giao dịch (`txn_id`) | Mã hàng | Loại | Số lượng | Trạng thái tại Client | Số lần Retry | Độ trễ | Trạng thái trên Máy chủ SV3 | Kết luận đối chiếu |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| `SP01` | `1` | `SP01-20261109-0001` | `SP001` | `NHAP` | `20` | `DA_XAC_NHAN` | 0 | `14.62 ms` | Có trên CSDL (200 OK - lúc 10:17:19) | **KHỚP 100%** |
| `SP01` | `2` | `SP01-20261109-0002` | `SP001` | `NHAP` | `5` | `TU_CHOI` | 0 | `5.18 ms` | Không lưu (Đúng kỳ vọng chặn 403 - lúc 10:19:11) | **KHỚP 100%** |
| `SP01` | `3` | `SP01-20261109-0003` | `SP999` | `NHAP` | `5` | `TU_CHOI` | 0 | `6.12 ms` | Không lưu (Đúng kỳ vọng chặn 404 - lúc 10:20:06) | **KHỚP 100%** |
| `SP01` | `4` | `SP01-20261109-0004` | `SP005` | `NHAP` | `15` | `DA_XAC_NHAN` | 2 | `16.40 ms` | Có trên CSDL (200 OK sau phục hồi mạng - lúc 10:24:12) | **KHỚP 100%** |
| `SP02` | `1` | `SP02-20261109-0001` | `SP001` | `XUAT` | `10` | `DA_XAC_NHAN` | 0 | `15.32 ms` | Có trên CSDL (200 OK - lúc 10:17:46) | **KHỚP 100%** |
| `SP02` | `2` | `SP02-20261109-0002` | `SP003` | `XUAT` | `500` | `TU_CHOI` | 0 | `9.84 ms` | Không lưu (Đúng kỳ vọng chặn thiếu tồn - lúc 10:20:41) | **KHỚP 100%** |
| `SP02` | `3` | `SP02-20261109-0003` | `SP006` | `XUAT` | `4` | `DA_XAC_NHAN` | 0 | `14.15 ms` | Có trên CSDL (200 OK sau khởi động lại - lúc 10:24:28) | **KHỚP 100%** |

---

## 3. Nhận xét & Kết luận thực nghiệm (CV03)
1. **Tính toàn vẹn của `seq_no` và hàng đợi khi tắt đột ngột:**
   - Mọi thao tác cấp phát `seq_no` (`queue/seq_SP01.txt`, `queue/seq_SP02.txt`) và ghi hàng đợi (`queue/queue_SP01.jsonl`, `queue/queue_SP02.jsonl`) đều thực hiện `flush()` + `os.fsync()` xuống đĩa cứng trước khi gửi mạng.
   - Khi giả lập tắt đột ngột tiến trình `SP02` ngay sau khi ghi giao dịch `SP006`, lúc khởi động lại điểm quét tự động phát hiện giao dịch `CHO_XAC_NHAN` và đồng bộ lên máy chủ thành công, không mất dữ liệu và không nhảy cóc `seq_no`.
2. **Cơ chế gửi lại có kiểm soát (Exponential Backoff & Idempotency):**
   - Khi mất mạng, điểm quét giữ nguyên `txn_id` ban đầu và chờ tăng dần trước khi thử lại.
   - Khi gửi lặp lại cùng một `txn_id` đã lưu, máy chủ trả về `409 DUPLICATE_TXN`, điểm quét ghi nhận `DA_XAC_NHAN` và tồn kho trên máy chủ không bị cộng/trừ hai lần.
3. **Đối chiếu sau khôi phục mạng:**
   - Số giao dịch bị mất: **0**.
   - Số giao dịch bị ghi đúp: **0**.
   - Toàn bộ các `seq_no` hợp lệ đều khớp 100% giữa nhật ký máy trạm và bảng `warehouse_transactions` trên máy chủ.
