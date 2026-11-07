# Kế hoạch chi tiết 3 tuần theo từng sinh viên
**Thiết kế hạ tầng CNTT cho hệ thống quản lý kho hàng thông minh – Phiếu giao đề 22**

Kế hoạch gồm 21 ngày, 4 cổng kiểm tra; mỗi sinh viên có danh sách việc theo thứ tự làm, ngày làm, sản phẩm và việc phải chờ từ ai. Tài liệu đi kèm: *Quy mô và định nghĩa ban đầu* và *Mô tả công việc và phân công thành viên*.

**Lớp:** ........ | **Nhóm:** ........ | **Ngày bắt đầu:** ........ | **Hạn nộp:** ........

---

## 1. Cách đọc kế hoạch
* **Ngày 1–21** là ngày đếm từ ngày bắt đầu của nhóm. Nếu bắt đầu vào thứ Hai 26/10/2026 (giả định, nhóm thay bằng ngày thật) thì Ngày 21 là Chủ nhật 15/11/2026.
* **Tuần 1** là Ngày 1–7, **Tuần 2** là Ngày 8–14, **Tuần 3** là Ngày 15–21.
* **Cột Mã việc** khớp tài liệu phân công: `CV01`–`CV03` là việc chuyên môn; `Chung` là vai trò chung; `Nâng cao` chỉ làm khi Cổng 2 đã đạt và lõi đã có bằng chứng; `Báo cáo` là báo cáo cá nhân.
* **Cột Chờ từ** cho biết việc đó cần kết quả của ai hoặc cổng nào. Chưa có thì làm trước phần không phụ thuộc, hoặc dùng dịch vụ giả để thử.
* **Ghi minh chứng ngay khi làm:** chụp ảnh, lưu nhật ký, đặt mã `MC` và ghi file cùng vị trí. Không để đến Tuần 3 mới tìm lại; mẫu báo cáo cá nhân không cho tự tạo số liệu hoặc minh chứng.

---

## 2. Bốn cổng kiểm tra

| Cổng | Hạn | Điều kiện đạt | Ai xác nhận | Ngày nếu bắt đầu 26/10/2026 |
| :--- | :--- | :--- | :--- | :--- |
| **Cổng 1** | Cuối Ngày 3 | Đã chốt công nghệ và định dạng `txn_id`; có sơ đồ quan hệ, từ điển dữ liệu, giao ước API, ma trận quyền, bảng IP; máy ảo máy chủ đã khởi động | SV1 chủ trì, cả nhóm đồng ý | Thứ Tư 28/10 |
| **Cổng 2** | Cuối Ngày 10 | Ba vùng mạng chạy với IP và tường lửa theo bảng; hai điểm quét gửi giao dịch qua mạng; máy chủ lưu và đọc lại được; lịch sử ghi đúng điểm quét; phân quyền cơ bản chạy | SV4 xác minh | Thứ Tư 4/11 |
| **Cổng 3** | Cuối Ngày 15 | KT1–KT3 và kiểm thử truy cập mạng có bằng chứng; sao lưu theo lịch đã tạo bản sao và khôi phục thật | SV4 xác minh | Thứ Hai 9/11 |
| **Cổng 4** | Cuối Ngày 18 | Đã đo tài nguyên thật, thử ngắt mạng thật, có báo cáo đối chiếu và bản nháp hồ sơ chung | SV1 và SV4 | Thứ Năm 12/11 |

Ngoài bốn cổng, cả nhóm họp ngắn (khoảng 15 phút) vào **Ngày 1, 6, 13 và 20** để báo tiến độ và gỡ vướng.

---

## 3. Tổng quan theo tuần

