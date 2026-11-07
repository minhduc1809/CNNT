# Quy mô và định nghĩa ban đầu của dự án
**Thiết kế hạ tầng CNTT cho hệ thống quản lý kho hàng thông minh – Phiếu giao đề 22**

* **Học phần:** Nhập môn công nghệ nền tảng (RIPT1304) – PTIT
* **Lớp:** ........ | **Nhóm:** ........ | **Hạn nộp:** ........
* **Trạng thái:** bản ban đầu, cả nhóm thống nhất trước khi bắt đầu lập trình.

---

## 1. Mục đích tài liệu
Tài liệu ghi lại phạm vi, quy mô và các định nghĩa chung của dự án để bốn thành viên dùng cùng một cách hiểu. Các nội dung ghi là “đề xuất” có thể điều chỉnh khi cả nhóm đồng ý; mọi thay đổi được ghi vào nhật ký ở Mục 15.

---

## 2. Bài toán và mục tiêu
Kho hàng có máy tính, thiết bị quét mã, máy chủ và dữ liệu nhập xuất tồn. Dự án thiết kế và mô phỏng hạ tầng CNTT cho kho này theo mô hình máy chủ tập trung: nhiều điểm quét cùng gửi giao dịch về một máy chủ và một cơ sở dữ liệu duy nhất.

**Mục tiêu theo phiếu giao đề:**
* Thiết kế mạng, máy chủ, lưu trữ, vai trò thủ kho/nhân viên/quản trị và luồng dữ liệu quét mã.
* Mô phỏng 2 điểm quét; lưu giao dịch có mã, thời gian và người thực hiện.
* Triển khai ghi/đọc dữ liệu mẫu, phân quyền và sao lưu; phát hiện dữ liệu trùng hoặc thao tác không hợp lệ.
* Ước lượng tài nguyên khi số điểm quét tăng gấp đôi; đề xuất xử lý mất mạng và đối chiếu dữ liệu sau khôi phục.
* Chứng minh bằng ba ca nghiệm thu KT1–KT3.

**Câu hỏi trọng tâm khi bảo vệ:** *Vì sao quét thành công chưa chứng minh máy chủ đã lưu giao dịch?* Câu trả lời nằm ở Mục 10.

---

## 3. Phạm vi

| Trong phạm vi lõi | Ngoài phạm vi lõi |
| :--- | :--- |
| Nhập kho, xuất kho, tra cứu tồn và lịch sử giao dịch | Kiểm kê và điều chỉnh tồn (chỉ là hướng mở rộng) |
| Hạ tầng dựng chạy thật: máy ảo Linux, 3 vùng mạng ảo, tường lửa theo quy tắc truy cập, đồng bộ giờ | Thiết bị mạng vật lý (switch, router thật) |
| 2 điểm quét giả lập, chạy như hai máy trong vùng khu quét và gọi máy chủ qua mạng | Thiết bị quét thật hoặc RFID, nếu nhóm không có thiết bị |
| Dịch vụ xử lý giao dịch tối thiểu (đồng bộ) và một CSDL dùng chung | Hàng đợi tin nhắn (Redis, BullMQ) và giao diện web trong phần lõi |
| 4 vai trò: quản trị viên, thủ kho, nhân viên, chỉ xem; quyền ở dịch vụ, CSDL và hệ điều hành | Đơn hàng, vận chuyển, thanh toán, nhiều kho |
| Chống giao dịch trùng, kiểm tra đầu vào | Cụm máy chủ dự phòng (chỉ nêu như đề xuất) |
| Sao lưu theo lịch, khôi phục thật và đo thời gian khôi phục | |
| Đo tài nguyên thật, thử ngắt mạng thật, đối chiếu dữ liệu sau khi nối lại | |

---

## 4. Định nghĩa thuật ngữ

