import sqlite3
import hashlib

DATABASE_PATH = "data/quanlynhansu.db"  # Đường dẫn đến file database

def connect_db():
    """Kết nối đến cơ sở dữ liệu."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return None  # Trả về None nếu kết nối thất bại

def close_db(conn):
    """Đóng kết nối cơ sở dữ liệu."""
    if conn:
        conn.close()

def create_tables(conn):
    """Tạo các bảng trong cơ sở dữ liệu nếu chưa tồn tại."""
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PhongBan (
                PhongBanID INTEGER PRIMARY KEY AUTOINCREMENT,
                TenPhongBan VARCHAR(255) NOT NULL,
                MoTa TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ViTri (
                ViTriID INTEGER PRIMARY KEY AUTOINCREMENT,
                TenViTri VARCHAR(255) NOT NULL,
                MoTa TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS NhanVien (
                MaNhanVien INTEGER PRIMARY KEY AUTOINCREMENT,
                HoTen VARCHAR(255) NOT NULL,
                NgaySinh DATE,
                GioiTinh VARCHAR(10),
                DiaChi TEXT,
                SoDienThoai VARCHAR(20),
                Email VARCHAR(255),
                PhongBanID INTEGER,
                ViTriID INTEGER,
                NgayVaoCongTy DATE,
                MucLuong DECIMAL(10, 2),
                AnhDaiDien VARCHAR(255),
                SoCMND VARCHAR(20),
                FOREIGN KEY (PhongBanID) REFERENCES PhongBan(PhongBanID),
                FOREIGN KEY (ViTriID) REFERENCES ViTri(ViTriID)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaiKhoan (
                TaiKhoanID INTEGER PRIMARY KEY AUTOINCREMENT,
                MaNhanVien INTEGER UNIQUE,
                TenDangNhap VARCHAR(255) NOT NULL,
                MatKhau VARCHAR(255) NOT NULL,
                QuyenHan VARCHAR(50),
                FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
            )
        """)

        # Thêm bảng CongViec (Tasks)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CongViec (
                CongViecID INTEGER PRIMARY KEY AUTOINCREMENT,
                TieuDe VARCHAR(255) NOT NULL,
                MoTa TEXT,
                NgayBatDau DATE,
                NgayKetThuc DATE,
                TrangThai VARCHAR(50) DEFAULT 'Chưa hoàn thành',
                MucDoUuTien VARCHAR(50) DEFAULT 'Bình thường',
                MaNhanVien INTEGER,
                NguoiGiao INTEGER,
                FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien),
                FOREIGN KEY (NguoiGiao) REFERENCES NhanVien(MaNhanVien)
            )
        """)

        # Thêm bảng ThanhTich (Achievements)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ThanhTich (
                ThanhTichID INTEGER PRIMARY KEY AUTOINCREMENT,
                TieuDe VARCHAR(255) NOT NULL,
                MoTa TEXT,
                NgayDat DATE,
                LoaiThanhTich VARCHAR(100),
                MaNhanVien INTEGER,
                FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
            )
        """)

        # Thêm bảng ChamCong (Attendance)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ChamCong (
                ChamCongID INTEGER PRIMARY KEY AUTOINCREMENT,
                MaNhanVien INTEGER,
                NgayLamViec DATE,
                GioVao TIME,
                GioRa TIME,
                TrangThai VARCHAR(50) DEFAULT 'Đi làm',
                GhiChu TEXT,
                FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
            )
        """)

        conn.commit()  # Lưu thay đổi
        print("Đã tạo các bảng thành công (nếu chưa tồn tại).")

    except sqlite3.Error as e:
        print(f"Lỗi tạo bảng: {e}")

def them_nhan_vien(conn, hoTen, ngaySinh, gioiTinh, diaChi, soDienThoai, email, phongBanID, viTriID, ngayVaoCongTy, mucLuong, anhDaiDien, soCMND):
    """Thêm một nhân viên mới vào cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO NhanVien (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, Email, PhongBanID, ViTriID, NgayVaoCongTy, MucLuong, AnhDaiDien, SoCMND)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (hoTen, ngaySinh, gioiTinh, diaChi, soDienThoai, email, phongBanID, viTriID, ngayVaoCongTy, mucLuong, anhDaiDien, soCMND)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã thêm nhân viên thành công.")
        return cursor.lastrowid  # Trả về ID của nhân viên vừa thêm
    except sqlite3.Error as e:
        print(f"Lỗi thêm nhân viên: {e}")
        return None

