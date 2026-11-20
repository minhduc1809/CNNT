# Cơ chế chống trùng giao dịch và chống tồn âm (SV3 – CV01)

Tài liệu mô tả cơ chế **đã cài đặt** trong `01_create_database.sql` và `03_create_procedure.sql`.
Mọi kết quả thử nghiệm ở Mục 5 phải do người làm tự chạy và điền; không điền số liệu chưa chạy.

## 1. Vì sao cần hai cơ chế này

- Điểm quét mất mạng sẽ **gửi lại cùng một giao dịch**. Nếu máy chủ ghi hai lần, tồn kho sai.
- Hai điểm quét có thể **xuất cùng một mặt hàng gần như cùng lúc**. Nếu cả hai cùng đọc tồn cũ rồi cùng trừ, tồn có thể âm.

## 2. Chống trùng giao dịch

| Lớp | Cơ chế | Vị trí |
|---|---|---|
| 1 | Procedure đếm bản ghi có cùng `transaction_id`; nếu đã có thì từ chối bằng thông báo "Ma giao dich da ton tai", không đổi tồn | `03_create_procedure.sql` (`v_exists`) |
| 2 | `PRIMARY KEY (transaction_id)` trên bảng `warehouse_transactions`: CSDL không cho hai dòng cùng mã. Đây là lớp chặn cuối khi hai yêu cầu cùng mã đến đồng thời và cùng vượt qua lớp 1 | `01_create_database.sql` |

Ghi chú:
- Khóa chính đã bao hàm tính duy nhất (UNIQUE) và không rỗng, nên không cần thêm chỉ mục UNIQUE riêng.
- Máy khách gửi lại phải **giữ nguyên `txn_id`**. Nếu sinh mã mới mỗi lần gửi lại thì cơ chế này không có tác dụng.
- Khi lớp 2 chạy, yêu cầu thứ hai báo lỗi khóa trùng (mã lỗi MySQL 1062) và bị `ROLLBACK`. Dịch vụ API cần chuyển lỗi này thành phản hồi `DUPLICATE_TXN` cho người dùng. (Cần kiểm tra lại trong `app.py`.)

## 3. Chống tồn âm

| Lớp | Cơ chế | Vị trí |
|---|---|---|
| 1 | `SELECT quantity ... FOR UPDATE` khóa dòng tồn của đúng mặt hàng đó. Hai điểm quét xuất cùng mặt hàng phải xếp hàng: giao dịch sau chỉ đọc tồn sau khi giao dịch trước đã `COMMIT` | `03_create_procedure.sql` |
| 2 | Với `EXPORT`, nếu `tồn < số lượng xuất` thì từ chối bằng thông báo "Ton kho khong du de xuat" | `03_create_procedure.sql` |
| 3 | `CHECK (quantity >= 0)` trên bảng `Inventory`: nếu code có lỗi, CSDL vẫn không cho tồn âm | `01_create_database.sql` |

Các ràng buộc đầu vào bổ sung: `transaction_id` không rỗng; `quantity > 0` (cả trong procedure và `CHECK (quantity > 0)` ở bảng giao dịch); loại giao dịch chỉ nhận `IMPORT` hoặc `EXPORT`.

## 4. Tính nguyên tử (không để dữ liệu dở dang)

Ghi bản ghi giao dịch và cập nhật tồn nằm trong **một transaction** (`START TRANSACTION ... COMMIT`).
Có `EXIT HANDLER FOR SQLEXCEPTION` thực hiện `ROLLBACK` rồi báo lỗi lại.
Dịch vụ chỉ trả xác nhận cho điểm quét **sau khi `COMMIT` thành công**.

Engine bảng là InnoDB (hỗ trợ transaction và khóa dòng).

## 5. Bảng kiểm chứng (tự chạy rồi điền)

Dùng mã `TEST-...` riêng để không lẫn với dữ liệu thật. Mã mặt hàng `SP001`, điểm quét `SCAN01`, người dùng `TK01` có sẵn trong dữ liệu mẫu.

| Ca | Thao tác | Kết quả mong đợi | Kết quả thực tế | Minh chứng |
|---|---|---|---|---|
| T1 – Gửi trùng | Gọi `sp_warehouse_transaction('TEST-DUP-01','SP001','IMPORT',5,'TK01','SCAN01')` hai lần | Lần 2 bị từ chối; tồn chỉ tăng 5; bảng giao dịch có 1 dòng mã này | ........ | MC.... |
| T2 – Xuất vượt tồn | Xuất số lượng lớn hơn tồn hiện có của `SP001` | Bị từ chối; tồn không đổi; không có dòng giao dịch mới | ........ | MC.... |
| T3 – Số lượng 0 / âm | Gọi với `quantity` = 0 và -3 | Bị từ chối | ........ | MC.... |
| T4 – Lớp chặn cuối `CHECK` | Chạy trực tiếp `UPDATE Inventory SET quantity = -1 WHERE product_id='SP001';` | CSDL báo vi phạm `chk_inventory_nonnegative` | ........ | MC.... |
| T5 – Hai phiên cùng xuất | Mở hai cửa sổ MySQL; cửa sổ 1 `START TRANSACTION` + `SELECT ... FOR UPDATE` trên `SP001`, cửa sổ 2 gọi procedure xuất cùng mặt hàng | Cửa sổ 2 phải chờ đến khi cửa sổ 1 `COMMIT`/`ROLLBACK`; tồn cuối không âm | ........ | MC.... |
| T6 – Lỗi giữa chừng | Gọi procedure với `product_id` không tồn tại, loại `IMPORT` | Bị từ chối (lỗi khóa ngoại); không có dòng giao dịch; tồn các mặt hàng khác không đổi | ........ | MC.... |

## 6. Câu hỏi bảo vệ liên quan

- *Vì sao mã giao dịch phải duy nhất?* Vì gửi lại sau mất mạng dùng lại đúng mã đó; CSDL nhận ra và không ghi lần hai.
- *Hai điểm quét xuất cùng mặt hàng thì sao?* `FOR UPDATE` khóa dòng; giao dịch thứ hai đọc tồn đã cập nhật, nên nếu không đủ sẽ bị từ chối.
- *Nếu code procedure có lỗi thì sao?* `CHECK (quantity >= 0)` và `PRIMARY KEY` vẫn chặn ở tầng CSDL.