| Thành viên | Tuần 1 (Ngày 1–7) | Tuần 2 (Ngày 8–14) | Tuần 3 (Ngày 15–21) |
| :--- | :--- | :--- | :--- |
| **SV1** | Chốt công nghệ; sơ đồ quan hệ, giao ước API, ma trận quyền; sơ đồ mạng; bắt đầu dựng ba vùng mạng | Tường lửa và kiểm chứng kết nối; sơ đồ luồng; đối chiếu tên trường; mô hình ước lượng; script | Hồ sơ chung; báo cáo cá nhân; tập bảo vệ |
| **SV2** | Khung điểm quét (đã có), hai bản SCAN01 và SCAN02, kiểm tra đầu vào; chuẩn bị hai máy điểm quét | Ping và curl đến máy chủ; kết nối dịch vụ thật qua mạng; Cổng 2; hàng đợi, gửi lại; thử mất mạng thật | Thử ngắt mạng cùng SV4; kịch bản demo; báo cáo cá nhân; tập demo |
| **SV3** | Máy ảo Linux, CSDL, IP tĩnh; bảng, ràng buộc, nạp 100 mặt hàng; dịch vụ tối thiểu | Tường lửa cùng SV1; phân quyền ba tầng; Cổng 2; sao lưu theo lịch; khôi phục thật | KT3b; môi trường demo; báo cáo cá nhân; tập bảo vệ |
| **SV4** | Kế hoạch kiểm thử; soạn ca kiểm thử, gồm cả truy cập mạng | Thử sớm; KT1, KT2; kiểm thử truy cập mạng; KT3a và ca lỗi | KT3b; đo tài nguyên thật; đối chiếu sau ngắt mạng; bảng kết quả chung; báo cáo cá nhân |

---

## 4. SV1 – Mạng và thiết kế dữ liệu

| # | Ngày | Việc theo thứ tự | Mã việc | Sản phẩm hoặc minh chứng | Chờ từ |
| :-: | :---: | :--- | :---: | :--- | :--- |
| 1 | 1 | Họp chốt công nghệ (CSDL, cách dựng 3 vùng mạng, dạng điểm quét, định dạng `txn_id`); ghi quyết định vào Mục 15.1 | Chung | Mục 15.1 đã chốt | Cả nhóm |
| 2 | 1–2 | Vẽ sơ đồ quan hệ 5 bảng và từ điển dữ liệu (đã có bản vẽ đầu `02_MoHinhDuLieu.png`, rà lại và chỉnh nếu cần) | CV02 | `02_MoHinhDuLieu.png`; từ điển dữ liệu | Bước 1 |
| 3 | 2–3 | Viết giao ước API: ghi giao dịch, đọc tồn, đọc lịch sử, danh sách mã lỗi; lập ma trận quyền ba tầng | CV03 | Tài liệu giao ước API; ma trận quyền | Bước 2 |
| 4 | 3 | Bàn giao thiết kế cho SV2, SV3, SV4; chủ trì Cổng 1 | CV02, CV03 | Cổng 1 đạt | Bước 2–3 |
| 5 | 3–4 | Vẽ sơ đồ mạng; lập bảng IP cho 3 vùng; liệt kê quy tắc truy cập cần kiểm chứng; chọn cách dựng (phần mềm ảo hóa hoặc container) | CV01 | `01_SoDoHaTang.png`; bảng IP | Bước 1 |
| 6 | 4–6 | Dựng ba vùng mạng thật: mạng ảo tách riêng, IP tĩnh cho từng máy theo bảng IP, định tuyến giữa các vùng, đồng bộ giờ | CV01 | Cấu hình mạng; ảnh ping giữa các vùng | Bước 5; máy chủ của SV3 (Ngày 3–4) |
| 7 | 6–8 | Áp dụng quy tắc truy cập bằng tường lửa cùng SV3; kiểm chứng hai chiều (được phép thì qua, bị chặn thì chặn) bằng ping, curl, kiểm tra cổng | CV01 | File cấu hình tường lửa; bảng kết quả kiểm tra kết nối | Bước 6 |
| 8 | 6–9 | Vẽ sơ đồ trình tự quét → gửi → kiểm tra → lưu → cập nhật tồn → phản hồi, có nhánh lỗi và nhánh trùng; viết `03_ThietKeDuLieu` | CV02 | Sơ đồ luồng; `03_ThietKeDuLieu` | Bước 3 |
| 9 | 8–9 | Đối chiếu tên trường trong mã của SV2 và SV3 với từ điển dữ liệu, ghi kết quả; nếu lệch thì chỉnh giao ước và ghi nhật ký thay đổi | CV02 | Bảng đối chiếu tên trường | SV2, SV3 có mã đầu |
| 10 | 10 | Dự Cổng 2: xem ba vùng mạng, tường lửa và chuỗi gửi, lưu, đọc lại | Chung | Cổng 2 | SV2, SV3 |
| 11 | 10–12 | Xây mô hình ước lượng tăng từ 2 lên 4 điểm quét: công thức, giả định, kết quả; ghi rõ là ước lượng, chưa đo | CV03 | Bảng ước lượng có công thức | Bước 3 |
| 12 | 13 | Giao mô hình ước lượng và bảng quy tắc truy cập cho SV4 | CV03 | Bàn giao | Bước 7, 11 |
| 13 | 13–16 | Nâng cao (khi Cổng 2 đã đạt): script tải 2 rồi 4 tiến trình; script kiểm tra kết nối cho phép và bị chặn | Nâng cao | Script; kết quả chạy | Cổng 2 |
| 14 | 13–17 | Dựng khung hồ sơ chung (mục lục, thuật ngữ, danh mục minh chứng); thu tài liệu từ SV2–SV4 | Chung | Khung hồ sơ | Cổng 3 |
| 15 | 17–19 | Hoàn thiện hồ sơ chung; rà thuật ngữ và số liệu cùng SV4 | Chung | Hồ sơ chung | Cổng 4 |
| 16 | 18–20 | Viết báo cáo cá nhân SV1 | Báo cáo | Báo cáo cá nhân | Bước 15 |
| 17 | 20–21 | Tập bảo vệ cả nhóm; trả lời câu hỏi chuẩn bị của SV1 | Chung | — | Cả nhóm |

