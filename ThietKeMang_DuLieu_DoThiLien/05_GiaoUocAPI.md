# Giao ước API và ma trận quyền – Đề tài 22

| | |
|---|---|
| Phiên bản | **v1.0** – 26/10/2026 (chốt tại Cổng 1) |
| Người soạn | SV1 |
| Bên dùng | SV2 (máy khách điểm quét), SV3 (máy chủ, lưu trữ, quyền), SV4 (kiểm thử) |
| Tài liệu liên quan | `06_TuDienDuLieu.md`, `du_lieu/schema.sql`, `04_SoDoLuongDuLieu.png` |
| Thay đổi | Mọi thay đổi phải tăng phiên bản và ghi vào `doi_chieu/NhatKyThayDoi.md` |

## 1. Quy ước chung

| Mục | Quy ước |
|---|---|
| Giao thức | HTTP/1.1, thân yêu cầu và phản hồi là JSON UTF-8 (`Content-Type: application/json`) |
| Địa chỉ máy chủ | Triển khai thật `http://192.168.10.10:8080` (hoặc `http://kho.local:8080`) · mô phỏng `http://127.0.0.1:8080` |
| Tên trường | **Trùng tên cột CSDL** trong từ điển dữ liệu: snake_case, tiếng Anh, không dấu |
| Thời gian | ISO 8601 giờ địa phương, không múi giờ: `2026-10-26T09:15:02` |
| Xác thực | `POST /api/login` → `token`; mọi lệnh khác gửi header `Authorization: Bearer <token>` |
| Người thực hiện | Máy chủ lấy `username` **từ token**, không nhận `username` do máy khách tự khai |
| Hết thời gian chờ | Máy khách chờ tối đa **5 giây**; quá hạn coi như mất mạng (xem mục 6) |
| Định dạng lỗi | Luôn `{ "status": "REJECTED" \| "ERROR", "error_code": "...", "message": "..." }` |

## 2. Đăng nhập – `POST /api/login`

```json
{ "username": "nv01", "password": "Kho@2026" }
```

`200 OK`
```json
{ "status": "OK", "token": "c2b1f0…", "username": "nv01", "role": "NHANVIEN", "expires_in": 28800 }
```

Sai tài khoản/mật khẩu hoặc tài khoản bị khóa → `401 LOGIN_FAILED`.

## 3. Ghi giao dịch – `POST /api/transactions`

Yêu cầu:

```json
{
  "txn_id": "SP01-20261026-0001",
  "product_code": "SP001",
  "txn_type": "NHAP",
  "quantity": 20,
  "scan_point_id": "SP01",
  "client_time": "2026-10-26T09:15:00"
}
```

| Trường | Bắt buộc | Quy tắc |
|---|---|---|
| `txn_id` | Có | Dạng `SPxx-yyyymmdd-nnnn` (regex `^SP\d{2}-\d{8}-\d{4}$`). Máy khách sinh, **lưu vào hàng đợi trước khi gửi**, gửi lại thì giữ nguyên |
| `product_code` | Có | Có trong `Products` và `is_active = 1` |
| `txn_type` | Có | `NHAP` hoặc `XUAT` |
| `quantity` | Có | Số nguyên 1 … 10000 |
| `scan_point_id` | Có | Có trong `ScanPoints`, `is_active = 1`, trùng tiền tố của `txn_id` |
| `client_time` | Có | Giờ quét tại máy khách |

Thành công – `201 Created` (máy chủ **chỉ trả sau khi COMMIT**):

```json
{ "status": "OK", "txn_id": "SP01-20261026-0001", "product_code": "SP001",
  "stock_after": 120, "server_time": "2026-10-26T09:15:02" }
```

Gửi trùng – `409 Conflict`, tồn **không** đổi, trả kèm kết quả của lần ghi đầu:

```json
{ "status": "REJECTED", "error_code": "DUPLICATE_TXN", "message": "Mã giao dịch đã được ghi trước đó",
  "original": { "stock_after": 120, "server_time": "2026-10-26T09:15:02" } }
```

