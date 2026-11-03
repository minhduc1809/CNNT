# Mô tả công việc và phân công thành viên
**Thiết kế hạ tầng CNTT cho hệ thống quản lý kho hàng thông minh – Phiếu giao đề 22**

* **Học phần:** Nhập môn công nghệ nền tảng (RIPT1304) – PTIT
* **Lớp:** ........ | **Nhóm:** ........ | **Hạn nộp:** ........
* **Tài liệu đi kèm:** *Quy mô và định nghĩa ban đầu của dự án – Đề 22* (gọi tắt là “tài liệu quy mô”).

---

## 1. Nguyên tắc chia việc
* Tài liệu này chia việc cho bốn thành viên SV1–SV4 theo đúng vai trò trong phiếu giao đề, đồng thời cân bằng khối lượng để không ai nhẹ hoặc nặng hơn rõ rệt.
* Trọng tâm của đề là hạ tầng: mạng, máy chủ, lưu trữ, phân quyền, sao lưu, mất mạng và đo đạc. Phần mềm giữ ở mức tối thiểu, chỉ đủ để chạy thử và chứng minh hạ tầng hoạt động đúng.
* Mỗi người có 3 mã việc (`CV01`–`CV03`) khớp với Mục 2 của mẫu báo cáo cá nhân, cộng một vai trò chung.
* Khối lượng quy đổi ra điểm. Một điểm tương ứng khoảng 2–3 giờ làm việc theo ước tính tương đối. Mỗi người có 20 điểm việc chuyên môn và 5 điểm công việc chung, tổng 25 điểm. Nhóm có thể điều chỉnh điểm khi thực tế khác ước tính (xem Mục 12).
* Mỗi người có phần chạy được hoặc kiểm chứng được và trực tiếp tham gia ít nhất một ca KT1–KT3.
* Mỗi người tự giải thích và thao tác được phần của mình khi bảo vệ. Không nhận phần mà bản thân không thể trình bày.
* Không tự tạo số liệu hoặc minh chứng. Phần chưa làm hoặc chỉ mô phỏng phải ghi đúng như vậy.

---

## 2. Tổng quan phân công

| Thành viên | Vai trò | CV01 | CV02 | CV03 | Việc chuyên môn | Việc chung | Tổng |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **SV1** | Thiết kế mạng và mô hình dữ liệu | Dựng 3 vùng mạng và tường lửa (8) | Mô hình dữ liệu, luồng dữ liệu (6) | Giao ước API, ma trận quyền, mô hình ước lượng (6) | 20 | 5 | **25** |
| **SV2** | Hai điểm quét giả lập | Hai điểm quét như hai máy trong vùng khu quét (7) | Gửi giao dịch, kiểm tra đầu vào, xác nhận đã lưu (6) | Mất mạng thật, hàng đợi, gửi lại có kiểm soát (7) | 20 | 5 | **25** |
| **SV3** | Máy chủ, lưu trữ, quyền, sao lưu | Máy chủ Linux và CSDL (7) | Dịch vụ tối thiểu và phân quyền nhiều tầng (6) | Sao lưu theo lịch, khôi phục thật, đo thời gian khôi phục (7) | 20 | 5 | **25** |
| **SV4** | Kiểm thử và đo hạ tầng | KT1, KT2 (6) | KT3, kiểm thử truy cập mạng, ca lỗi (6) | Đo tài nguyên thật, ngắt mạng, đối chiếu (8) | 20 | 5 | **25** |

So với bản đầu của tài liệu này, trọng tâm chuyển sang hạ tầng chạy thật: SV1 dựng 3 vùng mạng và tường lửa, SV3 cấu hình máy chủ và phân quyền nhiều tầng (dịch vụ phần mềm giữ tối thiểu), SV2 thử mất mạng thật ở phía điểm quét, SV4 đo tài nguyên thật và kiểm thử truy cập mạng. Điểm đã được cân lại để mỗi người vẫn có 20 điểm chuyên môn.

---