---

## 5. SV2 – Hai điểm quét giả lập

| # | Ngày | Việc theo thứ tự | Mã việc | Sản phẩm hoặc minh chứng | Chờ từ |
| :-: | :---: | :--- | :---: | :--- | :--- |
| 1 | 1 | Họp chốt công nghệ; cài môi trường; tạo thư mục mã nguồn (đã có `diem-quet/`) | Chung | Thư mục dự án | Cả nhóm |
| 2 | 1–3 | Khung điểm quét: nhập 4 thông tin, sinh `txn_id` và `seq_no`, in giao dịch dạng JSON (đã có); chạy hai bản SCAN01 và SCAN02 cùng lúc, chụp ảnh | CV01 | Mã nguồn khung; file cấu hình; ảnh hai điểm quét | Bước 1 |
| 3 | 3–4 | Chỉnh tên trường theo giao ước API của SV1; chạy lại các ca nhập sai (kiểm tra đầu vào đã có) | CV01, CV02 | Ảnh các ca nhập sai và một giao dịch hợp lệ | Cổng 1 |
| 4 | 5–6 | Chuẩn bị hai máy điểm quét trong vùng khu quét (máy ảo hoặc container), IP `.11` và `.12`; cài Python, chép chương trình và file cấu hình | CV01 | Ảnh cấu hình IP của hai máy | SV1 (vùng mạng, Ngày 4–6) |
| 5 | 6–7 | Kiểm tra từ hai máy điểm quét đến máy chủ: ping và curl đến cổng API | CV01 | Ảnh ping và curl | SV1, SV3 (địa chỉ dịch vụ, Ngày 6–7) |
| 6 | 7–9 | Kết nối dịch vụ thật của SV3 qua mạng; thêm trạng thái chờ xác nhận và đã xác nhận; đọc lại giao dịch từ máy chủ theo `txn_id` | CV02 | Nhật ký giao dịch từ cả hai điểm | Bước 5; tài khoản thử của SV3 |
| 7 | 10 | Cổng 2: gửi từ cả hai điểm qua mạng, kiểm tra lịch sử ghi đúng điểm quét | CV01, CV02 | Cổng 2 đạt | SV1, SV3 |
| 8 | 10 | Cùng SV3 chạy thử KT1 và KT2, ghi lại giá trị thực tế đã dùng | Chung | Nhật ký thử | Cổng 2 |
| 9 | 11–12 | Hàng đợi cục bộ: ghi file trước khi gửi; lưu `seq_no` vào file; gửi lại đúng `txn_id` khi chưa có xác nhận | CV03 | Mã nguồn hàng đợi | Bước 6 |
| 10 | 12–13 | Gửi lại có kiểm soát: khoảng chờ tăng dần, giới hạn số lần; nhật ký độ trễ, tỉ lệ thành công, số lần gửi lại | CV03 | Nhật ký gửi lại; bảng số đo | Bước 9 |
| 11 | 13–14 | Thử mất mạng thật: chặn cổng bằng tường lửa hoặc tắt dịch vụ; giả lập trễ và mất gói bằng `tc netem` nếu có quyền; thử tắt đột ngột giữa lúc ghi | CV03 | Nhật ký thử; kết quả tắt đột ngột | Bước 10 |
| 12 | 14–15 | Cùng SV4 thử ngắt mạng thật và đối chiếu theo `seq_no`; sửa lỗi | CV03 | Kết quả thử chung | SV4 |
| 13 | 14–16 | Nâng cao: script gửi đồng thời hai điểm quét cùng xuất một mặt hàng; giao SV4 | Nâng cao | Script; nhật ký chạy | Cổng 2 |
| 14 | 15–17 | Viết kịch bản demo: thứ tự thao tác, dữ liệu mẫu, ca lỗi và ca ngắt mạng | Chung | Kịch bản demo | Cổng 3 |
| 15 | 17–19 | Viết báo cáo cá nhân SV2 | Báo cáo | Báo cáo cá nhân | Bước 14 |
| 16 | 19–21 | Tập demo cùng SV3; tập trả lời câu hỏi chuẩn bị của SV2 | Chung | — | SV3 |

