#!/bin/bash
# ==============================================================================
# SCRIPT CẤU HÌNH PHÂN QUYỀN 3 TẦNG TRÊN MÁY CHỦ LINUX (SV3 - MÃ VIỆC CV02)
# ==============================================================================
# Tầng 1: Dịch vụ API (RBAC & Chạy dưới user không đặc quyền)
# Tầng 2: CSDL MySQL (User wh_store chỉ có quyền tối thiểu SELECT + EXECUTE)
# Tầng 3: Hệ điều hành (Tách biệt quyền thư mục dữ liệu và thư mục sao lưu)
# ==============================================================================

set -e

echo "=== [1/5] TẠO CÁC USER HỆ ĐIỀU HÀNH CHUYÊN BIỆT KHÔNG ĐẶC QUYỀN ==="
# User chạy dịch vụ API
if ! id -u wh_service >/dev/null 2>&1; then
    sudo useradd -r -s /usr/sbin/nologin -d /opt/smart_warehouse_api -m wh_service
    echo "✓ Đã tạo system user 'wh_service'"
fi

# User quản lý sao lưu tự động
if ! id -u wh_backup >/dev/null 2>&1; then
    sudo useradd -r -s /bin/bash -d /var/backups/warehouse -m wh_backup
    echo "✓ Đã tạo system user 'wh_backup'"
fi

echo "=== [2/5] THIẾT LẬP THƯ MỤC VÀ PHÂN QUYỀN TẦNG HỆ ĐIỀU HÀNH ==="
# Thư mục chứa mã nguồn API
sudo mkdir -p /opt/smart_warehouse_api
sudo mkdir -p /var/log/smart_warehouse

# Thư mục sao lưu CSDL (tách biệt hoàn toàn với thư mục dữ liệu CSDL)
sudo mkdir -p /var/backups/warehouse

# Áp dụng quyền hạn nghiêm ngặt (chmod 700 / 750)
sudo chown -R wh_service:wh_service /opt/smart_warehouse_api
sudo chown -R wh_service:wh_service /var/log/smart_warehouse
sudo chown -R wh_backup:wh_backup /var/backups/warehouse

sudo chmod 750 /opt/smart_warehouse_api
sudo chmod 750 /var/log/smart_warehouse
sudo chmod 700 /var/backups/warehouse

# Bảo vệ thư mục dữ liệu gốc MySQL (chỉ user mysql đọc/ghi)
if [ -d /var/lib/mysql ]; then
    sudo chown -R mysql:mysql /var/lib/mysql
    sudo chmod 700 /var/lib/mysql
    echo "✓ Đã khóa chặt thư mục CSDL /var/lib/mysql (chỉ user mysql được truy cập)"
fi

echo "=== [3/5] CÀI ĐẶT CÁC THƯ VIỆN PYTHON PHỤ THUỘC ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-mysql.connector
pip3 install Flask flask-cors PyJWT

echo "=== [4/5] SAO CHÉP DỊCH VỤ SYSTEMD ==="
sudo cp smart_warehouse_api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart_warehouse_api.service

echo "=== [5/5] HOÀN TẤT CẤU HÌNH BẢO MẬT 3 TẦNG ==="
echo "Kiểm tra phân quyền thư mục:"
ls -ld /var/lib/mysql /var/backups/warehouse /opt/smart_warehouse_api /var/log/smart_warehouse
echo ""
echo "Để khởi động dịch vụ: sudo systemctl start smart_warehouse_api.service"
echo "Để kiểm tra trạng thái: sudo systemctl status smart_warehouse_api.service"