## 3. SV1 – Mạng và thiết kế dữ liệu
**Mục tiêu:** dựng thật hạ tầng mạng và tạo bản thiết kế chung để SV2, SV3 triển khai thống nhất; cung cấp mô hình ước lượng cho SV4 đối chiếu.

| Mã việc | Nội dung công việc | Điểm | Sản phẩm bàn giao | Tiêu chí hoàn thành |
| :--- | :--- | :-: | :--- | :--- |
| **CV01 – Dựng 3 vùng mạng và tường lửa** | Vẽ sơ đồ và lập bảng IP cho 3 VLAN; dựng ba vùng mạng thật bằng phần mềm ảo hóa hoặc container (mạng ảo tách riêng, IP tĩnh); cấu hình định tuyến giữa các vùng và đồng bộ giờ NTP; áp dụng quy tắc truy cập bằng tường lửa cùng SV3; kiểm chứng hai chiều (được phép thì qua, bị chặn thì chặn) bằng ping, curl, kiểm tra cổng; ghi rõ phần dựng thật và phần chỉ vẽ | 8 | `01_SoDoHaTang.png`; bảng IP; file cấu hình mạng và tường lửa; bảng kết quả kiểm tra kết nối | Mỗi quy tắc ở tài liệu quy mô có kết quả kiểm chứng; điểm quét vào được cổng API nhưng không vào được cổng CSDL và SSH; sơ đồ khớp cấu hình thực tế |
| **CV02 – Mô hình dữ liệu và luồng dữ liệu** | Vẽ sơ đồ quan hệ cho các bảng `Products`, `Inventory`, `Transactions`, `Users`, `ScanPoints` (`AuditLog` tùy chọn); lập từ điển dữ liệu (tên trường, kiểu, ràng buộc); vẽ sơ đồ trình tự quét → gửi → kiểm tra → lưu → cập nhật tồn → phản hồi; nêu quy tắc giao dịch | 6 | `02_MoHinhDuLieu.png`; `03_ThietKeDuLieu`; sơ đồ luồng dữ liệu | Tên trường đã đối chiếu với mã của SV2 và SV3 và ghi lại kết quả; sơ đồ luồng có nhánh lỗi và nhánh giao dịch trùng |
| **CV03 – Giao ước API, ma trận quyền, mô hình ước lượng** | Quy định định dạng yêu cầu/phản hồi cho ghi giao dịch, đọc tồn, đọc lịch sử; liệt kê mã lỗi; lập ma trận quyền (dịch vụ, CSDL, hệ điều hành); xây mô hình ước lượng khi tăng từ 2 lên 4 điểm quét: công thức, giả định, kết quả | 6 | Tài liệu giao ước API; ma trận quyền; bảng ước lượng có công thức | SV2 và SV3 dùng được mà không phải hỏi lại; mọi con số ước lượng ghi giả định và ghi rõ chưa đo |

* **Việc chung (2 điểm):** tổng hợp hồ sơ chung (sắp xếp tài liệu, thống nhất thuật ngữ, mục lục, danh mục minh chứng).
* **Phối hợp:** giao thiết kế cho SV2, SV3 ở giai đoạn 1; giao mô hình ước lượng cho SV4; cùng SV3 thống nhất cấu hình tường lửa trên máy chủ; nhận phản hồi khi tên trường hoặc giao ước không khớp.
* **Chuẩn bị bảo vệ:**
  1. Vì sao chia ba vùng mạng, và mỗi quy tắc tường lửa bảo vệ điều gì?
  2. Làm sao chứng minh điểm quét không vào được cổng CSDL?
  3. Hai điểm quét dùng chung cơ sở dữ liệu như thế nào?
  4. Vì sao không chỉ lưu số lượng tồn mà còn phải lưu lịch sử giao dịch?
  5. Nếu số điểm quét tăng từ 2 lên 4, những thành phần nào cần xem xét nâng cấp và dựa trên giả định nào?

---

