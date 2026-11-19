# Hướng dẫn chụp lại toàn bộ minh chứng SV2

**Mục tiêu:** chụp lại mới toàn bộ minh chứng SV2 bằng ảnh màn hình thật trên máy chạy thử. Không dùng lại ảnh cũ trong thư mục làm ảnh nộp. Ảnh cũ chỉ để tham khảo nội dung và thao tác.

## 1. Nguyên tắc chụp

1. Thực hiện đúng ca kiểm thử rồi mới chụp màn hình.
2. Dùng **Win + Shift + S** hoặc **Snipping Tool** để chụp cửa sổ đang chạy. Lưu ảnh PNG trực tiếp vào thư mục `E:\CNNT\sinhvien2\evidence\` với tên quy định bên dưới.
3. Không dựng lại màn hình, ghép nội dung, chèn chữ, hoặc sửa kết quả. Có thể sắp xếp cửa sổ và tăng cỡ chữ trước khi chụp để nội dung dễ đọc.
4. Trước khi chụp, kiểm tra ảnh thấy đủ tên chương trình/cửa sổ, lệnh hoặc thao tác, kết quả, mã giao dịch và thời gian khi phù hợp. Không để mật khẩu, token, hay thông tin đăng nhập xuất hiện.
5. Cấu hình hiện hành dùng **cổng 8080**. Ảnh chụp mới phải thể hiện đúng địa chỉ máy chủ/cổng hiện hành; không dùng lại kết quả cũ trên cổng 5000 để chứng minh cấu hình mới.
6. Khi cần kết luận về MySQL, phải để API chạy bằng MySQL thật và chụp thêm truy vấn/đối chiếu ở công cụ CSDL. Kết quả ở chế độ in-memory chỉ chứng minh luồng xử lý API, không chứng minh dữ liệu đã ghi vào MySQL.
7. Sau khi chụp, mở PNG lên kiểm tra chữ có đọc được không. Giữ nguyên ảnh gốc.

## 2. Chuẩn bị trước khi chụp

- Đảm bảo API SV3 đã chạy ở địa chỉ nhóm quy định, cổng `8080`, đăng nhập được và kết nối MySQL thành công.
- Hỏi SV3 tài khoản thử nghiệm cho SP01/SP02; tự nhập mật khẩu ở dấu nhắc, không ghi mật khẩu vào ảnh hay tệp cấu hình.
- Dùng cơ sở dữ liệu thử nghiệm và mã hàng thử nghiệm. Ghi tồn kho ban đầu để có thể đối chiếu.
- Mở các cửa sổ cần dùng trước: API/server, SP01, SP02, PowerShell để xem hàng đợi, và công cụ MySQL nếu ca thử cần xác nhận CSDL.
- Môi trường bạn đang dùng là **một điểm quét trên Windows máy chính và một điểm trong WSL**. Đây là kiểm thử giao tiếp giữa Windows và môi trường WSL trên cùng máy vật lý; không mô tả là hai máy vật lý độc lập.
- Tạo giao dịch mới cho lượt chụp. Không lấy mã giao dịch từ log cũ làm kết quả của lần chạy mới.

## 3. Hướng dẫn khởi chạy mô hình Windows + WSL

Trong mô hình này, API chạy trên **Windows máy chính**, một scanner chạy trên Windows và scanner còn lại chạy trong WSL. Hai scanner là hai môi trường phần mềm trên cùng máy vật lý. Không chạy `chay_thu_2_may_wsl.py` cho ca này: script đó tự khởi động API trong WSL và gắn nhiều IP giả lên cùng card mạng, không phải mô hình Windows + WSL bạn đang dùng.

### Bước 1 — Kiểm tra MySQL và cài thư viện

1. Khởi động MySQL và nhờ SV3 xác nhận API đang dùng MySQL thật. Không tiếp tục với dữ liệu cần chứng minh MySQL nếu API rơi về in-memory.
2. Mở PowerShell ở Windows, chạy:

   ```powershell
   cd E:\CNNT
   py -m pip install -r sinh-vien-3\04_DICH_VU_API\requirements.txt
   py -m pip install -r sinhvien2\requirements.txt
   ```

3. Mở WSL Ubuntu. Nếu báo chưa có `pip` hoặc chưa có `venv`, cài các gói Ubuntu cần thiết:

   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv
   ```

   Tạo môi trường Python riêng và cài thư viện của scanner:

   ```bash
   python3 -m venv ~/.venvs/cnnt-sv2
   source ~/.venvs/cnnt-sv2/bin/activate
   cd /mnt/e/CNNT
   python -m pip install -r sinhvien2/requirements.txt
   ```

   Nếu lệnh tạo môi trường báo thiếu thành phần Python, cài gói đầy đủ rồi tạo lại:

   ```bash
   sudo apt install -y python3-full
   python3 -m venv ~/.venvs/cnnt-sv2
   ```

   Mỗi lần mở cửa sổ WSL mới, kích hoạt lại môi trường trước khi chạy scanner:

   ```bash
   source ~/.venvs/cnnt-sv2/bin/activate
   ```

   Không cần chạy `pip install` ngoài môi trường này.

