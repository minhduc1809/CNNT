# Báo cáo nhận xét và đánh giá hồ sơ nhóm Đề tài 22

**Học phần:** Nhập môn Công nghệ nền tảng  
**Nhóm:** 22  
**Thời điểm rà soát:** 19/11/2026 (đã cập nhật trạng thái SV2 sau kiểm thử tích hợp WSL)  
**Phạm vi:** Bốn phần việc cá nhân SV1–SV4, mã nguồn, báo cáo, tài liệu tích hợp và minh chứng hiện có trong workspace.

## 1. Mục đích và cách đọc báo cáo

Báo cáo này đánh giá mức độ hoàn thiện và khả năng bảo vệ của từng phần việc dựa trên hồ sơ đang có. Trọng tâm là tính nhất quán giữa yêu cầu, mã nguồn, kết quả kiểm thử và minh chứng. Một sản phẩm có thể đã được viết nhưng kết quả chỉ được coi là chứng minh khi có thể lần theo dữ liệu, môi trường, thao tác và tệp minh chứng tương ứng.

Đây là rà soát hồ sơ và mã nguồn. Các dịch vụ MySQL, API, Packet Tracer và kịch bản trên máy thật không được khởi chạy lại trong lần rà soát này. Vì vậy, báo cáo phân biệt rõ điều nhìn thấy trong repo với kết luận cần được nhóm xác nhận bằng lần chạy có ghi log.

## 2. Kết luận chung

Nhóm đã có phần lớn cấu phần kỹ thuật: client quét, API, cơ sở dữ liệu, sao lưu/khôi phục, tài liệu thiết kế và kết quả tải/đối chiếu. Tuy nhiên, hồ sơ chưa sẵn sàng để chốt và nộp vì còn ba vấn đề cấp nhóm:

1. **Hợp đồng chuẩn đã được SV1 chốt theo giao ước v1.0 và kế hoạch nhóm.** Cổng chuẩn là 8080; API, client và firewall đã được chuyển về cổng này. Các log/ảnh cũ ghi 5000 là kết quả lịch sử, không đại diện cấu hình hiện hành. Một số tệp vẫn cần rà IP/VLAN và tên trường.
2. **Một số kết quả có thể lấy từ môi trường khác môi trường được mô tả:** API SV3 tự rơi về dữ liệu trong bộ nhớ khi MySQL không kết nối được; một số ca mạng chạy trên cùng máy hoặc là mô phỏng.
3. **Hồ sơ nộp chưa khép kín:** còn minh chứng thiếu/sai vị trí, shortcut thay cho ảnh, chỗ mẫu chưa xóa, checklist chưa đánh dấu; trong repo chưa thấy báo cáo chung hoàn chỉnh và tệp Packet Tracer `.pkt`.

### Mức độ sẵn sàng tương đối

| Thành viên | Vai trò | Nhận xét tổng quát | Mức sẵn sàng hồ sơ |
|---|---|---|---|
| SV1 – Đỗ Thị Liên | Mạng, dữ liệu, giao ước | Đã có giao ước API v1.0 và kế hoạch chuẩn; cần hoàn thiện minh chứng mạng và rà việc các phần triển khai tuân theo chuẩn | Còn minh chứng và kiểm tra tuân thủ |
| SV2 – Trần Lê Minh Đức | Điểm quét, hàng đợi, gửi lại | Mã hàng đợi/xác thực đã được chỉnh; kiểm thử WSL hai client đã có log. Nhóm đã có minh chứng MySQL thật; còn ảnh chụp và một số liên kết minh chứng tích hợp | Gần hoàn thiện phần cá nhân; còn hoàn thiện ảnh và xác định đúng phạm vi từng phép thử |
| SV3 – Phạm Công Mạnh | Máy chủ, CSDL, API, quyền, sao lưu | Đã có bằng chứng MySQL thật, phân quyền và khôi phục; còn rà nhánh fallback, giao ước và truy vết từng lần chạy | Có nền tảng và kiểm chứng MySQL; còn hoàn thiện độ nhất quán |
| SV4 – Nguyễn Mạnh Dũng | Kiểm thử, tải, đối chiếu | Có số đo và đối chiếu hữu ích; một số kết quả mạng và minh chứng chưa đủ sức chứng minh | Gần hoàn thiện nhất, còn việc bắt buộc |