Thứ tự kiểm tra trên máy chủ: token (R5) → quyền ghi (R5) → định dạng và trường bắt buộc (R3) → điểm quét (R6) → **trùng txn_id (R1)** → mã hàng (R2) → tồn đủ khi XUAT (R4) → ghi trong 1 giao dịch CSDL (R7) → COMMIT → phản hồi (R9).

## 4. Đọc tồn

### `GET /api/inventory`

`200 OK`
```json
{ "status": "OK", "count": 5, "items": [
  { "product_code": "SP001", "product_name": "Nước suối 500ml", "unit": "thùng",
    "quantity": 120, "last_txn_id": "SP01-20261026-0001", "updated_at": "2026-10-26T09:15:02" }
] }
```

### `GET /api/inventory/{product_code}`

Trả một phần tử như trên; mã hàng không có → `404 PRODUCT_NOT_FOUND`.

## 5. Đọc lịch sử giao dịch

### `GET /api/transactions?product_code=&scan_point_id=&username=&from=&to=&limit=`

| Tham số | Bắt buộc | Ý nghĩa |
|---|---|---|
| `product_code`, `scan_point_id`, `username` | Không | Lọc theo mã hàng / điểm quét / người thực hiện |
| `from`, `to` | Không | Lọc theo `server_time`, dạng `2026-10-26` hoặc ISO 8601 đầy đủ |
| `limit` | Không | Mặc định 100, tối đa 1000; sắp xếp `server_time` giảm dần |

Tài khoản NHANVIEN chỉ nhận giao dịch của chính mình (máy chủ tự thêm điều kiện `username = <người gọi>`).

`200 OK`
```json
{ "status": "OK", "count": 1, "items": [
  { "txn_id": "SP01-20261026-0001", "product_code": "SP001", "txn_type": "NHAP", "quantity": 20,
    "username": "nv01", "scan_point_id": "SP01", "client_time": "2026-10-26T09:15:00",
    "server_time": "2026-10-26T09:15:02", "stock_after": 120, "note": null }
] }
```

### `GET /api/transactions/{txn_id}`

Dùng để **xác minh máy chủ đã lưu** một giao dịch (sau khi mất phản hồi). Có → `200` + một phần tử như trên; chưa có → `404 TXN_NOT_FOUND`.

### `GET /api/reconcile`

Trả nội dung view `v_doi_chieu_ton`:

```json
{ "status": "OK", "all_match": true, "items": [
  { "product_code": "SP001", "product_name": "Nước suối 500ml", "ton_luu_tru": 120, "ton_tinh_lai": 120, "chenh_lech": 0 }
] }
```

## 6. Danh sách mã lỗi

| HTTP | error_code | Khi nào | Tồn bị đổi? | Máy khách xử lý | Gửi lại? |
|---|---|---|---|---|---|
| 400 | `INVALID_JSON` | Thân yêu cầu không phải JSON hoặc thiếu trường bắt buộc | Không | Báo lỗi phần mềm | Không |
| 400 | `INVALID_TXN_ID` | `txn_id` sai định dạng hoặc tiền tố khác `scan_point_id` | Không | Sinh lại txn_id đúng | Không |
| 400 | `INVALID_TYPE` | `txn_type` khác NHAP/XUAT | Không | Chọn lại loại | Không |
| 400 | `INVALID_QUANTITY` | Số lượng không nguyên, ≤ 0 hoặc > 10000 | Không | Nhập lại số lượng (txn_id mới) | Không |
| 400 | `INVALID_SCAN_POINT` | Điểm quét không tồn tại hoặc ngừng hoạt động | Không | Báo quản trị | Không |
| 401 | `LOGIN_FAILED` | Sai tài khoản/mật khẩu, tài khoản bị khóa | — | Nhập lại | Không |
| 401 | `UNAUTHORIZED` | Thiếu token, token sai hoặc hết hạn | Không | Đăng nhập lại rồi gửi lại **cùng txn_id** | Có |
| 403 | `FORBIDDEN` | Vai trò không có quyền (VD: QUANLY ghi giao dịch) | Không | Báo “không có quyền” | Không |
| 404 | `PRODUCT_NOT_FOUND` | Mã hàng không có hoặc ngừng kinh doanh | Không | Báo thủ kho | Không |
| 404 | `TXN_NOT_FOUND` | `GET /api/transactions/{txn_id}` chưa có | — | Gửi lại giao dịch đang chờ | Có |
| 409 | `DUPLICATE_TXN` | `txn_id` đã được ghi | **Không** | Coi như **đã lưu**, xóa khỏi hàng đợi | Không |
| 422 | `INSUFFICIENT_STOCK` | Xuất nhiều hơn tồn | Không | Báo nhân viên | Không |
| 500 | `SERVER_ERROR` | Lỗi CSDL/máy chủ, đã ROLLBACK | Không | Giữ trong hàng đợi | Có |
| — | (không phản hồi) | Mất mạng, quá 5 giây | Chưa biết | Giữ trong hàng đợi, thử lại 5 s → 10 s → 20 s (tối đa 60 s) với **cùng txn_id** | Có |