## 4. SV2 – Hai điểm quét giả lập
**Mục tiêu:** xây dựng hai điểm quét chạy như hai máy trong vùng khu quét, gửi giao dịch qua mạng đến máy chủ và chứng minh hành vi đúng khi mất mạng.

| Mã việc | Nội dung công việc | Điểm | Sản phẩm bàn giao | Tiêu chí hoàn thành |
| :--- | :--- | :-: | :--- | :--- |
| **CV01 – Hai điểm quét SCAN01, SCAN02 như hai máy trong vùng khu quét** | Chương trình dòng lệnh chạy trên hai máy (máy ảo hoặc container) trong vùng khu quét, IP theo bảng (`.11` và `.12`); mỗi máy một file cấu hình; nhập mã hàng, loại giao dịch, số lượng, người thực hiện; sinh `txn_id` và `seq_no`; kiểm tra kết nối đến máy chủ bằng ping và curl | 7 | Mã nguồn và file cấu hình; ảnh cấu hình IP; kết quả ping và curl; ảnh giao diện từng điểm | Hai điểm chạy cùng lúc; giao dịch đi qua mạng chứ không phải localhost; mỗi giao dịch ghi đúng điểm quét; không có CSDL riêng cho từng điểm |
| **CV02 – Gửi giao dịch, kiểm tra đầu vào, xác nhận đã lưu** | Kiểm tra mã hàng không trống, số lượng hợp lệ; gửi giao dịch; hiển thị kết quả (thành công, mã hàng không tồn tại, không đủ hàng, trùng, không có quyền, lỗi kết nối); giữ trạng thái chờ xác nhận và đã xác nhận; đọc lại giao dịch từ máy chủ để kiểm tra đã lưu | 6 | Mã nguồn; nhật ký giao dịch từ cả hai điểm; ảnh kết quả thử mã sai | Thông báo thành công chỉ hiện sau phản hồi xác nhận từ máy chủ; đã thử mã sai, số lượng 0 và số âm |
| **CV03 – Mất mạng thật, hàng đợi và gửi lại có kiểm soát** | Giữ giao dịch chưa xác nhận trong hàng đợi (ghi file trước, gửi sau); gửi lại đúng `txn_id` với khoảng chờ tăng dần và giới hạn số lần; lưu `seq_no` vào file; thử mất mạng thật (chặn cổng bằng tường lửa, tắt dịch vụ, hoặc giả lập trễ và mất gói bằng `tc netem` nếu có quyền); thử tắt đột ngột giữa lúc ghi; ghi nhật ký gửi lại và số đo (độ trễ, tỉ lệ thành công, số lần gửi lại) | 7 | Mã nguồn hàng đợi; nhật ký gửi lại; kết quả thử tắt đột ngột; bảng số đo | Sau nối lại, giao dịch không mất và không bị ghi hai lần; nhật ký thể hiện khoảng chờ tăng dần; phạm vi mô phỏng được ghi rõ |

* **Việc chung (2 điểm):** soạn kịch bản demo và trình diễn hai điểm quét khi bảo vệ.
* **Phối hợp:** dùng đúng tên trường và giao ước API của SV1; kết nối dịch vụ của SV3; cùng SV3 thực hiện KT1, KT2; cùng SV4 thử ngắt mạng thật và đối chiếu theo `seq_no`; nhận địa chỉ IP của hai máy điểm quét từ SV1.
* **Chuẩn bị bảo vệ:**
  1. Hai điểm quét khác nhau ở những thông tin nào, và máy khách gửi dữ liệu đến đâu qua mạng?
  2. Làm thế nào biết giao dịch đã được lưu chứ không chỉ mới quét thành công?
  3. Khi mất kết nối, máy khách xử lý thế nào, và vì sao gửi lại phải giữ nguyên `txn_id`?
  4. Vì sao khoảng chờ giữa các lần gửi lại tăng dần?
  5. Nếu hai điểm quét cùng gửi giao dịch gần như đồng thời, điều gì có thể xảy ra?

---

