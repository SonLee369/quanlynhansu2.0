import streamlit as st
from utils import database
import pandas as pd
from datetime import datetime, timedelta

def training_performance(user_id, is_admin=False):
    """Module Đào tạo & Đánh giá Hiệu suất."""
    
    # Tạo tabs cho các chức năng
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Kế hoạch Đào tạo",
        "Khóa học",
        "Đăng ký & Theo dõi",
        "KPI",
        "Đánh giá Hiệu suất",
        "Phản hồi",
        "Lộ trình Phát triển"
    ])
    
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    # Tab 1: Kế hoạch Đào tạo
    with tab1:
        st.header("Quản lý Kế hoạch Đào tạo")
        
        if is_admin:
            with st.expander("Thêm kế hoạch mới"):
                ten_ke_hoach = st.text_input("Tên kế hoạch", key="ten_ke_hoach")
                mo_ta = st.text_area("Mô tả", key="mo_ta_ke_hoach")
                ngay_bat_dau = st.date_input("Ngày bắt đầu", key="ngay_bat_dau_ke_hoach")
                ngay_ket_thuc = st.date_input("Ngày kết thúc", key="ngay_ket_thuc_ke_hoach")
                
                if st.button("Thêm kế hoạch", key="btn_them_ke_hoach"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO KeHoachDaoTao (TenKeHoach, MoTa, NgayBatDau, NgayKetThuc, TrangThai, NguoiTaoID)
                        VALUES (?, ?, ?, ?, 'Chờ duyệt', ?)
                    """, (ten_ke_hoach, mo_ta, ngay_bat_dau, ngay_ket_thuc, user_id))
                    conn.commit()
                    st.success("Đã thêm kế hoạch mới!")
        
        # Hiển thị danh sách kế hoạch
        cursor = conn.cursor()
        cursor.execute("""
            SELECT k.*, n.HoTen as NguoiTao
            FROM KeHoachDaoTao k
            LEFT JOIN NhanVien n ON k.NguoiTaoID = n.MaNhanVien
            ORDER BY k.NgayBatDau DESC
        """)
        ke_hoach_list = cursor.fetchall()
        
        if ke_hoach_list:
            df = pd.DataFrame(ke_hoach_list, columns=[
                'ID', 'Tên kế hoạch', 'Mô tả', 'Ngày bắt đầu', 'Ngày kết thúc',
                'Trạng thái', 'Người tạo ID', 'Người tạo'
            ])
            st.dataframe(df, key="df_ke_hoach")
        else:
            st.info("Chưa có kế hoạch đào tạo nào.")
    
    # Tab 2: Khóa học
    with tab2:
        st.header("Quản lý Khóa học")
        
        if is_admin:
            with st.expander("Thêm khóa học mới"):
                ten_khoa_hoc = st.text_input("Tên khóa học", key="ten_khoa_hoc")
                mo_ta = st.text_area("Mô tả", key="mo_ta_khoa_hoc")
                loai_hoc = st.selectbox("Loại học", ["Online", "Offline"], key="loai_hoc")
                thoi_luong = st.number_input("Thời lượng (giờ)", min_value=1, key="thoi_luong")
                gia_tien = st.number_input("Giá tiền", min_value=0, key="gia_tien")
                
                # Lấy danh sách kế hoạch
                cursor = conn.cursor()
                cursor.execute("SELECT KeHoachID, TenKeHoach FROM KeHoachDaoTao WHERE TrangThai != 'Hủy'")
                ke_hoach_options = cursor.fetchall()
                
                ke_hoach_id = st.selectbox(
                    "Kế hoạch đào tạo",
                    options=[k[0] for k in ke_hoach_options],
                    format_func=lambda x: next((k[1] for k in ke_hoach_options if k[0] == x), ""),
                    key="ke_hoach_id"
                )
                
                if st.button("Thêm khóa học", key="btn_them_khoa_hoc"):
                    cursor.execute("""
                        INSERT INTO KhoaHoc (TenKhoaHoc, MoTa, LoaiHoc, ThoiLuong, GiaTien, KeHoachID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (ten_khoa_hoc, mo_ta, loai_hoc, thoi_luong, gia_tien, ke_hoach_id))
                    conn.commit()
                    st.success("Đã thêm khóa học mới!")
        
        # Hiển thị danh sách khóa học
        cursor.execute("""
            SELECT k.*, kh.TenKeHoach
            FROM KhoaHoc k
            LEFT JOIN KeHoachDaoTao kh ON k.KeHoachID = kh.KeHoachID
            ORDER BY k.KhoaHocID DESC
        """)
        khoa_hoc_list = cursor.fetchall()
        
        if khoa_hoc_list:
            df = pd.DataFrame(khoa_hoc_list, columns=[
                'ID', 'Tên khóa học', 'Mô tả', 'Loại học', 'Thời lượng',
                'Giá tiền', 'Kế hoạch ID', 'Tên kế hoạch'
            ])
            st.dataframe(df, key="df_khoa_hoc")
        else:
            st.info("Chưa có khóa học nào.")
    
    # Tab 3: Đăng ký & Theo dõi
    with tab3:
        st.header("Đăng ký & Theo dõi Đào tạo")
        
        # Form đăng ký khóa học
        with st.expander("Đăng ký khóa học"):
            # Lấy danh sách khóa học
            cursor = conn.cursor()
            cursor.execute("""
                SELECT k.KhoaHocID, k.TenKhoaHoc, k.LoaiHoc, k.ThoiLuong, k.GiaTien
                FROM KhoaHoc k
                JOIN KeHoachDaoTao kh ON k.KeHoachID = kh.KeHoachID
                WHERE kh.TrangThai != 'Hủy'
            """)
            khoa_hoc_options = cursor.fetchall()
            
            if khoa_hoc_options:
                khoa_hoc_id = st.selectbox(
                    "Chọn khóa học",
                    options=[k[0] for k in khoa_hoc_options],
                    format_func=lambda x: next((k[1] for k in khoa_hoc_options if k[0] == x), ""),
                    key="dang_ky_khoa_hoc"
                )
                
                if st.button("Đăng ký", key="btn_dang_ky"):
                    cursor.execute("""
                        INSERT INTO DangKyKhoaHoc (KhoaHocID, NhanVienID, NgayDangKy, TrangThai)
                        VALUES (?, ?, ?, 'Chờ duyệt')
                    """, (khoa_hoc_id, user_id, datetime.now().date()))
                    conn.commit()
                    st.success("Đã đăng ký khóa học!")
            else:
                st.info("Không có khóa học nào để đăng ký.")
        
        # Hiển thị danh sách đăng ký
        cursor.execute("""
            SELECT dk.*, k.TenKhoaHoc, k.LoaiHoc, n.HoTen
            FROM DangKyKhoaHoc dk
            JOIN KhoaHoc k ON dk.KhoaHocID = k.KhoaHocID
            JOIN NhanVien n ON dk.NhanVienID = n.MaNhanVien
            WHERE dk.NhanVienID = ?
            ORDER BY dk.NgayDangKy DESC
        """, (user_id,))
        dang_ky_list = cursor.fetchall()
        
        if dang_ky_list:
            df = pd.DataFrame(dang_ky_list, columns=[
                'ID', 'Khóa học ID', 'Nhân viên ID', 'Ngày đăng ký',
                'Trạng thái', 'Điểm số', 'Ghi chú', 'Tên khóa học',
                'Loại học', 'Họ tên'
            ])
            st.dataframe(df, key="df_dang_ky")
        else:
            st.info("Bạn chưa đăng ký khóa học nào.")
    
    # Tab 4: KPI
    with tab4:
        st.header("Quản lý Chỉ số KPI")
        
        if is_admin:
            with st.expander("Thêm chỉ số KPI mới"):
                ten_kpi = st.text_input("Tên KPI", key="ten_kpi")
                mo_ta = st.text_area("Mô tả", key="mo_ta_kpi")
                don_vi = st.text_input("Đơn vị", key="don_vi_kpi")
                muc_tieu = st.number_input("Mục tiêu", min_value=0.0, key="muc_tieu_kpi")
                trong_so = st.number_input("Trọng số", min_value=0.0, max_value=1.0, step=0.1, key="trong_so_kpi")
                
                # Lấy danh sách phòng ban
                cursor = conn.cursor()
                cursor.execute("SELECT PhongBanID, TenPhongBan FROM PhongBan")
                phong_ban_options = cursor.fetchall()
                
                phong_ban_id = st.selectbox(
                    "Phòng ban",
                    options=[p[0] for p in phong_ban_options],
                    format_func=lambda x: next((p[1] for p in phong_ban_options if p[0] == x), ""),
                    key="phong_ban_kpi"
                )
                
                if st.button("Thêm KPI", key="btn_them_kpi"):
                    cursor.execute("""
                        INSERT INTO ChiSoKPI (TenKPI, MoTa, DonVi, MucTieu, TrongSo, PhongBanID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (ten_kpi, mo_ta, don_vi, muc_tieu, trong_so, phong_ban_id))
                    conn.commit()
                    st.success("Đã thêm KPI mới!")
        
        # Hiển thị danh sách KPI
        cursor.execute("""
            SELECT k.*, p.TenPhongBan
            FROM ChiSoKPI k
            JOIN PhongBan p ON k.PhongBanID = p.PhongBanID
            ORDER BY k.KPIID DESC
        """)
        kpi_list = cursor.fetchall()
        
        if kpi_list:
            df = pd.DataFrame(kpi_list, columns=[
                'ID', 'Tên KPI', 'Mô tả', 'Đơn vị', 'Mục tiêu',
                'Trọng số', 'Phòng ban ID', 'Tên phòng ban'
            ])
            st.dataframe(df, key="df_kpi")
        else:
            st.info("Chưa có chỉ số KPI nào.")
    
    # Tab 5: Đánh giá Hiệu suất
    with tab5:
        st.header("Đánh giá Hiệu suất")
        
        if is_admin:
            with st.expander("Tạo đánh giá mới"):
                # Chọn nhân viên
                cursor = conn.cursor()
                cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
                nhan_vien_options = cursor.fetchall()
                
                nhan_vien_id = st.selectbox(
                    "Chọn nhân viên",
                    options=[n[0] for n in nhan_vien_options],
                    format_func=lambda x: next((n[1] for n in nhan_vien_options if n[0] == x), ""),
                    key="nhan_vien_danh_gia"
                )
                
                ky_danh_gia = st.text_input("Kỳ đánh giá (VD: Q1-2024)", key="ky_danh_gia")
                ngay_danh_gia = st.date_input("Ngày đánh giá", key="ngay_danh_gia")
                
                # Lấy danh sách KPI của phòng ban
                cursor.execute("""
                    SELECT k.KPIID, k.TenKPI, k.MucTieu, k.TrongSo
                    FROM ChiSoKPI k
                    JOIN NhanVien n ON k.PhongBanID = n.PhongBanID
                    WHERE n.MaNhanVien = ?
                """, (nhan_vien_id,))
                kpi_list = cursor.fetchall()
                
                if kpi_list:
                    st.subheader("Đánh giá các chỉ số KPI")
                    diem_kpi = {}
                    for idx, kpi in enumerate(kpi_list):
                        ket_qua = st.number_input(
                            f"Kết quả {kpi[1]}",
                            min_value=0.0,
                            value=float(kpi[2]),
                            key=f"ket_qua_kpi_{idx}"
                        )
                        diem_kpi[kpi[0]] = ket_qua
                    
                    if st.button("Lưu đánh giá", key="btn_luu_danh_gia"):
                        # Tính tổng điểm
                        tong_diem = sum(diem_kpi.values())
                        
                        # Xác định xếp loại
                        if tong_diem >= 90:
                            xep_loai = "Xuất sắc"
                        elif tong_diem >= 80:
                            xep_loai = "Tốt"
                        elif tong_diem >= 70:
                            xep_loai = "Đạt"
                        elif tong_diem >= 60:
                            xep_loai = "Cần cải thiện"
                        else:
                            xep_loai = "Không đạt"
                        
                        # Lưu đánh giá
                        cursor.execute("""
                            INSERT INTO DanhGiaHieuSuat 
                            (NhanVienID, KyDanhGia, NgayDanhGia, NguoiDanhGiaID, TongDiem, XepLoai)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (nhan_vien_id, ky_danh_gia, ngay_danh_gia, user_id, tong_diem, xep_loai))
                        
                        danh_gia_id = cursor.lastrowid
                        
                        # Lưu chi tiết KPI
                        for kpi_id, ket_qua in diem_kpi.items():
                            cursor.execute("""
                                INSERT INTO ChiTietDanhGiaKPI 
                                (DanhGiaID, KPIID, KetQua)
                                VALUES (?, ?, ?)
                            """, (danh_gia_id, kpi_id, ket_qua))
                        
                        conn.commit()
                        st.success("Đã lưu đánh giá hiệu suất!")
                else:
                    st.warning("Không tìm thấy chỉ số KPI cho nhân viên này.")
        
        # Hiển thị lịch sử đánh giá
        cursor.execute("""
            SELECT dg.*, n.HoTen as NhanVien, ng.HoTen as NguoiDanhGia
            FROM DanhGiaHieuSuat dg
            JOIN NhanVien n ON dg.NhanVienID = n.MaNhanVien
            JOIN NhanVien ng ON dg.NguoiDanhGiaID = ng.MaNhanVien
            WHERE dg.NhanVienID = ?
            ORDER BY dg.NgayDanhGia DESC
        """, (user_id,))
        danh_gia_list = cursor.fetchall()
        
        if danh_gia_list:
            df = pd.DataFrame(danh_gia_list, columns=[
                'ID', 'Nhân viên ID', 'Kỳ đánh giá', 'Ngày đánh giá',
                'Người đánh giá ID', 'Tổng điểm', 'Xếp loại', 'Nhận xét',
                'Nhân viên', 'Người đánh giá'
            ])
            st.dataframe(df, key="df_danh_gia")
        else:
            st.info("Chưa có đánh giá hiệu suất nào.")
    
    # Tab 6: Phản hồi
    with tab6:
        st.header("Quản lý Phản hồi")
        
        # Form gửi phản hồi
        with st.expander("Gửi phản hồi mới"):
            loai_phan_hoi = st.selectbox(
                "Loại phản hồi",
                ["Đào tạo", "Hiệu suất", "Môi trường làm việc", "Khác"],
                key="loai_phan_hoi"
            )
            noi_dung = st.text_area("Nội dung phản hồi", key="noi_dung_phan_hoi")
            
            if st.button("Gửi phản hồi", key="btn_gui_phan_hoi"):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO PhanHoi (NhanVienID, LoaiPhanHoi, NoiDung, NgayGui, TrangThai)
                    VALUES (?, ?, ?, ?, 'Chờ xử lý')
                """, (user_id, loai_phan_hoi, noi_dung, datetime.now().date()))
                conn.commit()
                st.success("Đã gửi phản hồi!")
        
        # Hiển thị danh sách phản hồi
        cursor.execute("""
            SELECT p.*, n.HoTen as NhanVien, ng.HoTen as NguoiXuLy
            FROM PhanHoi p
            JOIN NhanVien n ON p.NhanVienID = n.MaNhanVien
            LEFT JOIN NhanVien ng ON p.NguoiXuLyID = ng.MaNhanVien
            WHERE p.NhanVienID = ?
            ORDER BY p.NgayGui DESC
        """, (user_id,))
        phan_hoi_list = cursor.fetchall()
        
        if phan_hoi_list:
            df = pd.DataFrame(phan_hoi_list, columns=[
                'ID', 'Nhân viên ID', 'Loại phản hồi', 'Nội dung',
                'Ngày gửi', 'Trạng thái', 'Người xử lý ID', 'Nhân viên',
                'Người xử lý'
            ])
            st.dataframe(df, key="df_phan_hoi")
        else:
            st.info("Chưa có phản hồi nào.")
    
    # Tab 7: Lộ trình Phát triển
    with tab7:
        st.header("Lộ trình Phát triển")
        
        # Form tạo lộ trình mới
        with st.expander("Tạo lộ trình mới"):
            vi_tri_muc_tieu = st.text_input("Vị trí mục tiêu", key="vi_tri_muc_tieu")
            thoi_gian_du_kien = st.date_input("Thời gian dự kiến", key="thoi_gian_du_kien")
            mo_ta = st.text_area("Mô tả lộ trình", key="mo_ta_lo_trinh")
            
            if st.button("Tạo lộ trình", key="btn_tao_lo_trinh"):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO LoTrinhPhatTrien 
                    (NhanVienID, ViTriMucTieu, ThoiGianDuKien, TrangThai, MoTa)
                    VALUES (?, ?, ?, 'Đang thực hiện', ?)
                """, (user_id, vi_tri_muc_tieu, thoi_gian_du_kien, mo_ta))
                conn.commit()
                st.success("Đã tạo lộ trình mới!")
        
        # Hiển thị danh sách lộ trình
        cursor.execute("""
            SELECT l.*, n.HoTen
            FROM LoTrinhPhatTrien l
            JOIN NhanVien n ON l.NhanVienID = n.MaNhanVien
            WHERE l.NhanVienID = ?
            ORDER BY l.ThoiGianDuKien DESC
        """, (user_id,))
        lo_trinh_list = cursor.fetchall()
        
        if lo_trinh_list:
            df = pd.DataFrame(lo_trinh_list, columns=[
                'ID', 'Nhân viên ID', 'Vị trí mục tiêu', 'Thời gian dự kiến',
                'Trạng thái', 'Mô tả', 'Họ tên'
            ])
            st.dataframe(df, key="df_lo_trinh")
        else:
            st.info("Chưa có lộ trình phát triển nào.")
    
    database.close_db(conn) 