def lay_danh_sach_nhan_vien(conn):
    """Lấy danh sách tất cả nhân viên từ cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM NhanVien")
        rows = cursor.fetchall()  # Lấy tất cả các dòng dữ liệu
        return rows
    except sqlite3.Error as e:
        print(f"Lỗi lấy danh sách nhân viên: {e}")
        return None

def lay_nhan_vien_theo_id(conn, maNhanVien):
    """Lấy thông tin nhân viên theo ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM NhanVien WHERE MaNhanVien = ?", (maNhanVien,))
        row = cursor.fetchone()  # Lấy một dòng dữ liệu duy nhất
        return row
    except sqlite3.Error as e:
        print(f"Lỗi lấy thông tin nhân viên theo ID: {e}")
        return None

def sua_nhan_vien(conn, maNhanVien, hoTen, ngaySinh, gioiTinh, diaChi, soDienThoai, email, phongBanID, viTriID, ngayVaoCongTy, mucLuong, anhDaiDien, soCMND):
    """Sửa thông tin của một nhân viên."""
    try:
        cursor = conn.cursor()
        sql = """
            UPDATE NhanVien
            SET HoTen = ?, NgaySinh = ?, GioiTinh = ?, DiaChi = ?, SoDienThoai = ?, Email = ?, PhongBanID = ?, ViTriID = ?, NgayVaoCongTy = ?, MucLuong = ?, AnhDaiDien = ?, SoCMND = ?
            WHERE MaNhanVien = ?
        """
        values = (hoTen, ngaySinh, gioiTinh, diaChi, soDienThoai, email, phongBanID, viTriID, ngayVaoCongTy, mucLuong, anhDaiDien, soCMND, maNhanVien)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã sửa thông tin nhân viên thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi sửa thông tin nhân viên: {e}")
        return False

def xoa_nhan_vien(conn, maNhanVien):
    """Xóa một nhân viên khỏi cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM NhanVien WHERE MaNhanVien = ?", (maNhanVien,))
        conn.commit()
        print("Đã xóa nhân viên thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi xóa nhân viên: {e}")
        return False

# --- HÀM LẤY THÔNG TIN TÀI KHOẢN THEO TÊN ĐĂNG NHẬP ---
def lay_tai_khoan_theo_ten_dang_nhap(conn, ten_dang_nhap):
    """Lấy thông tin tài khoản theo tên đăng nhập."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TaiKhoan WHERE TenDangNhap = ?", (ten_dang_nhap,))
        tai_khoan = cursor.fetchone()
        return tai_khoan
    except sqlite3.Error as e:
        print(f"Lỗi lấy thông tin tài khoản: {e}")
        return None

# --- HÀM SỬA THÔNG TIN TÀI KHOẢN ---
def sua_tai_khoan(conn, tai_khoan_id, ten_dang_nhap, mat_khau, quyen_han):
    """Sửa thông tin tài khoản."""
    try:
        cursor = conn.cursor()
        sql = """
            UPDATE TaiKhoan
            SET TenDangNhap = ?, MatKhau = ?, QuyenHan = ?
            WHERE TaiKhoanID = ?
        """
        values = (ten_dang_nhap, mat_khau, quyen_han, tai_khoan_id)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã sửa thông tin tài khoản thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi sửa thông tin tài khoản: {e}")
        return False