| Thuật ngữ | Định nghĩa dùng trong dự án |
| :--- | :--- |
| **Điểm quét** | Thiết bị hoặc chương trình máy khách nhập mã hàng và gửi giao dịch; có mã định danh riêng (`SCAN01`, `SCAN02`…) |
| **Giao dịch** | Một lần nhập hoặc xuất kho của một mặt hàng với số lượng xác định |
| **Mã giao dịch (`txn_id`)** | Mã định danh duy nhất của giao dịch, do máy khách sinh, dùng để nhận ra giao dịch gửi lặp |
| **Tồn kho** | Số lượng hiện có của một mặt hàng, thay đổi theo giao dịch |
| **Chống trùng** | Gửi lại cùng `txn_id` không làm thay đổi tồn lần thứ hai; được bảo đảm ở phía xử lý dữ liệu và CSDL, không chỉ bằng cảnh báo trên giao diện |
| **Xác nhận đã lưu** | Phản hồi của máy chủ sau khi đã ghi và commit giao dịch; khác với việc thiết bị đọc được mã |
| **Ghi nguyên tử** | Ghi giao dịch và cập nhật tồn trong cùng một transaction CSDL; lỗi thì hoàn tác toàn bộ |
| **Phân quyền theo vai trò** | Mỗi vai trò chỉ được thực hiện một số thao tác, được kiểm tra ở dịch vụ xử lý hoặc CSDL |
| **Sao lưu / khôi phục** | Tạo bản sao dữ liệu ở nơi khác và dựng lại dữ liệu từ bản sao đó; chỉ được coi là an toàn khi đã khôi phục thử và đối chiếu |
| **RPO / RTO** | Lượng dữ liệu tối đa chấp nhận mất / thời gian tối đa để khôi phục dịch vụ |
| **VLAN** | Mạng LAN ảo dùng để tách nhóm thiết bị và kiểm soát truy cập |
| **Hàng đợi cục bộ** | Nơi máy khách giữ các giao dịch chưa được máy chủ xác nhận khi mất mạng |

---

## 5. Quy mô hệ thống
Nhóm tách rõ phần triển khai và kiểm thử thật với phần chỉ thiết kế và ước lượng để mọi kết luận trong báo cáo đều có bằng chứng tương ứng.

| Hạng mục | Triển khai và kiểm thử thật | Chỉ thiết kế hoặc ước lượng (kịch bản gấp đôi) |
| :--- | :--- | :--- |
| **Điểm quét** | 2: `SCAN01`, `SCAN02`, chạy như hai máy trong vùng khu quét | 4: thêm `SCAN03`, `SCAN04` |
| **Tài khoản** | 5 tài khoản mẫu: `admin01`, `thukho01`, `nv01`, `nv02`, `xem01` | khoảng 30 (giả định: 1 quản trị, 3 thủ kho, 26 nhân viên) |
| **Mặt hàng** | 100 mặt hàng mẫu | giữ nguyên |
| **Máy chủ** | 1 máy ảo Linux: IP tĩnh, đồng bộ giờ, dịch vụ xử lý giao dịch, CSDL, thư mục sao lưu tách riêng | nâng cấu hình hoặc tách CSDL ra máy riêng |
| **Mạng** | 3 vùng mạng ảo tách riêng với IP theo bảng, tường lửa theo quy tắc truy cập, kiểm chứng bằng ping, curl và kiểm tra cổng | thiết bị mạng vật lý |
| **Dữ liệu giao dịch** | giao dịch phát sinh trong lúc kiểm thử | khối lượng theo mô hình ước lượng ở Mục 13 |

### 5.1. Ba tầng thực hiện
Công việc chia ba tầng để nhóm làm chắc phần bắt buộc trước rồi mới mở rộng. Chỉ phần đã có kết quả chạy mới được ghi vào báo cáo là đã làm.

| Tầng | Nội dung | Điều kiện ghi vào báo cáo |
| :--- | :--- | :--- |
| **Lõi (bắt buộc)** | Hạ tầng dựng thật (máy ảo Linux, 3 vùng mạng, tường lửa); 2 điểm quét; nhập, xuất, tồn; chống trùng; phân quyền; sao lưu theo lịch và khôi phục thật; KT1–KT3; đo tài nguyên và thử ngắt mạng thật | Có minh chứng cho từng ca |
| **Nâng cao (làm khi lõi đã có bằng chứng)** | Script chạy lại KT1–KT3 bằng một lệnh; script gửi đồng thời hai điểm quét cùng xuất một mặt hàng; script tải 2 rồi 4 tiến trình khách; script kiểm tra kết nối cho phép và bị chặn giữa các vùng mạng; script khôi phục thử và so checksum tự động | Chỉ ghi là đã làm khi có kết quả chạy; chưa làm thì ghi rõ |
| **Mở rộng tự chọn (chỉ khi hai tầng trước xong)** | Triển khai và so sánh một phương án thay thế cho một thành phần, cùng tiêu chí và số liệu (ví dụ SQLite với PostgreSQL, hoặc có và không có hàng đợi tin nhắn) | Theo yêu cầu phiếu giao đề |

---

## 6. Thiết kế mạng