---

## 6. SV3 – Máy chủ, lưu trữ, phân quyền và sao lưu

| # | Ngày | Việc theo thứ tự | Mã việc | Sản phẩm hoặc minh chứng | Chờ từ |
| :-: | :---: | :--- | :---: | :--- | :--- |
| 1 | 1 | Họp chốt công nghệ; dựng máy ảo Linux; cập nhật hệ thống; tạo tài khoản quản trị | Chung | Máy ảo khởi động được | Cả nhóm |
| 2 | 1–3 | Cài CSDL; tạo thư mục dữ liệu và thư mục sao lưu tách riêng; tạo người dùng hệ điều hành riêng cho dịch vụ | CV01 | Ảnh cấu trúc thư mục và quyền | Bước 1 |
| 3 | 3–4 | Đặt IP tĩnh theo bảng IP, bật đồng bộ giờ, bật tường lửa mặc định chặn | CV01 | Ảnh cấu hình IP và NTP | SV1 (bảng IP, Ngày 3–4) |
| 4 | 3–5 | Tạo bảng theo sơ đồ của SV1; ràng buộc `UNIQUE` cho `txn_id`; script nạp 100 mặt hàng và tồn đầu; ghi giao dịch và cập nhật tồn trong một transaction; điều kiện chống tồn âm; thử bằng truy vấn trực tiếp | CV01 | File tạo bảng; script nạp dữ liệu; nhật ký truy vấn | Cổng 1 |
| 5 | 5–7 | Viết dịch vụ đồng bộ tối thiểu theo giao ước API: nhận, kiểm tra, ghi, trả xác nhận sau khi commit; đọc tồn và lịch sử | CV02 | Mã dịch vụ | Bước 4; giao ước API |
| 6 | 6–7 | Giao địa chỉ dịch vụ và tài khoản thử cho SV2 | CV02 | Bàn giao | Bước 5 |
| 7 | 6–8 | Cùng SV1 áp dụng quy tắc tường lửa trên máy chủ: điểm quét chỉ vào cổng API, CSDL chỉ nhận từ dịch vụ, SSH chỉ cho quản trị | CV02 | Cấu hình tường lửa trên máy chủ | SV1 (bước 7 của SV1) |
| 8 | 7–9 | Tạo 4 vai trò và 5 tài khoản mẫu (băm mật khẩu); dịch vụ dùng tài khoản CSDL quyền tối thiểu; quyền thư mục dữ liệu và sao lưu ở hệ điều hành; thử `xem01` đọc được nhưng ghi bị từ chối | CV02 | Bảng phân quyền ba tầng; ảnh `xem01` bị từ chối | Bước 5 |
| 9 | 10 | Cổng 2; cùng SV2 chạy thử KT1 và KT2 (chặn trùng ở CSDL) | Chung | Cổng 2 đạt | SV2 |
| 10 | 11–12 | Sao lưu bằng công cụ của CSDL vào vị trí tách riêng; đặt lịch tự động; ghi thời điểm và vị trí | CV03 | File sao lưu mẫu; cấu hình lịch | Bước 8 |
| 11 | 12–13 | Khôi phục vào CSDL tách biệt; đối chiếu số bản ghi, tổng tồn, checksum; đo thời gian khôi phục; viết hướng dẫn khôi phục; giao SV4 | CV03 | Hướng dẫn khôi phục; bảng đối chiếu; thời gian khôi phục | Bước 10 |
| 12 | 14–15 | Cùng SV4 chạy KT3b; sửa chênh lệch nếu có | CV03 | Phần KT3b trong `KT3_PhanQuyen_KhoiPhuc` | SV4 |
| 13 | 14–16 | Nâng cao: script khôi phục thử và so checksum tự động | Nâng cao | Nhật ký; kết quả checksum | Cổng 2 |
| 14 | 15–17 | Chuẩn bị môi trường demo, dữ liệu mẫu, hướng dẫn chạy lại; thử chạy lại trên máy sạch | Chung | Hướng dẫn chạy lại | Cổng 3 |
| 15 | 17–19 | Viết báo cáo cá nhân SV3 | Báo cáo | Báo cáo cá nhân | Bước 14 |
| 16 | 19–21 | Tập demo cùng SV2; tập trả lời câu hỏi chuẩn bị của SV3 | Chung | — | SV2 |