## 5. SV3 – Máy chủ, lưu trữ, phân quyền và sao lưu
**Mục tiêu:** dựng máy chủ, cơ sở dữ liệu, phân quyền nhiều tầng và sao lưu theo lịch; dịch vụ phần mềm giữ ở mức tối thiểu.

| Mã việc | Nội dung công việc | Điểm | Sản phẩm bàn giao | Tiêu chí hoàn thành |
| :--- | :--- | :-: | :--- | :--- |
| **CV01 – Máy chủ Linux và CSDL** | Dựng máy ảo Linux: IP tĩnh theo bảng IP, đồng bộ giờ, người dùng hệ điều hành riêng cho dịch vụ, thư mục dữ liệu và thư mục sao lưu tách riêng; cài CSDL; tạo bảng theo mô hình của SV1; ràng buộc `UNIQUE` cho `txn_id` và chống tồn âm; nạp 100 mặt hàng và tồn đầu | 7 | File cấu hình máy chủ; file tạo bảng và nạp dữ liệu; mô tả cơ chế chống trùng, chống tồn âm | Máy chủ truy cập được qua IP đã đặt; gửi trùng không đổi tồn; xuất vượt tồn bị từ chối; lỗi giữa chừng không để dữ liệu dở dang |
| **CV02 – Dịch vụ tối thiểu và phân quyền nhiều tầng** | Viết dịch vụ đồng bộ tối thiểu theo giao ước API của SV1 (nhận yêu cầu, kiểm tra, ghi giao dịch và cập nhật tồn trong một transaction, trả xác nhận sau khi commit; đọc tồn và lịch sử); tạo 4 vai trò và 5 tài khoản mẫu (băm mật khẩu); phân quyền ở ba tầng: dịch vụ, tài khoản CSDL (quyền tối thiểu), hệ điều hành (quyền thư mục dữ liệu và sao lưu); không dùng hàng đợi tin nhắn trong phần lõi | 6 | Mã dịch vụ; bảng phân quyền thực tế ba tầng; ảnh `xem01` bị từ chối; ảnh quyền thư mục | `xem01` đọc được nhưng thêm, sửa, xóa bị từ chối; dịch vụ dùng tài khoản CSDL có quyền tối thiểu, không dùng tài khoản quản trị; mỗi vai trò đã thử ít nhất một thao tác được phép và một thao tác bị cấm |
| **CV03 – Sao lưu theo lịch, khôi phục thật, đo thời gian khôi phục** | Sao lưu bằng công cụ của hệ quản trị CSDL vào vị trí tách riêng, chạy theo lịch tự động (ví dụ `cron`); ghi thời điểm và vị trí; khôi phục vào CSDL tách biệt; đối chiếu số bản ghi, tổng tồn, checksum; đo thời gian khôi phục thật để so với RTO giả định; viết hướng dẫn khôi phục | 7 | File sao lưu mẫu; cấu hình lịch; hướng dẫn khôi phục; bảng đối chiếu trước và sau; thời gian khôi phục đã đo | Đã khôi phục thật chứ không chỉ có file sao lưu; có ít nhất một bản sao lưu do lịch tự động tạo; mọi chênh lệch được ghi lại; thời gian khôi phục có số đo |

* **Việc chung (2 điểm):** chuẩn bị môi trường, dữ liệu mẫu và hướng dẫn chạy lại toàn hệ thống cho buổi bảo vệ.
* **Phối hợp:** nhận thiết kế từ SV1; cung cấp địa chỉ dịch vụ và tài khoản thử cho SV2; bàn giao CSDL, bản sao lưu và hướng dẫn khôi phục cho SV4; cùng SV1 áp dụng quy tắc tường lửa trên máy chủ.
* **Chuẩn bị bảo vệ:**
  1. Phân quyền ở ba tầng (dịch vụ, CSDL, hệ điều hành) khác nhau thế nào, và vì sao cần cả ba?
  2. Vì sao mã giao dịch phải duy nhất?
  3. Sao lưu khác gì với lưu dữ liệu trên máy chủ, và vì sao đặt ở vị trí khác?
  4. File sao lưu tồn tại nhưng không khôi phục được thì có an toàn không? Thời gian khôi phục thật là bao nhiêu?
  5. Làm sao xác nhận dữ liệu sau khôi phục không thiếu hoặc bị ghi hai lần?