### 6.1. Phân vùng mạng

| VLAN | Vai trò | Mạng | Thiết bị |
| :-: | :--- | :--- | :--- |
| **10** | Văn phòng | `192.168.10.0/24` | máy tính của thủ kho và quản trị |
| **20** | Khu quét | `192.168.20.0/24` | `SCAN01` (`.11`), `SCAN02` (`.12`); mở rộng `SCAN03` (`.13`), `SCAN04` (`.14`) |
| **30** | Máy chủ | `192.168.30.0/24` | máy chủ (`.10`); vị trí sao lưu tách riêng (`.20` hoặc ổ/volume riêng) |

### 6.2. Quy tắc truy cập tối thiểu

| Nguồn → Đích | Cho phép | Chặn |
| :--- | :--- | :--- |
| **VLAN 20 → máy chủ** | chỉ cổng API (HTTPS) | SSH, cổng CSDL |
| **VLAN 10 → máy chủ** | cổng web/API | cổng CSDL |
| **Quản trị → máy chủ** | SSH | — |
| **Mọi nguồn → CSDL** | không truy cập trực tiếp, chỉ qua dịch vụ xử lý | — |

### 6.3. Đồng bộ thời gian và mô phỏng
* Máy chủ đồng bộ giờ qua NTP. Thời gian giao dịch lấy theo giờ máy chủ; giờ máy khách chỉ ghi tham khảo.
* Ba vùng mạng được dựng thật bằng mạng ảo của phần mềm ảo hóa hoặc container; mỗi máy có IP tĩnh theo bảng ở 6.1. Báo cáo ghi rõ thành phần nào chạy thật, thành phần nào chỉ được thể hiện trên sơ đồ.
* Mỗi quy tắc ở 6.2 được kiểm chứng hai chiều: truy cập được phép thì thành công, truy cập bị chặn thì thật sự bị chặn (ping, curl, kiểm tra cổng). Kết quả lưu làm minh chứng.

---

## 7. Máy chủ và lưu trữ
* 1 máy ảo Linux chạy dịch vụ xử lý giao dịch và cơ sở dữ liệu. Cấu hình tối thiểu đề xuất: 2 vCPU, 4 GB RAM, 40 GB đĩa; nhóm điều chỉnh theo tài nguyên thực có. Máy có IP tĩnh theo bảng IP, bật tường lửa và đồng bộ giờ.
* Dữ liệu sao lưu nằm ở vị trí khác nơi chứa dữ liệu đang chạy (ổ hoặc volume riêng), quyền hệ điều hành chỉ cho quản trị.
* Dịch vụ xử lý giao dịch giữ tối thiểu và đồng bộ: nhận yêu cầu, kiểm tra, ghi CSDL, trả xác nhận sau khi commit. Hàng đợi tin nhắn (Redis, BullMQ) không nằm trong phần lõi.
* Công nghệ cụ thể (hệ quản trị CSDL, ngôn ngữ dịch vụ, giao diện điểm quét) xem Mục 15.

---

## 8. Dữ liệu và mã giao dịch

| Bảng | Nội dung chính |
| :--- | :--- |
| **`Products`** | mã hàng, tên hàng, đơn vị tính |
| **`Inventory`** | mã hàng, số lượng tồn |
| **`Transactions`** | mã giao dịch, mã hàng, loại nhập/xuất, số lượng, thời gian, người thực hiện, điểm quét, trạng thái |
| **`Users`** | tên tài khoản, vai trò |
| **`ScanPoints`** | mã điểm quét, tên điểm quét |
| **`AuditLog` (tùy chọn)** | nhật ký thao tác nhạy cảm: sao lưu, khôi phục, thao tác bị từ chối |

**Quy ước về mã giao dịch:**
* Do máy khách sinh (UUID hoặc dạng `SCAN01-<ngày>-<số thứ tự>`), có ràng buộc `UNIQUE` trong CSDL.
* Số thứ tự tăng dần theo từng điểm quét để phát hiện giao dịch bị thiếu khi đối chiếu.
* Các giá trị như `TXN001`, `SP001`, `NV01` trong phiếu giao đề chỉ là dữ liệu minh họa; khi kiểm thử phải ghi lại giá trị thực tế đã dùng.

---

## 9. Vai trò và phân quyền