Thứ tự trên phản ánh độ đầy đủ của hồ sơ nhìn thấy, không phải xếp hạng năng lực cá nhân hay điểm số.

## 3. Nhận xét theo từng thành viên

## 3.1. SV1 – Đỗ Thị Liên: thiết kế mạng, mô hình dữ liệu và giao ước

### Điểm đã làm được

- Có bộ tài liệu tương đối rộng: sơ đồ hạ tầng, sơ đồ dữ liệu, sơ đồ luồng, từ điển dữ liệu, giao ước API, ma trận quyền và ước lượng mở rộng.
- Tư duy thiết kế có cơ sở: phân vùng mạng, giới hạn quyền truy cập, lưu trạng thái tồn và lịch sử giao dịch, dùng mã giao dịch để chống ghi trùng.
- Có cấu hình thiết bị, bảng IP, tài liệu phối hợp và kết quả mô phỏng Packet Tracer được đưa vào báo cáo.

### Điểm cần chỉnh

1. **Bằng chứng chưa tương xứng với mức khẳng định.** Yêu cầu có kiểm chứng kết nối giữa các vùng, gồm ping và truy cập dịch vụ/cổng. Trong repo chưa thấy tệp `.pkt`; một số kết quả phối hợp/tải ghi rõ `THU_GIA_LAP`. Cần phân biệt ảnh mô phỏng, kết quả trên máy thật và kết quả do thành viên khác thực hiện.
2. **Cần dùng đúng bản chuẩn SV1 đã chốt.** Một số tệp cấu hình/mô tả còn lệch giữa VLAN, subnet và IP; đây là việc đồng bộ theo bảng IP và kế hoạch đã có, không phải chưa có quyết định thiết kế.
3. **Cổng API hiện hành đã được đồng bộ về chuẩn 8080:** API, cấu hình client, ACL và firewall đang dùng cổng này. Các log/ảnh cũ trên cổng 5000 cần được ghi là kết quả lịch sử; nếu dùng để bảo vệ cấu hình hiện tại thì phải chạy lại.
4. **Đối chiếu tên trường còn báo 4 mục lệch** (`product_code`, `txn_id`, `txn_type`, `username`) trong `SV1_ThietKeMang_DuLieu/doi_chieu/BangDoiChieuTenTruong.md`. Cần chạy lại trên mã cuối và lưu kết quả mới.
5. **Báo cáo cá nhân còn dấu vết mẫu:** các dòng chấm ở mục tự đánh giá và nguồn tham khảo còn chung chung; thông tin ký tên/trình bày cần rà soát. Checklist hồ sơ chung chưa được đánh dấu.

### Việc cần làm

- Dùng giao ước API v1.0, từ điển dữ liệu và bảng IP do SV1 ban hành làm chuẩn; rà cấu hình, mã và báo cáo theo chuẩn đó. Nếu nhóm đã thông qua thay đổi, cập nhật phiên bản và nhật ký thay đổi.
- Bổ sung tệp `.pkt` và ảnh/log thể hiện cấu hình cùng phép thử thực sự đã chạy; nếu chỉ mô phỏng, ghi đúng phạm vi.
- Sửa các mục mẫu còn sót, ghi nguồn tham khảo cụ thể và hoàn tất checklist sau khi các thành viên bàn giao minh chứng.

**Đánh giá giảng viên:** Nền thiết kế tốt và có công sức tổng hợp, nhưng chưa thể xem yêu cầu hạ tầng đã được nghiệm thu chỉ dựa trên sơ đồ và mô tả. Cần nối rõ yêu cầu → cấu hình → phép thử → kết quả.