---

## 7. SV4 – Kiểm thử và đo hạ tầng

| # | Ngày | Việc theo thứ tự | Mã việc | Sản phẩm hoặc minh chứng | Chờ từ |
| :-: | :---: | :--- | :---: | :--- | :--- |
| 1 | 1 | Họp; đọc Mục 14 tài liệu quy mô; chốt thư mục minh chứng và quy ước mã `MC` cho cả nhóm | Chung | Quy ước `MC` | Cả nhóm |
| 2 | 1–3 | Lập kế hoạch kiểm thử và mẫu bảng kết quả (sáu mục mỗi ca); chọn công cụ đo CPU, RAM, đĩa, băng thông, thời gian phản hồi | CV01 | Mẫu `BangKetQuaKiemThu`; danh sách công cụ đo | Bước 1 |
| 3 | 4–7 | Soạn chi tiết KT1, KT2, KT3a, ca lỗi và ca kiểm thử truy cập mạng: dữ liệu thử cụ thể, kết quả mong đợi tính trước | CV01, CV02 | Bảng ca kiểm thử (chưa có kết quả thực tế) | Giao ước API và bảng quy tắc truy cập (Ngày 3) |
| 4 | 8–9 | Thử sớm trên bản tích hợp đầu; báo lỗi cho SV2, SV3 | CV01 | Danh sách lỗi | SV2, SV3 |
| 5 | 10–12 | Xác minh Cổng 2; chạy chính thức KT1 và KT2; thử hai điểm quét cùng xuất một mặt hàng | CV01 | `KT1_GiaoDichHopLe`; `KT2_GiaoDichTrung` | Cổng 2 |
| 6 | 11–13 | Kiểm thử truy cập mạng độc lập: từ máy điểm quét thử vào cổng API, cổng CSDL, SSH; ghi kết quả | CV02 | Bảng kết quả truy cập mạng | SV1 (bước 7 của SV1) |
| 7 | 12–14 | Chạy KT3a (`xem01` đọc, thêm, sửa, xóa) và các ca lỗi (mã không tồn tại, số lượng 0 hoặc âm, xuất vượt tồn, gửi lại khi không nhận phản hồi) | CV02 | Phần KT3a trong `KT3_PhanQuyen_KhoiPhuc`; kết quả ca lỗi | Bước 5 |
| 8 | 14–15 | KT3b cùng SV3: khôi phục và đối chiếu; ghi mọi chênh lệch | CV02 | `KT3_PhanQuyen_KhoiPhuc` | SV3 (Ngày 13) |
| 9 | 14–15 | Cùng SV2 thử ngắt mạng thật | CV03 | Kết quả thử | SV2 |
| 10 | 15 | Xác minh Cổng 3: đủ bằng chứng KT1–KT3 và kiểm thử truy cập mạng | Chung | Cổng 3 đạt | Bước 5–8 |
| 11 | 15–17 | Đo tài nguyên thật khi chạy 2 điểm quét; chạy script tải của SV1 (2 rồi 4 tiến trình) nếu có; so với mô hình; viết `DanhGiaMoRong` | CV03 | `DanhGiaMoRong` | SV1 (Ngày 13) |
| 12 | 16–18 | Đối chiếu nhật ký điểm quét với dữ liệu máy chủ theo `seq_no`, tìm giao dịch thiếu hoặc thừa; viết `PhuongAnMatMang` | CV03 | `PhuongAnMatMang`; báo cáo đối chiếu | Bước 9 |
| 13 | 16–18 | Nâng cao: script chạy lại KT1–KT3 bằng một lệnh | Nâng cao | Script; bảng kết quả chạy lại | Cổng 3 |
| 14 | 17–19 | Lập bảng kết quả kiểm thử chung; rà số liệu thống nhất giữa các tài liệu cùng SV1 | Chung | Bảng kết quả chung | Cổng 4 |
| 15 | 18–20 | Viết báo cáo cá nhân SV4 | Báo cáo | Báo cáo cá nhân | Bước 14 |
| 16 | 20–21 | Tập bảo vệ; trả lời câu hỏi chuẩn bị của SV4 | Chung | — | Cả nhóm |