### Bước 2 — Khởi động API trên Windows

Mở một cửa sổ PowerShell riêng:

```powershell
cd E:\CNNT\sinh-vien-3\04_DICH_VU_API
py app.py
```

Giữ cửa sổ này mở trong lúc kiểm thử. API nghe trên cổng `8080` và bind `0.0.0.0`. Mở một PowerShell thứ hai để kiểm tra cổng:

```powershell
Test-NetConnection 127.0.0.1 -Port 8080
```

Kết quả cần có `TcpTestSucceeded : True`. Nếu không, xem lại API, cấu hình MySQL và thông báo lỗi ở cửa sổ server. Không tắt Windows Firewall để chữa lỗi.

### Bước 3 — Lấy địa chỉ Windows mà WSL truy cập được

Để API đang chạy ở Windows và cửa sổ WSL vẫn mở, mở một cửa sổ **Ubuntu/WSL khác**. Chạy:

```bash
cd /mnt/e/CNNT
WIN_HOST=$(ip route | awk '/default/ {print $3; exit}')
echo "IP Windows nhìn từ WSL: $WIN_HOST"
```

Lệnh này tự lưu địa chỉ vào biến `WIN_HOST`; bạn không cần tự thay placeholder trong lệnh sau. Địa chỉ có thể đổi khi WSL khởi động lại. Kiểm tra API từ WSL:

```bash
curl -i --max-time 3 "http://$WIN_HOST:8080/"
```

Nếu hiện dòng bắt đầu bằng `HTTP/1.1` hoặc `HTTP/`, WSL đã tới được API; mã `404` ở đường dẫn `/` vẫn có nghĩa là đã kết nối được. Nếu hiện `Connection refused` hoặc timeout, dừng ở đây: kiểm tra API còn chạy trên Windows và Windows Firewall có cho phép kết nối TCP 8080 từ WSL chưa.

Ảnh kiểm tra IP và `curl` riêng chỉ là phần kiểm tra mạng. MC07 hoàn chỉnh cần thể hiện thêm scanner Windows và WSL gọi API. Với bộ ảnh hiện tại, hai phần đã được ghép trong `MC_SV2_07_KetNoi_Windows_WSL.png`. Khi chụp lại từ đầu, lưu ảnh cuối cùng bằng tên này. Chú thích báo cáo: Windows–WSL trên cùng máy vật lý.

### Bước 4 — Dùng cấu hình gốc SP01/SP02

Bạn có thể dùng trực tiếp `config_sp01.json` và `config_sp02.json`; không cần tạo file demo.

- SP01 trên Windows: không cần sửa config vì URL loopback sẽ bỏ qua IP nguồn giả. Chạy với `--url http://127.0.0.1:8080`.
- SP02 trong WSL: mở `E:\CNNT\sinhvien2\config_sp02.json` bằng Notepad. Đổi duy nhất `client_ip` từ `192.168.20.12` thành IP WSL của bạn (`172.23.155.222`, theo ảnh vừa gửi). Lưu file. Sau buổi chụp, đổi lại `192.168.20.12`.

### Bước 5 — Chạy hai scanner

**Windows PowerShell** (cửa sổ riêng với API):

```powershell
cd E:\CNNT
py sinhvien2\scanner.py sinhvien2\config_sp01.json --url http://127.0.0.1:8080
```

**Ubuntu/WSL:**

```bash
cd /mnt/e/CNNT
source ~/.venvs/cnnt-sv2/bin/activate
WIN_HOST=$(ip route | awk '/default/ {print $3; exit}')
python3 sinhvien2/scanner.py sinhvien2/config_sp02.json --url "http://$WIN_HOST:8080"
```

Khi scanner hỏi tài khoản:

| Điểm quét | Username | Mật khẩu demo |
|---|---|---|
| SP01 trên Windows | `nhanvien_demo` | `Kho@2026` |
| SP02 trong WSL | `thukho_demo` | `Kho@2026` |