## 3.2. SV2 – Trần Lê Minh Đức: điểm quét, hàng đợi và đồng bộ

### Điểm đã làm được

- Có chương trình scanner cho SP01/SP02, kiểm tra đầu vào, tạo `txn_id`/`seq_no`, hàng đợi cục bộ, gửi lại và đọc lại giao dịch.
- Mã hiện tại ghi hàng đợi dạng JSONL nối thêm và `fsync`; cập nhật trạng thái được ghi thành sự kiện mới. Bộ đếm `seq_no` được ghi qua tệp tạm rồi thay thế nguyên tử.
- Nhánh đăng nhập hiện dừng khi xác thực thất bại hoặc API không trả token hợp lệ; cấu hình và hướng dẫn phân biệt rõ loopback với kết nối qua IP.
- Có kiểm thử tích hợp WSL mới: hai client ở `.20.11` và `.20.12` đăng nhập, nhập/xuất, nhận HTTP 201, đọc lại HTTP 200 và được đánh dấu `DA_XAC_NHAN`. Log máy chủ/client và hàng đợi được lưu tại `sinhvien2/evidence/MC_SV2_08_*`.
- Báo cáo cá nhân và biên bản MC_SV2_08 đã cập nhật để phân biệt kết quả đã chạy với các giới hạn còn lại.

### Phần còn thiếu trước khi chốt

1. **Ảnh chụp màn hình thật của MC_SV2_08:** hiện đã có log gốc nhưng chưa có ảnh chụp trực tiếp các cửa sổ chạy. SV2 sẽ tự chụp và bổ sung vào thư mục minh chứng.
2. **Phạm vi riêng của lần chạy MC_SV2_08:** hồ sơ nhóm đã có kiểm thử MySQL thật, ví dụ log quyền CSDL `SV4_KiemThu/MC-KT3a-03.txt` và biên bản khôi phục MySQL 9.3 của SV3. Tuy nhiên, chính lần chạy WSL MC_SV2_08 dùng fallback in-memory, nên không thể dùng log đó để nói hai giao dịch SP01/SP02 đã được ghi vào MySQL. Nếu cần ca WSL này làm bằng chứng ghi CSDL end-to-end, có thể chạy lại với API nối MySQL; nếu không, giữ nhãn in-memory và dẫn chiếu riêng bộ minh chứng MySQL đã có.
3. **Phạm vi mạng:** hai IP nguồn được tạo bằng network namespace trong cùng WSL/kernel. Kết quả chứng minh luồng client–server qua IP nguồn riêng trong WSL, chưa chứng minh hai máy/VM độc lập, VLAN hoặc firewall thật.
4. **Mất kết nối và phục hồi:** mã và log hiện có phân biệt rõ mô phỏng gọi cổng đóng với kill tiến trình thật. Chưa có lần chạy mới chứng minh giao dịch sống sót qua dừng tiến trình, khởi động lại và đồng bộ lại cùng `txn_id`.
5. **Ảnh MC_SV2_01–07:** đây là ảnh lịch sử; cần chụp lại các ảnh được dùng khi nộp để khớp mã hiện tại, số lần retry và kết quả thực tế.

### Việc cần làm

- Chụp và lưu ảnh thật cho MC_SV2_08; giữ nguyên log/queue thô làm dữ liệu đối chiếu.
- Gắn rõ minh chứng MySQL thật đang có với ca kiểm thử tương ứng. Chỉ cần chạy lại MC_SV2_08 trên MySQL nếu muốn dùng chính ca WSL hai client làm bằng chứng end-to-end ghi CSDL.
- Nếu tiêu chí yêu cầu, chạy ca phục hồi sau khi dừng tiến trình thật và ca mạng trên hai máy/VM độc lập; ghi rõ điều kiện nếu chỉ mô phỏng.
- Rà lại các ảnh lịch sử được chọn để nộp, bảo đảm không lộ mật khẩu/token và không mô tả WSL là hai máy vật lý.