# --- HÀM XÓA TÀI KHOẢN ---
def xoa_tai_khoan(conn, tai_khoan_id):
    """Xóa một tài khoản khỏi cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TaiKhoan WHERE TaiKhoanID = ?", (tai_khoan_id,))
        conn.commit()
        print("Đã xóa tài khoản thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi xóa tài khoản: {e}")
        return False

def tao_tai_khoan(conn, ten_dang_nhap, mat_khau, ma_nhan_vien, quyen_han):
  """Tạo tài khoản mới trong cơ sở dữ liệu."""
  try:
    cursor = conn.cursor()
    sql = """
        INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, QuyenHan)
        VALUES (?, ?, ?, ?)
    """
    values = (ten_dang_nhap, mat_khau, ma_nhan_vien, quyen_han)
    cursor.execute(sql, values)
    conn.commit()
    print("Đã tạo tài khoản thành công.")
    return True
  except sqlite3.Error as e:
    print(f"Lỗi tạo tài khoản: {e}")
    return False

# --- QUẢN LÝ CÔNG VIỆC (TASKS) ---
def them_cong_viec(conn, tieu_de, mo_ta, ngay_bat_dau, ngay_ket_thuc, trang_thai, muc_do_uu_tien, ma_nhan_vien, nguoi_giao):
    """Thêm một công việc mới vào cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO CongViec (TieuDe, MoTa, NgayBatDau, NgayKetThuc, TrangThai, MucDoUuTien, MaNhanVien, NguoiGiao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (tieu_de, mo_ta, ngay_bat_dau, ngay_ket_thuc, trang_thai, muc_do_uu_tien, ma_nhan_vien, nguoi_giao)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã thêm công việc mới thành công.")
        return cursor.lastrowid  # Trả về ID của công việc vừa thêm
    except sqlite3.Error as e:
        print(f"Lỗi thêm công việc: {e}")
        return None

def lay_danh_sach_cong_viec(conn, ma_nhan_vien=None):
    """Lấy danh sách tất cả công việc hoặc theo nhân viên."""
    try:
        cursor = conn.cursor()
        if ma_nhan_vien is not None:
            # Lấy công việc của một nhân viên cụ thể
            cursor.execute("""
                SELECT cv.*, nv.HoTen as NguoiNhan, ng.HoTen as NguoiGiao
                FROM CongViec cv
                LEFT JOIN NhanVien nv ON cv.MaNhanVien = nv.MaNhanVien
                LEFT JOIN NhanVien ng ON cv.NguoiGiao = ng.MaNhanVien
                WHERE cv.MaNhanVien = ?
            """, (ma_nhan_vien,))
        else:
            # Lấy tất cả công việc
            cursor.execute("""
                SELECT cv.*, nv.HoTen as NguoiNhan, ng.HoTen as NguoiGiao
                FROM CongViec cv
                LEFT JOIN NhanVien nv ON cv.MaNhanVien = nv.MaNhanVien
                LEFT JOIN NhanVien ng ON cv.NguoiGiao = ng.MaNhanVien
            """)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Lỗi lấy danh sách công việc: {e}")
        return None

def cap_nhat_trang_thai_cong_viec(conn, cong_viec_id, trang_thai):
    """Cập nhật trạng thái của một công việc."""
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE CongViec SET TrangThai = ? WHERE CongViecID = ?", (trang_thai, cong_viec_id))
        conn.commit()
        print("Đã cập nhật trạng thái công việc thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi cập nhật trạng thái công việc: {e}")
        return False

def xoa_cong_viec(conn, cong_viec_id):
    """Xóa một công việc từ cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CongViec WHERE CongViecID = ?", (cong_viec_id,))
        conn.commit()
        print("Đã xóa công việc thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi xóa công việc: {e}")
        return False

# --- QUẢN LÝ THÀNH TÍCH (ACHIEVEMENTS) ---
def them_thanh_tich(conn, tieu_de, mo_ta, ngay_dat, loai_thanh_tich, ma_nhan_vien):
    """Thêm một thành tích mới vào cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO ThanhTich (TieuDe, MoTa, NgayDat, LoaiThanhTich, MaNhanVien)
            VALUES (?, ?, ?, ?, ?)
        """
        values = (tieu_de, mo_ta, ngay_dat, loai_thanh_tich, ma_nhan_vien)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã thêm thành tích mới thành công.")
        return cursor.lastrowid  # Trả về ID của thành tích vừa thêm
    except sqlite3.Error as e:
        print(f"Lỗi thêm thành tích: {e}")
        return None

def lay_danh_sach_thanh_tich(conn, ma_nhan_vien=None):
    """Lấy danh sách tất cả thành tích hoặc theo nhân viên."""
    try:
        cursor = conn.cursor()
        if ma_nhan_vien is not None:
            # Lấy thành tích của một nhân viên cụ thể
            cursor.execute("""
                SELECT tt.*, nv.HoTen
                FROM ThanhTich tt
                LEFT JOIN NhanVien nv ON tt.MaNhanVien = nv.MaNhanVien
                WHERE tt.MaNhanVien = ?
            """, (ma_nhan_vien,))
        else:
            # Lấy tất cả thành tích
            cursor.execute("""
                SELECT tt.*, nv.HoTen
                FROM ThanhTich tt
                LEFT JOIN NhanVien nv ON tt.MaNhanVien = nv.MaNhanVien
            """)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Lỗi lấy danh sách thành tích: {e}")
        return None

def xoa_thanh_tich(conn, thanh_tich_id):
    """Xóa một thành tích từ cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ThanhTich WHERE ThanhTichID = ?", (thanh_tich_id,))
        conn.commit()
        print("Đã xóa thành tích thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi xóa thành tích: {e}")
        return False

# --- QUẢN LÝ CHẤM CÔNG (ATTENDANCE) ---
def them_cham_cong(conn, ma_nhan_vien, ngay_lam_viec, gio_vao, gio_ra, trang_thai, ghi_chu):
    """Thêm một bản ghi chấm công mới vào cơ sở dữ liệu."""
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO ChamCong (MaNhanVien, NgayLamViec, GioVao, GioRa, TrangThai, GhiChu)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (ma_nhan_vien, ngay_lam_viec, gio_vao, gio_ra, trang_thai, ghi_chu)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã thêm bản ghi chấm công mới thành công.")
        return cursor.lastrowid  # Trả về ID của bản ghi vừa thêm
    except sqlite3.Error as e:
        print(f"Lỗi thêm chấm công: {e}")
        return None

def lay_danh_sach_cham_cong(conn, ma_nhan_vien=None, tu_ngay=None, den_ngay=None):
    """Lấy danh sách chấm công theo nhân viên và khoảng thời gian."""
    try:
        cursor = conn.cursor()
        query = """
            SELECT cc.*, nv.HoTen
            FROM ChamCong cc
            LEFT JOIN NhanVien nv ON cc.MaNhanVien = nv.MaNhanVien
            WHERE 1=1
        """
        params = []
        
        if ma_nhan_vien is not None:
            query += " AND cc.MaNhanVien = ?"
            params.append(ma_nhan_vien)
        
        if tu_ngay is not None:
            query += " AND cc.NgayLamViec >= ?"
            params.append(tu_ngay)
        
        if den_ngay is not None:
            query += " AND cc.NgayLamViec <= ?"
            params.append(den_ngay)
        
        query += " ORDER BY cc.NgayLamViec DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Lỗi lấy danh sách chấm công: {e}")
        return None