---

## 6. SV4 – Kiểm thử, xử lý lỗi và khả năng mở rộng
**Mục tiêu:** trực tiếp chạy thử hệ thống, thu thập bằng chứng cho KT1–KT3, kiểm thử truy cập mạng và đo tài nguyên thật. SV4 không chỉ viết đánh giá trong báo cáo mà phải thực sự chạy kiểm thử.

| Mã việc | Nội dung công việc | Điểm | Sản phẩm bàn giao | Tiêu chí hoàn thành |
| :--- | :--- | :-: | :--- | :--- |
| **CV01 – Kiểm thử nhất quán KT1, KT2** | Lập kế hoạch và dữ liệu thử thực tế; KT1: ghi tồn đầu, gửi giao dịch hợp lệ, đọc lại và so với phép tính; KT2: gửi lại cùng `txn_id`, đối chiếu lịch sử và tồn trước/sau; thử hai điểm quét cùng xuất một mặt hàng | 6 | `KT1_GiaoDichHopLe`; `KT2_GiaoDichTrung`; bảng kết quả kiểm thử | Mỗi ca đủ sáu mục: điều kiện đầu, thao tác, kết quả mong đợi, kết quả thực tế, kết luận, mã minh chứng; số liệu là số thực tế |
| **CV02 – KT3, kiểm thử truy cập mạng và ca lỗi** | KT3a: đăng nhập `xem01`, thử đọc, thêm, sửa, xóa; KT3b: cùng SV3 khôi phục và đối chiếu; kiểm thử độc lập các quy tắc truy cập của SV1 (điểm quét vào được cổng API, không vào được cổng CSDL và SSH); ca lỗi: mã hàng không tồn tại, số lượng 0 hoặc âm, xuất vượt tồn, gửi lại do không nhận phản hồi | 6 | `KT3_PhanQuyen_KhoiPhuc`; `BangKetQuaKiemThu` (gồm kết quả kiểm thử truy cập mạng) | Mọi chênh lệch được ghi lại; không kết luận “đạt” khi chưa có bằng chứng |
| **CV03 – Đo tài nguyên thật, ngắt mạng, đối chiếu** | Đo CPU, RAM, đĩa, băng thông và thời gian phản hồi trên máy chủ bằng công cụ của hệ điều hành khi chạy 2 điểm quét (và chạy script tải của SV1 với 2 rồi 4 tiến trình nếu có); so với mô hình của SV1; cùng SV2 thử ngắt mạng thật; đối chiếu nhật ký điểm quét với dữ liệu máy chủ theo `seq_no` để tìm giao dịch thiếu hoặc thừa; viết phương án mất mạng; đề xuất giải pháp khi vượt ngưỡng | 8 | `DanhGiaMoRong`; `PhuongAnMatMang`; báo cáo đối chiếu | Số đo ghi rõ công cụ, thời điểm và điều kiện; phần chỉ ước lượng ghi rõ giả định; sau ngắt mạng có báo cáo đối chiếu giao dịch thiếu hoặc thừa |

* **Việc chung (2 điểm):** rà soát số liệu thống nhất giữa các tài liệu và lập bảng kết quả kiểm thử chung của nhóm.
* **Phối hợp:** ở giai đoạn đầu viết kế hoạch kiểm thử và chuẩn bị dữ liệu thử; nhận hệ thống từ SV2, SV3; nhận mô hình ước lượng từ SV1; báo lỗi cho người phụ trách để sửa rồi kiểm tra lại.
* **Chuẩn bị bảo vệ:**
  1. Làm sao phân biệt giao dịch đã gửi với giao dịch đã được máy chủ lưu?
  2. Làm sao chứng minh tồn kho không bị cập nhật hai lần?
  3. Nếu hai điểm quét cùng xuất một mặt hàng, hệ thống ngăn tồn âm thế nào?
  4. Khi tăng gấp đôi số điểm quét, số đo thật khác ước lượng ở đâu và vì sao?
  5. Sau mất mạng, đối chiếu nhật ký điểm quét với dữ liệu máy chủ thế nào?