**Đánh giá giảng viên:** Phần mã SV2 đã tiến bộ rõ và hiện gần hoàn thiện ở chức năng điểm quét, xác thực, hàng đợi và luồng gửi/đọc lại. Phần còn lại chủ yếu là hoàn thiện ảnh và mô tả phạm vi tích hợp. MySQL thật đã có minh chứng trong hồ sơ nhóm; riêng MC_SV2_08 vẫn phải ghi đúng là lần chạy in-memory. Không còn căn cứ để giữ nhận xét cũ rằng SV2 vẫn cần sửa lỗi ghi hàng đợi hoặc token giả trong mã hiện hành.

## 3.3. SV3 – Phạm Công Mạnh: máy chủ, MySQL, API, quyền và sao lưu

### Điểm đã làm được

- Có schema, dữ liệu mẫu, stored procedure, kiểm soát giao dịch, kiểm tra tồn kho, RBAC ở API/CSDL và script sao lưu/khôi phục.
- Hồ sơ đã có minh chứng chạy MySQL thật: `SV4_KiemThu/MC-KT3a-03.txt` ghi kiểm tra quyền và dữ liệu trước/sau; `sinh-vien-3/02_BACKUP_RESTORE/BangDoiChieu_ThoiGianKhoiPhuc.md` ghi phiên bản MySQL 9.3, khôi phục và đối chiếu dữ liệu. Đây là bằng chứng có giá trị cho các ca được nêu, không tự động chứng minh mọi lần chạy API khác đều nối MySQL.
- Báo cáo ghi nhận môi trường hiện tại là Windows 10 trong VMware, khác với kế hoạch máy chủ Linux.

### Điểm cần chỉnh

1. **Cần phân biệt rõ từng ca dùng MySQL hay in-memory.** MySQL 9.3 đã được chạy và có minh chứng ở các ca SV3/SV4 nêu trên. Tuy nhiên `app.py` vẫn có nhánh chuyển sang `_InMemoryConnection` sau lỗi kết nối; biên bản MC_SV2_08 xác nhận chính lần WSL này dùng fallback. Khi nghiệm thu từng ca API, cần ghi backend thực tế để không gán log in-memory thành kết quả MySQL.
2. **Một số phần mã chưa tuân theo bộ tên chuẩn.** Mã/schema SV3 còn tên như `product_id`, `transaction_id`, `transaction_type`, `user_id`, trong khi giao ước/từ điển SV1 v1.0 quy định `product_code`, `txn_id`, `txn_type`, `username`. Kế hoạch đã giao SV1 làm chuẩn; cần cập nhật phía triển khai và chạy lại bảng đối chiếu, không cần quyết định lại bộ tên.
3. **Số lượng ca kiểm thử không nhất quán:** báo cáo cá nhân nêu 25/25, README nêu 26/26. Cần dẫn log cụ thể từ đúng mã cuối, xác định ca nào được tính và sửa các con số còn lại.
4. **Môi trường triển khai khác yêu cầu:** Windows 10/VMware thay cho máy chủ Linux chuyên dụng. Có thể trình bày đây là giới hạn thực nghiệm; không nên viết như đã hoàn tất triển khai Linux. Script Linux trong repo không tự chứng minh script đã chạy.
5. **Đã đồng bộ cổng dịch vụ theo giao ước:** API/client/firewall hiện dùng `8080`, endpoint đăng nhập là `/api/login`. Cần ghi rõ kết quả kiểm thử cũ ở cổng 5000 là lịch sử và rà tiếp các tên trường/IP/VLAN còn lệch.
6. **Dữ liệu seed cần kiểm tra xuyên suốt.** Có các giá trị tồn SP001 khác nhau giữa dữ liệu giả, seed SQL và báo cáo kiểm thử. Mỗi ca cần ghi rõ CSDL, seed, số tồn trước/sau và thời điểm đo.

### Việc cần làm