| Thao tác | Quản trị viên | Thủ kho | Nhân viên | Chỉ xem |
| :--- | :---: | :---: | :---: | :---: |
| **Ghi giao dịch nhập/xuất** | không | có | có | không |
| **Xem tồn kho** | có | có | có | có |
| **Xem lịch sử giao dịch** | có | có | chỉ giao dịch của mình | có |
| **Sửa danh mục hàng** | không | có | không | không |
| **Quản lý tài khoản** | có | không | không | không |
| **Sao lưu và khôi phục** | có | không | không | không |

Quyền được kiểm tra ở dịch vụ xử lý, tài khoản CSDL và hệ điều hành (quyền thư mục dữ liệu và sao lưu), không chỉ ẩn nút trên giao diện. Bảng trên là đề xuất; nhóm có thể chỉnh nhưng phải kiểm chứng trên hệ thống.

---

## 10. Nguyên tắc bảo đảm dữ liệu đúng
* **Ghi nguyên tử:** ghi giao dịch và cập nhật tồn trong cùng một transaction; lỗi thì hoàn tác, không để lại trạng thái dở dang.
* **Chống trùng (KT2):** `txn_id` là `UNIQUE`. Gửi lại cùng mã thì máy chủ trả kết quả đã có và không cập nhật tồn lần hai.
* **Chống tồn âm:** xuất kho chỉ thành công khi tồn đủ, được kiểm tra ngay trong câu lệnh cập nhật để hai điểm quét cùng xuất một mặt hàng không làm tồn âm.
* **Kiểm tra đầu vào:** mã hàng phải tồn tại; số lượng là số nguyên lớn hơn $0$; loại giao dịch hợp lệ; người dùng có quyền.
* **Xác nhận sau khi lưu:** giao dịch chỉ là “đã lưu” khi máy chủ commit xong và trả xác nhận. Máy khách giữ trạng thái chờ xác nhận và đã xác nhận.
* **Trả lời câu hỏi trọng tâm:** quét thành công chỉ cho biết thiết bị đọc được mã. Giao dịch có thể mất do lỗi mạng, bị từ chối vì dữ liệu sai, hoặc rollback do lỗi ghi. Chỉ phản hồi xác nhận sau commit, kèm việc đọc lại được bản ghi từ CSDL, mới chứng minh máy chủ đã lưu.

---

## 11. Mất mạng và đối chiếu
* Điểm có thể mất kết nối: máy khách, mạng nội bộ, máy chủ.
* Máy khách giữ giao dịch chưa được xác nhận trong hàng đợi cục bộ.
* Khi có mạng, gửi lại đúng `txn_id` cũ; không sinh mã mới.
* **Đối chiếu sau đồng bộ:** so số lượng giao dịch và số thứ tự theo từng điểm quét giữa máy khách và máy chủ, rồi so tổng tồn. Giao dịch máy chủ đã có thì đánh dấu đã đồng bộ; giao dịch còn thiếu thì gửi bổ sung; giao dịch xung đột thì ghi nhận và báo thủ kho xử lý.
* Nếu chỉ mô phỏng bằng cách ngắt kết nối thử, phải ghi đúng phạm vi mô phỏng, không khẳng định đã xây dựng hệ thống ngoại tuyến hoàn chỉnh.

---

## 12. Sao lưu và khôi phục
* Sao lưu bằng công cụ của hệ quản trị CSDL, chạy theo lịch tự động (ví dụ `cron`); ghi lại thời điểm và vị trí lưu.
* Mục tiêu thiết kế (giả định): RPO không quá 24 giờ, RTO không quá 30 phút. Thời gian khôi phục thật được đo để so với RTO.
* Khôi phục thử vào CSDL tách biệt, không ghi đè dữ liệu đang dùng; đối chiếu số bản ghi giao dịch, tổng tồn và checksum trước và sau.
* Bản sao lưu chưa khôi phục thử thì chưa được coi là bảo đảm an toàn dữ liệu.

---

## 13. Ước lượng tài nguyên khi tăng từ 2 lên 4 điểm quét
Các số dưới đây là giả định minh họa, chưa phải số đo. Nhóm đo thật CPU, RAM, đĩa, băng thông và thời gian phản hồi bằng công cụ của hệ điều hành, so với bảng này, và ghi rõ phần nào là đo, phần nào là ước lượng.

**Giả định:** $20\text{ giao dịch/phút/điểm quét}$; $8\text{ giờ/ngày}$; $300\text{ ngày/năm}$; $300\text{ byte/bản ghi}$ (gồm chỉ mục); hệ số đỉnh $5\text{ lần}$ so với trung bình.