---

## 7. Công việc chung của mỗi thành viên (5 điểm)

| Hạng mục | Điểm | Nội dung |
| :--- | :-: | :--- |
| **Báo cáo cá nhân** | 3 | Điền mẫu báo cáo cá nhân theo thực tế: nhiệm vụ, cách làm, minh chứng có mã `MC`, kết quả kiểm thử, một vấn đề có thật đã gặp, tiến độ, tự đánh giá, nguồn tham khảo và công cụ AI đã dùng |
| **Vai trò chung** | 2 | SV1 tổng hợp hồ sơ chung; SV2 kịch bản demo; SV3 môi trường và hướng dẫn chạy lại; SV4 rà soát số liệu và bảng kết quả kiểm thử chung |

---

## 8. Ai làm gì trong từng ca nghiệm thu

| Ca | Nội dung | Thực hiện | Xác minh |
| :--- | :--- | :--- | :--- |
| **KT1** | Giao dịch hợp lệ, kiểm tra tồn | SV2 gửi, SV3 lưu | SV4 |
| **KT2** | Gửi trùng `txn_id`, tồn không đổi lần hai | SV2 gửi, SV3 chặn ở CSDL | SV4 |
| **KT3a** | `xem01` sửa dữ liệu bị từ chối | SV3 | SV4 |
| **KT3b** | Khôi phục bản sao và đối chiếu | SV3 | SV4 |
| **Truy cập mạng (bổ sung)** | Điểm quét vào được cổng API, không vào được cổng CSDL và SSH | SV1 | SV4 |

SV1 tham gia bằng cách đối chiếu tên trường và giao ước giữa SV2, SV3 và chứng minh các quy tắc truy cập mạng; kết quả ghi vào báo cáo cá nhân, không phải điều kiện đạt của KT1–KT3.

---

## 9. Bàn giao và phụ thuộc

| Từ | Đến | Bàn giao | Giai đoạn |
| :--- | :--- | :--- | :---: |
| **SV1** | SV2, SV3 | mô hình dữ liệu, giao ước API, ma trận quyền, bảng IP | 1 |
| **SV1** | SV2, SV3 | ba vùng mạng chạy được: IP tĩnh, tường lửa, kết quả kiểm tra kết nối | 2 |
| **SV3** | SV2 | địa chỉ dịch vụ, tài khoản thử | 2 |
| **SV2** | SV4 | hai điểm quét chạy được qua mạng và hướng dẫn thao tác | 2 sang 3 |
| **SV3** | SV4 | CSDL có dữ liệu mẫu, bản sao lưu, lịch sao lưu, hướng dẫn khôi phục | 3 |
| **SV1** | SV4 | mô hình ước lượng tài nguyên, bảng quy tắc truy cập để kiểm thử độc lập | 3 |
| **SV4** | cả nhóm | lỗi phát hiện và kết quả kiểm thử, cập nhật liên tục | 2 đến 4 |

---

## 10. Tiến độ gợi ý

| Giai đoạn | Việc chính | Kết quả cần có | Hạn |
| :---: | :--- | :--- | :--- |
| **1** | SV1 thiết kế, chốt giao ước và bảng IP; cả nhóm chốt công nghệ; SV3 dựng máy chủ Linux; SV2 dựng khung điểm quét; SV4 viết kế hoạch và dữ liệu thử | Sơ đồ, mô hình dữ liệu, giao ước API, máy chủ có IP tĩnh | ........ |
| **2** | SV1 dựng ba vùng mạng và tường lửa; SV2 làm CV01–CV02 (điểm quét gọi qua mạng); SV3 làm CV01–CV02; tích hợp chuỗi gửi, lưu, đọc lại qua mạng | Gửi và lưu được giao dịch từ hai điểm quét qua mạng, tường lửa chạy đúng quy tắc | ........ |
| **3** | SV3 làm CV03; SV2 làm CV03; SV4 chạy KT1–KT3 và kiểm thử truy cập mạng; SV1 giao mô hình ước lượng | Bằng chứng KT1–KT3, sao lưu khôi phục thật | ........ |
| **4** | SV4 đo tài nguyên thật, đối chiếu sau ngắt mạng và hoàn thiện phương án mất mạng; SV1 tổng hợp hồ sơ; mọi người hoàn thiện báo cáo cá nhân và chuẩn bị bảo vệ | Hồ sơ chung, báo cáo cá nhân, minh chứng | ........ |