---

## 8. Rủi ro và cách cắt giảm

| Tình huống | Cách xử lý |
| :--- | :--- |
| **Cổng 2 trễ quá 2 ngày** | Bỏ tầng nâng cao trước; SV1 (rảnh sau Ngày 9) hỗ trợ SV3 phần đọc và lịch sử; SV2 dùng dịch vụ giả để thử tiếp |
| **Không dựng được ba vùng mạng riêng (thiếu máy hoặc quyền)** | Dùng container hoặc mạng ảo trên một máy; ghi rõ phần dựng thật và phần chỉ vẽ trên sơ đồ, không ghi là mạng thật |
| **Không có quyền root để dùng `tc netem`** | Giả lập mất mạng bằng tường lửa hoặc tắt dịch vụ; ghi rõ phạm vi mô phỏng |
| **Giao ước API đổi giữa chừng** | SV1 báo cả nhóm ngay, cập nhật giao ước và ghi nhật ký thay đổi |
| **Hàng đợi cục bộ quá nặng** | Làm mức tối thiểu: lưu giao dịch chưa xác nhận vào file và gửi lại đúng `txn_id`; ghi rõ phạm vi, không nói là hệ thống ngoại tuyến hoàn chỉnh |
| **Khôi phục báo lỗi hoặc lệch dữ liệu** | Làm lại với dữ liệu nhỏ; ghi chênh lệch; không ghi “đạt” khi chưa có bằng chứng |
| **Không có công cụ đo tài nguyên** | Dùng công cụ có sẵn của hệ điều hành; nếu vẫn không đo được thì ghi rõ là ước lượng và nêu giả định |
| **Chưa kịp làm tầng nâng cao** | Bỏ qua, ghi rõ “chưa làm” trong báo cáo; lõi có bằng chứng quan trọng hơn |

---

## 9. Nhật ký tiến độ

| Ngày | Thành viên | Việc (số thứ tự) | Trạng thái | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| ........ | ........ | ........ | ........ | ........ |