Nhập `nhanvien_demo` hoặc `thukho_demo` ở dòng username; mật khẩu được nhập ẩn nên màn hình không hiện ký tự khi gõ. Cấu hình SP01 hiện mặc định `nhanvien_demo`, tài khoản có trong seed `02_insert_sample_data.sql`; SP02 mặc định `thukho_demo`. Nếu API/MySQL của nhóm đã đổi mật khẩu thì dùng mật khẩu hiện hành do SV3 xác nhận. Windows phải hiện SP01 và `127.0.0.1:8080`; WSL phải hiện SP02 và gateway Windows cổng 8080. Queue/log dùng đường dẫn trong file config gốc, nên có thể đã tồn tại; chúng được giữ lại và `seq_no` tiếp tục từ giá trị hiện tại.

Menu scanner: `1` tạo giao dịch; `2` gửi lại các giao dịch còn chờ; `3` gửi lại một mã giao dịch để kiểm tra chống trùng; `4` xem tồn; `5` xem thống kê/đối chiếu; `6` đăng nhập tài khoản khác; `0` thoát. Để chụp MC01, để cả hai scanner mở đồng thời và thao tác lần lượt trên mỗi cửa sổ.

### Chạy các ca thường dùng

- **MC01 — hai điểm chạy song song:** mở scanner Windows và scanner WSL, đăng nhập cả hai. Tạo một giao dịch ở Windows và một giao dịch ở WSL, để phản hồi của cả hai còn hiện trên màn hình. **Chụp hai cửa sổ cùng lúc**, thấy SP01/SP02, mã giao dịch và kết quả thành công. Lưu `MC_SV2_01_HaiDiemQuetSongSong.png`.
- **MC02 — dữ liệu sai:** ở một scanner chọn `1`; nhập mã hàng để trống, loại giao dịch sai, số lượng `0`, số lượng âm và số lượng `10001`. Chụp sau khi các thông báo từ chối đã hiện, trước khi cuộn mất khỏi màn hình. Lưu `MC_SV2_02_KiemTraDauVao.png`.
- **MC03 — giao dịch hợp lệ:** chọn `4` và tra `SP001` để thấy tồn ban đầu; chọn `1` và tạo giao dịch nhỏ, hợp lệ. Chụp kết quả có `txn_id`, phản hồi thành công và dòng đọc lại giao dịch. Lưu `MC_SV2_03_GiaoDichHopLe_DocLai.png`. Nếu cần chứng minh ghi MySQL, chụp truy vấn tìm đúng `txn_id` và lưu thêm `MC_SV2_03_MySQL_DoiChieu.png`.
- **MC04 — mất kết nối và khôi phục:** dùng một scanner đang mở. Dừng API bằng **Ctrl + C** ở cửa sổ server; scanner chọn `1`, nhập giao dịch thử, chờ hết các lần retry và hiện `CHO_XAC_NHAN`. **Chụp trạng thái chờ ngay lúc này**, lưu `MC_SV2_04_MatMang_HangDoi.png`. Khởi động lại API bằng lệnh ở Bước 2; tại scanner chọn `2`. Khi cùng `txn_id` được xác nhận và đọc lại thành công, chụp lần hai, lưu `MC_SV2_04_KhoiPhuc_GuiLai.png`. Đây là mô phỏng API ngừng hoạt động, không chứng minh mất điện hay đứt mạng vật lý.
- **MC05 — hàng đợi và seq_no:** tại scanner chọn `5` để hiện thống kê. Mở PowerShell/WSL khác xem queue JSONL demo và tệp seq tương ứng. Chụp thống kê cùng nội dung queue/seq dễ đọc; lưu `MC_SV2_05_BangSoDo_DoiChieuSeqNo.png`. Các tệp queue/seq chỉ xuất hiện sau khi scanner ghi giao dịch.
- **MC06 — gửi đồng thời:** khi API chạy, từ PowerShell dùng script kiểm thử:

  ```powershell
  cd E:\CNNT
  py sinhvien2\thu_dong_thoi_xuat.py --base-url http://127.0.0.1:8080 --code SP001 --qty 70
  ```

  Nhập username `thukho_demo`, mật khẩu demo `Kho@2026` khi được hỏi. Chọn `--qty` sao cho hai yêu cầu cộng lại lớn hơn tồn ban đầu. Khi màn hình hiện tồn trước, hai phản hồi và tồn sau, chụp lưu `MC_SV2_06_DongThoiXuat_2DiemQuet.png`. Script tạo hai luồng cùng tiến trình Windows; ảnh này không chứng minh mỗi yêu cầu xuất phát từ một hệ điều hành khác nhau. Nếu cần kết luận MySQL, đối chiếu tồn trong MySQL và lưu thêm `MC_SV2_06_MySQL_DoiChieu.png`.