---

## 11. Tầng nâng cao và mở rộng tự chọn
Công việc chia ba tầng. **Lõi** là `CV01`–`CV03` ở trên và là phần tính vào 25 điểm. **Nâng cao** chỉ làm khi lõi đã có bằng chứng. **Mở rộng tự chọn** chỉ làm khi hai tầng trước đã xong. Hai tầng sau không tính vào 25 điểm, và chỉ được ghi vào báo cáo là đã làm khi có kết quả chạy.

### 11.1. Tầng nâng cao (khoảng 2 điểm mỗi người)

| Thành viên | Việc | Kết quả để ghi nhận |
| :--- | :--- | :--- |
| **SV1** | Viết script tải chạy 2 rồi 4 tiến trình khách theo mô hình ước lượng; script kiểm tra kết nối cho phép và bị chặn giữa các vùng mạng | Script, tham số tải, kết quả chạy |
| **SV2** | Viết script gửi đồng thời hai điểm quét cùng xuất một mặt hàng | Nhật ký chạy, tồn không âm |
| **SV3** | Viết script khôi phục thử vào CSDL tách biệt và so checksum tự động sau mỗi lần sao lưu | Nhật ký, kết quả checksum |
| **SV4** | Viết script chạy lại KT1–KT3 bằng một lệnh; chạy script tải của SV1 để lấy số đo | Bảng kết quả chạy lại, số đo thực tế |

### 11.2. Mở rộng tự chọn
Nếu nhóm làm phần mở rộng (triển khai và kiểm thử một phương án thay thế cho một thành phần, so sánh theo cùng tiêu chí và số liệu), chia việc để giữ cân bằng, mỗi người khoảng 3 điểm thêm:

| Thành viên | Việc |
| :--- | :--- |
| **SV3** | triển khai phương án thay thế (ví dụ hệ quản trị CSDL khác) |
| **SV2** | chỉnh máy khách để kết nối phương án thay thế |
| **SV4** | chạy cùng bộ kiểm thử và đo cùng chỉ số trên cả hai phương án |
| **SV1** | lập tiêu chí và bảng so sánh, viết kết luận |

---

## 12. Quy tắc phối hợp
* Không tự tạo số liệu hoặc minh chứng; ca chưa chạy ghi “chưa kiểm thử”.
* Chốt cấu trúc dữ liệu và giao ước API trước khi lập trình; mọi thay đổi sau đó phải báo cả nhóm và ghi vào nhật ký.
* Trong báo cáo cá nhân, ghi rõ phần tự làm và phần được hỗ trợ; chỉ kê khai việc mình thực sự thực hiện.
* Khi một mã việc vượt quá dự kiến, cả nhóm họp để điều chuyển điểm hoặc việc và ghi vào nhật ký, không để một người gánh phần dồn lại.
* Không đưa mật khẩu hoặc dữ liệu cá nhân thật vào tài liệu và minh chứng.
* Tài liệu này chia cho 4 thành viên. Nếu nhóm có 5 người, cần bổ sung phần việc SV5 theo hướng dẫn chung của giảng viên.

---

## 13. Nhật ký thay đổi phân công

| Ngày | Thay đổi | Lý do | Cả nhóm đã đồng ý |
| :--- | :--- | :--- | :--- |
| ........ | ........ | ........ | ........ |