def cap_nhat_cham_cong(conn, cham_cong_id, gio_vao, gio_ra, trang_thai, ghi_chu):
    """Cập nhật thông tin chấm công."""
    try:
        cursor = conn.cursor()
        sql = """
            UPDATE ChamCong
            SET GioVao = ?, GioRa = ?, TrangThai = ?, GhiChu = ?
            WHERE ChamCongID = ?
        """
        values = (gio_vao, gio_ra, trang_thai, ghi_chu, cham_cong_id)
        cursor.execute(sql, values)
        conn.commit()
        print("Đã cập nhật thông tin chấm công thành công.")
        return True
    except sqlite3.Error as e:
        print(f"Lỗi cập nhật chấm công: {e}")
        return False

def tinh_so_ngay_lam_viec(conn, ma_nhan_vien, thang, nam):
    """Tính số ngày làm việc của nhân viên trong tháng."""
    try:
        cursor = conn.cursor()
        ngay_dau_thang = f"{nam}-{thang:02d}-01"
        ngay_cuoi_thang = f"{nam}-{thang:02d}-31"  # Sẽ tự điều chỉnh nếu tháng không có 31 ngày
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ChamCong 
            WHERE MaNhanVien = ? 
            AND NgayLamViec BETWEEN ? AND ?
            AND TrangThai = 'Đi làm'
        """, (ma_nhan_vien, ngay_dau_thang, ngay_cuoi_thang))
        
        so_ngay = cursor.fetchone()[0]
        return so_ngay
    except sqlite3.Error as e:
        print(f"Lỗi tính số ngày làm việc: {e}")
        return 0

# --- CÁC HÀM KHÁC CHO PhongBan, ViTri, ... ---