- **MC08 — log API:** sau khi đã có giao dịch từ scanner Windows và WSL, chụp cửa sổ server đang chạy API; cần thấy log đăng nhập, POST giao dịch và GET đọc lại. Lưu `MC_SV2_08_API_Server.png`.
- **MC09 — scanner Windows/SP01:** trên cửa sổ Windows, để hiện SP01, URL `127.0.0.1:8080`, giao dịch vừa gửi, `txn_id` và kết quả đọc lại. Chụp/lưu `MC_SV2_09_SP01.png`.
- **MC10 — scanner WSL/SP02:** trên cửa sổ WSL, để hiện SP02, URL IP Windows cổng 8080, giao dịch vừa gửi, `txn_id` và kết quả đọc lại. Chụp/lưu `MC_SV2_10_SP02.png`.

### Bước 6 — Dừng sau buổi chụp

- Thoát mỗi scanner bằng `0`.
- Dừng API bằng **Ctrl + C** tại cửa sổ server.
- Khôi phục `client_ip` trong `config_sp02.json` về `192.168.20.12`. Giữ log và queue để đối chiếu; không xóa chúng trước khi kiểm tra.

## 4. Danh sách ảnh cần chụp lại

| Tên ảnh | Thao tác và nội dung bắt buộc phải nhìn thấy |
|---|---|
| `MC_SV2_01_HaiDiemQuetSongSong.png` | Chạy một điểm quét trên Windows máy chính và điểm còn lại trong WSL. Đăng nhập thành công; mỗi điểm thực hiện giao dịch riêng. Chụp thấy hai cửa sổ, SP01/SP02, phản hồi API và mã giao dịch. Ghi chú đây là Windows–WSL trên cùng máy vật lý. |
| `MC_SV2_02_KiemTraDauVao.png` | Tại scanner, lần lượt thử dữ liệu sai: thiếu mã hàng, loại giao dịch không hợp lệ, số lượng 0/âm và số lượng vượt giới hạn. Chụp thấy chương trình từ chối trước khi tạo giao dịch/gửi API. Không để lệnh hoặc kết quả bị khuất. |
| `MC_SV2_03_GiaoDichHopLe_DocLai.png` | Ghi nhận tồn kho ban đầu; tạo một giao dịch hợp lệ; chụp mã giao dịch, HTTP 201/đáp ứng thành công và kết quả GET đọc lại cùng giao dịch. Nếu báo cáo kết luận dữ liệu được lưu MySQL, ghép thêm ảnh truy vấn DB đối chiếu đúng mã giao dịch/tồn kho sau. |
| `MC_SV2_04_MatMang_HangDoi_Retry.png` | Khi API đang hoạt động, tạo giao dịch thử; làm API không thể truy cập theo kịch bản kiểm thử; chụp lỗi kết nối, cùng `txn_id` được giữ trong trạng thái chờ và các lần thử lại. Sau đó khôi phục API, gửi lại hàng đợi, chụp xác nhận thành công và đọc lại cùng giao dịch. Một ảnh chỉ có lỗi mạng mà không có bước khôi phục thì chưa chứng minh gửi lại thành công. |
| `MC_SV2_05_BangSoDo_DoiChieuSeqNo.png` | Chụp nội dung hàng đợi JSONL cùng thống kê scanner. Cần thấy các sự kiện `enqueue/status`, trạng thái giao dịch, `seq_no` tăng liên tục và số giao dịch khớp với hàng đợi. Nếu yêu cầu chứng minh phục hồi sau khởi động lại, chụp trước khi đóng scanner và sau khi mở lại, cho thấy giao dịch còn nguyên. |
| `MC_SV2_06_DongThoiXuat_2DiemQuet.png` | Dùng hai điểm quét gửi yêu cầu xuất đồng thời cho cùng mã hàng với tổng lượng lớn hơn tồn kho ban đầu. Chụp tồn ban đầu, hai yêu cầu, một yêu cầu thành công và yêu cầu còn lại bị từ chối, tồn cuối không âm. Nếu kết luận về MySQL/khóa giao dịch, chụp truy vấn tồn kho trước/sau và xác nhận API thực sự dùng MySQL. |
| `MC_SV2_07_KetNoi_Windows_WSL.png` | Chụp đúng mô hình của bạn: một điểm quét chạy ở Windows, điểm còn lại trong WSL. Chụp `ipconfig` trên Windows, `hostname -I` trong WSL, địa chỉ API cổng 8080 và kết quả hai điểm gọi được API. Ghi chú trong báo cáo: kiểm thử giao tiếp Windows–WSL trên cùng máy vật lý, không phải hai máy độc lập. |
| `MC_SV2_08_API_Server.png` | Chụp cửa sổ terminal đang chạy API ở cổng 8080. Sau khi client chạy, log phải có các yêu cầu đăng nhập, tạo giao dịch và đọc lại với mã phản hồi tương ứng; thấy địa chỉ IP máy khách nếu ca thử có nhiều máy. |
| `MC_SV2_09_SP01.png` | Chụp cửa sổ SP01 trong lần chạy mới: đăng nhập, mã SP01, thao tác giao dịch, `txn_id`, trạng thái gửi và kết quả đọc lại. Đảm bảo URL hiện hành dùng cổng 8080 nếu URL được hiển thị. |
| `MC_SV2_10_SP02.png` | Chụp cửa sổ SP02 trong lần chạy mới với các nội dung tương tự SP01, nhưng phải thấy đúng mã điểm quét SP02 và mã giao dịch riêng. |