- Giữ cảnh báo/fail-fast rõ khi API rơi về in-memory; trong báo cáo từng phép thử ghi backend đang dùng.
- Liên kết kết quả MySQL thật hiện có với đúng phiên bản API và ca kiểm thử; bổ sung chạy lại những ca còn cần chứng minh tích hợp API–MySQL.
- Theo giao ước SV1 v1.0, cập nhật các thành phần còn lệch và chạy lại đối chiếu trường; thay con số 25/26 bằng kết quả chứng minh được.
- Nêu rõ Windows/VMware là môi trường đã chạy; nếu không chuyển sang Linux thì ghi hạn chế thay vì nhận đã hoàn thành tiêu chí triển khai Linux.

**Đánh giá giảng viên:** Phần backend đã có minh chứng triển khai MySQL thật, phân quyền và sao lưu/khôi phục. Rủi ro còn lại là nhánh fallback trong API và việc một số phép thử (trong đó có MC_SV2_08) dùng in-memory; cần gắn mỗi kết luận với đúng backend và bộ log của lần chạy đó.

## 3.4. SV4 – Nguyễn Mạnh Dũng: kiểm thử, đo tải và đối chiếu

### Điểm đã làm được

- Có bảng kết quả kiểm thử, script đo CPU/RAM, dữ liệu tải gốc, kết quả đối chiếu sau mất kết nối và báo cáo khôi phục.
- Hồ sơ ghi nhận các phép thử trên MySQL thật, gồm giao dịch, quyền, sao lưu/khôi phục và tải 2/4 điểm quét.
- Báo cáo đối chiếu sau ngắt mạng phân biệt các giao dịch ngày 15/11 với bốn giao dịch cũ ngày 09/11 chưa tìm thấy trong CSDL đang đối chiếu. Không quy bốn giao dịch cũ thành lỗi mất dữ liệu trong lần thử của SV4.
- Báo cáo tự nêu giới hạn hệ thống chạy trên cùng máy và chưa thử mất mạng thật giữa hai máy.

### Điểm cần chỉnh

1. **Không kết luận “Đạt” khi dữ liệu đầu vào còn placeholder.** Ca MANG-02 còn `[điền IP]`; cần điền giá trị từ log thật hoặc đổi kết luận thành “chưa đủ bằng chứng”.
2. **Các ca mạng chưa chứng minh được tường lửa.** Thử từ `127.0.0.1` trên cùng máy không đi qua tường lửa giữa các vùng. Cổng 22 bị từ chối do chưa cài SSH không chứng minh firewall đã chặn. Cần thử từ máy/VM nguồn qua IP đích, ghi trạng thái dịch vụ, luật firewall và kết quả tương ứng.
3. **Đường dẫn minh chứng sai hoặc thiếu:** MC-KT3a-03 có tệp `.txt` ở ngoài thư mục `MinhChung`; các mã MC-L1-01, MC-L2-01, MC-L3-01, MC-L4-04 và MC-LICH-01..03 không thấy tại vị trí được dẫn. MC-KT2-01 và MC-LOI-01 là shortcut `.lnk`, không phải ảnh minh chứng độc lập. Cần đóng gói tệp thật và sửa bảng tham chiếu.
4. **Ngày ghi trong ca L3/L4 cần xác minh:** báo cáo có ngày `2026-09-11`, không khớp các mốc kiểm thử tháng 11 trong hồ sơ khác.
5. **Bản nộp bị trùng:** báo cáo cá nhân và thư mục minh chứng có bản ở cả `docs/` và `SV4_KiemThu/`; cần xác định bản chính cuối cùng để tránh nộp nhầm.
6. **Một vài tuyên bố cần nối bằng chứng:** RPO chưa xác định; kiểm tra firewall/mạng mới ở mức cùng máy hoặc mô phỏng. Không suy rộng kết quả tải một máy thành hiệu năng triển khai phân tán.

### Việc cần làm