Mọi yêu cầu ghi, kể cả bị từ chối, đều được ghi vào `AuditLog` với `result` và `error_code` tương ứng.

## 7. Ma trận quyền

Ký hiệu: ✔ được phép · ◐ được phép có giới hạn · ✘ bị từ chối (`403 FORBIDDEN`).

| Chức năng | API | ADMIN (quản trị) | THUKHO (thủ kho) | NHANVIEN (nhân viên) | QUANLY (chỉ xem) |
|---|---|:-:|:-:|:-:|:-:|
| Đăng nhập | `POST /api/login` | ✔ | ✔ | ✔ | ✔ |
| Ghi giao dịch NHAP/XUAT | `POST /api/transactions` | ✔ | ✔ | ✔ | ✘ |
| Đọc tồn kho | `GET /api/inventory[/{code}]` | ✔ | ✔ | ✔ | ✔ |
| Đọc lịch sử giao dịch | `GET /api/transactions` | ✔ | ✔ | ◐ chỉ của mình | ✔ |
| Kiểm tra một giao dịch | `GET /api/transactions/{txn_id}` | ✔ | ✔ | ◐ chỉ của mình | ✔ |
| Đối chiếu tồn | `GET /api/reconcile` | ✔ | ✔ | ✘ | ✔ |
| Thêm/sửa danh mục hàng | `POST`/`PUT /api/products` | ✔ | ✔ | ✘ | ✘ |
| Quản lý tài khoản | `POST`/`PUT /api/users` | ✔ | ✘ | ✘ | ✘ |
| Quản lý điểm quét | `POST`/`PUT /api/scanpoints` | ✔ | ✘ | ✘ | ✘ |
| Xem nhật ký AuditLog | `GET /api/audit` | ✔ | ✘ | ✘ | ✔ |
| Sao lưu CSDL | `POST /api/backup` | ✔ | ✘ | ✘ | ✘ |
| Khôi phục CSDL | `POST /api/restore` | ✔ | ✘ | ✘ | ✘ |
| Sửa / xóa giao dịch đã ghi | *(không có API)* | ✘ | ✘ | ✘ | ✘ |

Ghi chú:

- **Không ai** sửa hoặc xóa được giao dịch đã ghi: CSDL có trigger chặn. Ghi sai thì làm một giao dịch ngược chiều (NHAP ↔ XUAT) có `note` “Điều chỉnh cho <txn_id>”.
- Chỉ tiến trình máy chủ đọc/ghi file `kho.db`. Máy khách không bao giờ truy cập CSDL trực tiếp, nên quyền được kiểm soát ở một chỗ duy nhất.
- KT3 dùng tài khoản `quanly01`: thử `POST /api/transactions` phải nhận `403 FORBIDDEN` và tồn không đổi.
- Tài khoản mẫu (mật khẩu `Kho@2026`): `admin`, `thukho01`, `nv01`, `nv02`, `quanly01`.