| Chỉ số | 2 điểm quét | 4 điểm quét |
| :--- | :--- | :--- |
| **Giao dịch trung bình** | khoảng $0,67\text{/giây}$ | khoảng $1,33\text{/giây}$ |
| **Giao dịch đỉnh** | khoảng $3,3\text{/giây}$ | khoảng $6,7\text{/giây}$ |
| **Giao dịch mỗi ngày** | khoảng $19.200$ | khoảng $38.400$ |
| **Dữ liệu tăng mỗi ngày** | khoảng $5,8\text{ MB}$ | khoảng $11,5\text{ MB}$ |
| **Dữ liệu tăng mỗi năm** | khoảng $1,7\text{ GB}$ | khoảng $3,5\text{ GB}$ |

**Nhận xét:** với tải này CPU và mạng chưa phải điểm nghẽn. Mức tiêu thụ không tăng hoàn toàn tuyến tính vì tranh chấp khóa trên các mặt hàng bán chạy, chỉ mục lớn dần và việc gửi lại khi lỗi. Khi vượt ngưỡng thì xem xét nâng CPU/RAM, tối ưu truy vấn và chỉ mục, tách CSDL ra máy riêng hoặc thêm bản sao chỉ đọc.

---

## 14. Tiêu chí nghiệm thu và quy ước minh chứng

| Mã | Cách thực hiện | Kết quả mong đợi |
| :--- | :--- | :--- |
| **KT1** | Ghi giao dịch hợp lệ, kiểm tra số liệu tồn mẫu | Giao dịch được ghi nhận; tồn đúng theo phép tính |
| **KT2** | Gửi trùng mã giao dịch | Tồn không thay đổi lần thứ hai |
| **KT3a** | Tài khoản chỉ xem thử sửa dữ liệu | Thao tác bị từ chối |
| **KT3b** | Khôi phục bản sao và đối chiếu | Dữ liệu khớp; chênh lệch (nếu có) được ghi nhận |

Mỗi ca ghi tối thiểu: dữ liệu ban đầu, thao tác, kết quả mong đợi, kết quả thực tế, kết luận, mã minh chứng. Ca chưa chạy ghi “chưa kiểm thử”, không ghi “đạt” trước.

**Quy ước ba mức trạng thái khi viết báo cáo:**
1. **Đã chạy và có minh chứng:** có file, ảnh hoặc nhật ký kèm theo.
2. **Mô phỏng:** chạy trên môi trường giả lập; nêu rõ phạm vi.
3. **Chỉ thiết kế hoặc ước lượng:** chưa triển khai hoặc chưa đo; nêu rõ giả định.

---

## 15. Giả định, hạn chế và các điểm cần nhóm chốt

### 15.1. Quyết định cần chốt trước khi lập trình

| Nội dung | Phương án gợi ý | Người đề xuất | Trạng thái |
| :--- | :--- | :---: | :---: |
| **Hệ quản trị CSDL** | PostgreSQL hoặc MySQL 8 (InnoDB); SQLite để dành cho mở rộng | SV3 | chưa chốt |
| **Cách điểm quét kết nối** | dịch vụ xử lý qua giao thức HTTP | SV1 | chưa chốt |
| **Dạng điểm quét** | chương trình dòng lệnh hoặc giao diện web đơn giản | SV2 | chưa chốt |
| **Định dạng `txn_id`** | UUID hoặc `SCAN01-<ngày>-<số thứ tự>` | SV1 | chưa chốt |
| **Môi trường chạy** | máy ảo Linux cho máy chủ; ba vùng mạng dựng bằng mạng ảo của phần mềm ảo hóa hoặc container (SV1 và SV3 chốt) | SV3 | chưa chốt |
| **Mở rộng tự chọn** | so sánh hai phương án cho một thành phần, ví dụ hai hệ quản trị CSDL | cả nhóm | chưa chốt |

### 15.2. Hạn chế đã biết
* Một máy chủ và một CSDL là điểm lỗi đơn; chấp nhận ở mức mô phỏng nhưng phải nêu thành hạn chế và đề xuất dự phòng.
* Phần 4 điểm quét, 30 tài khoản và các con số ở Mục 13 mới ở mức thiết kế hoặc ước lượng.
* Điểm quét giả lập nhập mã bằng bàn phím, không phải thiết bị quét thật.

### 15.3. Nhật ký thay đổi

| Ngày | Nội dung thay đổi | Người thay đổi | Cả nhóm đã đồng ý |
| :--- | :--- | :--- | :--- |
| ........ | ........ | ........ | ........ |