- Sửa placeholder và ngày; chỉ đánh dấu Đạt khi có log/ảnh đúng điều kiện.
- Bổ sung/đóng gói minh chứng thật, thay shortcut và cập nhật liên kết từ bảng kiểm thử.
- Tách bản báo cáo cuối khỏi bản nháp/cũ; ghi rõ giới hạn phép thử mạng và đo tải.
- Chốt RPO theo cấu hình sao lưu thực tế, hoặc ghi rõ chưa đo/chưa xác định.

**Đánh giá giảng viên:** Đây là hồ sơ kiểm thử có dữ liệu định lượng và khả năng truy vết tốt nhất nhóm. Điểm yếu chủ yếu là kỷ luật minh chứng và phạm vi suy luận: số đo chỉ chứng minh đúng điều kiện đã chạy, không thay thế kiểm thử firewall hay mạng nhiều máy.

## 4. Vấn đề tích hợp cần cả nhóm cùng xử lý

### 4.1. Tuân thủ hợp đồng hệ thống đã chốt

Kế hoạch nhóm đã giao SV1 chốt giao ước API, từ điển dữ liệu và bảng IP; giao ước API v1.0 hiện ghi rõ phiên bản và quy tắc thay đổi. Vì vậy, nhóm không cần quyết định lại từ đầu. Việc còn lại là đối chiếu mã, cấu hình, kịch bản và báo cáo với bản chuẩn đang được nhóm áp dụng.

| Thành phần | Chuẩn tham chiếu | Việc rà soát còn lại |
|---|---|---|
| API | `SV1_ThietKeMang_DuLieu/05_GiaoUocAPI.md` v1.0 | Cổng, endpoint, mã HTTP và JSON ở SV2/SV3 có theo giao ước không |
| Trường dữ liệu | Từ điển dữ liệu và schema chuẩn của SV1 | Chạy lại bảng đối chiếu trên mã hiện tại; sửa các tên trường lệch |
| IP/VLAN | Bảng IP và cấu hình mạng SV1 | Dùng đúng bản IP/subnet/VLAN chuẩn trong README, cấu hình và ảnh kiểm thử |
| Thay đổi sau khi chốt | Nhật ký `doi_chieu/NhatKyThayDoi.md` | Nếu nhóm đã thống nhất đổi chuẩn, tăng phiên bản và ghi lại; không để các bản cũ/khác nhau cùng được coi là chuẩn |

### 4.2. Phân tầng độ tin cậy của bằng chứng

Khi viết kết luận, nên dùng nhãn rõ ràng:

- **Triển khai thật:** kết quả từ tiến trình/dịch vụ và CSDL thật, có log hoặc ảnh kèm thời gian.
- **Mô phỏng:** Packet Tracer, IP phụ, dịch vụ giả hoặc dữ liệu trong bộ nhớ; ghi đúng mục đích và giới hạn.
- **Thiết kế/chưa kiểm chứng:** sơ đồ, cấu hình mẫu hoặc script chưa có bằng chứng chạy.

Không dùng kết quả mô phỏng để khẳng định firewall, MySQL hoặc mạng thật đã được nghiệm thu.

## 5. Việc chung của nhóm và hồ sơ cuối

- Trong workspace chưa thấy báo cáo chung hoàn chỉnh 12–18 trang; tệp trong `SV1_ThietKeMang_DuLieu/ho_so_chung/` là bản khung và checklist rà soát chưa đánh dấu.
- Chưa thấy tệp Packet Tracer `.pkt` trong danh sách tệp hiện có.
- README gốc cần sửa tên thư mục cũ, bổ sung thông tin nhóm theo yêu cầu và bỏ thông tin mật khẩu demo nếu còn dùng được.
- SV2 đã lưu biên bản, log API/client và hàng đợi MC_SV2_08 trong repo; hiện còn thiếu ảnh chụp màn hình thật của lần chạy WSL.
- Thư mục gốc có `temp_doc.xml` và `tao_v2_sql.py`; cần xác định chúng có thuộc sản phẩm bàn giao không để gói nộp gọn, rõ.
- Chốt một bản báo cáo SV4 và một thư mục minh chứng chuẩn; xác nhận mọi mã minh chứng trong bảng đều mở được.
- Điền phần đóng góp cá nhân và nguồn tham khảo/AI theo đúng công việc thực tế của từng người.