## 5. Cách chụp trên Windows

1. Đưa cửa sổ cần chụp lên trước; phóng to cửa sổ hoặc dùng **Win + mũi tên trái/phải** để bố trí hai cửa sổ cạnh nhau.
2. Tăng cỡ chữ terminal nếu cần. Cuộn tới đoạn có cả lệnh chạy và kết quả; không cắt mất tiêu đề/chú thích giúp nhận diện cửa sổ.
3. Nhấn **Win + Shift + S**, chọn vùng chụp phù hợp. Với hai client chạy song song, có thể chọn vùng bao trọn hai cửa sổ nếu cả hai đều đọc được.
4. Mở thông báo ảnh chụp, chọn **Save As**, lưu PNG vào `E:\CNNT\sinhvien2\evidence\` đúng tên trong bảng.
5. Mở file vừa lưu để kiểm tra. Nếu chữ nhỏ, dòng kết quả bị khuất hoặc ảnh cho thấy sai cổng/sai chế độ dữ liệu thì chụp lại sau khi chạy đúng.

## 6. Trình tự chạy gợi ý

Để kết quả dễ đối chiếu, dùng mã hàng thử nghiệm và ghi lại tồn ban đầu, thời điểm chạy, IP máy khách, URL API, chế độ CSDL và mã giao dịch.

1. **Server + MySQL:** xác nhận API ở cổng 8080, MySQL đang kết nối; chụp MC08 sau khi có yêu cầu từ client.
2. **SP01/SP02:** đăng nhập từng điểm quét; thực hiện MC02 rồi MC03; chụp từng client cho MC09/MC10.
3. **Hai điểm quét:** chạy song song để chụp MC01.
4. **Mất mạng:** thực hiện đầy đủ giai đoạn mất kết nối, giữ hàng đợi, khôi phục, gửi lại và đối chiếu; chụp MC04.
5. **Hàng đợi:** kiểm tra JSONL, thống kê, `seq_no`, và nếu cần thì khởi động lại scanner; chụp MC05.
6. **Xuất đồng thời:** đặt tồn thử phù hợp, cho hai client xuất cạnh tranh cùng một mặt hàng, đọc tồn sau; chụp MC06 và đối chiếu MySQL.
7. **Windows–WSL:** chạy một điểm quét trong Windows và điểm kia trong WSL; xác nhận cả hai truy cập API qua cổng 8080. Chụp IP hai môi trường và kết quả. Mô tả đúng phạm vi: hai môi trường chạy trên cùng máy vật lý.

## 7. Kiểm tra trước khi đưa vào báo cáo

- Đủ ảnh MC01–MC10, đúng tên và mở xem được.
- Tất cả ảnh dùng làm kết quả hiện hành đều được chụp lại từ lần chạy mới; ảnh lịch sử trên cổng 5000 không thay thế cho ảnh cổng 8080.
- Mã giao dịch, tồn kho, thời gian và phản hồi nhất quán giữa client, server và CSDL.
- Có chú thích trung thực về môi trường: MySQL hay in-memory; Windows–WSL trên cùng máy hay hai máy/VM độc lập.
- Không kết luận mất điện/kill tiến trình, ACID/khóa MySQL hoặc thử nghiệm hai máy nếu ca chụp không thực hiện đúng điều đó.
- Không xóa ảnh/log cũ trước khi đã kiểm tra ảnh mới và cập nhật báo cáo.