## 6. Thứ tự khuyến nghị để hoàn thiện

### Ưu tiên 1 – Bảo đảm kết quả chạy đúng nguồn dữ liệu

Nhóm đã có bằng chứng MySQL thật trong các ca SV3/SV4. Cần ghi backend của từng ca; MC_SV2_08 là in-memory, còn các kết quả MySQL phải được dẫn tới đúng log/biên bản và dữ liệu đầu vào của lần chạy đó.

### Ưu tiên 2 – Sửa các lỗi có thể làm mất hoặc nhận sai giao dịch

SV2 bổ sung phép thử dừng tiến trình thật để xác minh hàng đợi hiện hành; SV3 xác minh thủ tục giao dịch, khóa và ràng buộc trên MySQL thật. Chạy lại giao dịch trùng, xuất vượt tồn, nhập/xuất đồng thời và khôi phục.

### Ưu tiên 3 – Chốt giao ước và chạy tích hợp

SV1 dùng giao ước v1.0 đã chốt làm chuẩn; SV2/SV3 rà và đồng bộ cấu hình cùng mã theo chuẩn (hoặc ghi thay đổi phiên bản); SV4 cập nhật kịch bản và lưu kết quả đối chiếu mới.

### Ưu tiên 4 – Hoàn tất bằng chứng và hồ sơ

SV4 sửa bảng kết quả và minh chứng; từng thành viên xóa placeholder, sửa số liệu, ghi giới hạn; nhóm hoàn thành báo cáo chung, `.pkt` nếu đề yêu cầu, README và checklist.

## 7. Tiêu chí chốt hồ sơ

Chỉ nên coi hồ sơ sẵn sàng khi các câu sau đều trả lời “có” và tìm được tệp chứng minh:

- Mã cuối, báo cáo và ảnh/log cùng mô tả một endpoint, một bộ trường, một cấu hình IP/cổng và một bộ dữ liệu thử?
- Mỗi kết quả được gắn đúng backend: ca nào đã kiểm chứng trên MySQL thật, ca nào (như MC_SV2_08 hiện tại) chạy in-memory?
- Hàng đợi sống sót qua tình huống dừng tiến trình và sau đó đồng bộ mà không mất/ghi đúp?
- Ca mạng dùng máy/địa chỉ nguồn đích đúng phạm vi cần chứng minh; firewall được kiểm tra với dịch vụ đang chạy?
- Mọi kết luận “Đạt” có đầu vào, thao tác, kết quả thực tế và minh chứng mở được?
- Báo cáo cá nhân, báo cáo chung, README, cấu hình và gói minh chứng đã được rà tên, ngày, đường dẫn và placeholder?

## 8. Nhận xét cuối

Nhóm đã làm được một nguyên mẫu có đủ các lớp chính: client, API, CSDL, phân quyền, lưu ngoại tuyến, sao lưu và kiểm thử. SV2 hiện gần hoàn thiện phần mã và đã có kiểm thử WSL với log; các việc còn lại của bạn chủ yếu là ảnh chụp thật và ghi rõ MC_SV2_08 dùng in-memory, tách biệt với các minh chứng MySQL thật đã có của nhóm. Điểm cần nâng cấp lớn nhất ở cấp nhóm vẫn là **chứng minh các kết quả thuộc đúng hệ thống và môi trường được mô tả**, bảo đảm mã/cấu hình tuân theo giao ước SV1 đã chốt và hoàn thiện minh chứng.

*Báo cáo này là nhận xét kỹ thuật và hồ sơ dựa trên repo hiện tại; không thay thế rubric chấm chính thức hoặc kết quả chạy nghiệm thu của giảng viên.*
