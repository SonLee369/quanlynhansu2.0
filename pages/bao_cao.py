import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from utils import database
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import calendar

# Thiết lập trang
st.set_page_config(page_title="Báo cáo & Thống kê", page_icon="📊", layout="wide")

# Kiểm tra quyền truy cập
if "dang_nhap" not in st.session_state or not st.session_state.dang_nhap:
    st.warning("Vui lòng đăng nhập để sử dụng chức năng này.")
    st.stop()

if st.session_state.quyen_han != "admin":
    st.error("Bạn không có quyền truy cập chức năng này.")
    st.stop()

st.title("Báo cáo & Thống kê")

# Tạo tabs cho các loại báo cáo khác nhau
tab1, tab2, tab3 = st.tabs(["Nhân sự", "Công việc", "Chấm công"])

# Tab 1: Báo cáo Nhân sự
with tab1:
    st.subheader("Phân tích nhân sự")
    
    # Kết nối CSDL
    conn = database.connect_db()
    if conn:
        try:
            # Lấy thông tin tổng quan
            cursor = conn.cursor()
            
            # Tổng số nhân viên
            cursor.execute("SELECT COUNT(*) FROM NhanVien")
            tong_nhan_vien = cursor.fetchone()[0]
            
            # Phân bố theo phòng ban
            cursor.execute("""
                SELECT PhongBan.TenPhongBan, COUNT(NhanVien.MaNhanVien) as SoLuong
                FROM NhanVien 
                JOIN PhongBan ON NhanVien.PhongBanID = PhongBan.PhongBanID
                GROUP BY PhongBan.TenPhongBan
            """)
            phan_bo_phong_ban = cursor.fetchall()
            
            # Phân bố theo vị trí
            cursor.execute("""
                SELECT ViTri.TenViTri, COUNT(NhanVien.MaNhanVien) as SoLuong
                FROM NhanVien 
                JOIN ViTri ON NhanVien.ViTriID = ViTri.ViTriID
                GROUP BY ViTri.TenViTri
            """)
            phan_bo_vi_tri = cursor.fetchall()
            
            # Phân bố giới tính
            cursor.execute("""
                SELECT GioiTinh, COUNT(*) as SoLuong
                FROM NhanVien
                GROUP BY GioiTinh
            """)
            phan_bo_gioi_tinh = cursor.fetchall()
            
            # Thâm niên làm việc
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN julianday('now') - julianday(NgayVaoCongTy) < 365 THEN 'Dưới 1 năm'
                        WHEN julianday('now') - julianday(NgayVaoCongTy) < 365*3 THEN '1-3 năm'
                        WHEN julianday('now') - julianday(NgayVaoCongTy) < 365*5 THEN '3-5 năm'
                        ELSE 'Trên 5 năm'
                    END as ThamNien,
                    COUNT(*) as SoLuong
                FROM NhanVien
                WHERE NgayVaoCongTy IS NOT NULL
                GROUP BY ThamNien
            """)
            phan_bo_tham_nien = cursor.fetchall()
            
            # Hiển thị tổng quan
            st.markdown("### Tổng quan nhân sự")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tổng số nhân viên", tong_nhan_vien)
            
            with col2:
                phan_bo_nam_nu = {row[0]: row[1] for row in phan_bo_gioi_tinh}
                so_nam = phan_bo_nam_nu.get("Nam", 0)
                so_nu = phan_bo_nam_nu.get("Nữ", 0)
                ty_le_nam = (so_nam / tong_nhan_vien * 100) if tong_nhan_vien > 0 else 0
                st.metric("Tỷ lệ Nam/Nữ", f"{ty_le_nam:.1f}% / {100-ty_le_nam:.1f}%")
            
            with col3:
                # Số nhân viên mới (vào công ty trong 3 tháng gần đây)
                ba_thang_truoc = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
                cursor.execute(
                    "SELECT COUNT(*) FROM NhanVien WHERE NgayVaoCongTy >= ?", 
                    (ba_thang_truoc,)
                )
                nhan_vien_moi = cursor.fetchone()[0]
                st.metric("Nhân viên mới (3 tháng)", nhan_vien_moi)
            
            with col4:
                # Tìm phòng ban có nhiều nhân viên nhất
                if phan_bo_phong_ban:
                    phong_ban_max = max(phan_bo_phong_ban, key=lambda x: x[1])
                    st.metric("Phòng ban đông nhất", f"{phong_ban_max[0]} ({phong_ban_max[1]})")
                else:
                    st.metric("Phòng ban đông nhất", "Không có dữ liệu")
            
            # Hiển thị biểu đồ
            st.markdown("### Phân bố nhân viên")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Biểu đồ phân bố theo phòng ban
                if phan_bo_phong_ban:
                    df_phong_ban = pd.DataFrame(phan_bo_phong_ban, columns=["Phòng ban", "Số lượng"])
                    fig = px.pie(
                        df_phong_ban, 
                        values="Số lượng", 
                        names="Phòng ban", 
                        title="Phân bố nhân viên theo phòng ban",
                        hole=0.4
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Không có dữ liệu phân bố theo phòng ban.")
            
            with col2:
                # Biểu đồ phân bố theo vị trí
                if phan_bo_vi_tri:
                    df_vi_tri = pd.DataFrame(phan_bo_vi_tri, columns=["Vị trí", "Số lượng"])
                    fig = px.bar(
                        df_vi_tri, 
                        x="Vị trí", 
                        y="Số lượng", 
                        title="Phân bố nhân viên theo vị trí",
                        color="Số lượng"
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Không có dữ liệu phân bố theo vị trí.")
            
            # Biểu đồ thâm niên và giới tính
            col1, col2 = st.columns(2)
            
            with col1:
                # Biểu đồ phân bố theo thâm niên
                if phan_bo_tham_nien:
                    df_tham_nien = pd.DataFrame(phan_bo_tham_nien, columns=["Thâm niên", "Số lượng"])
                    # Sắp xếp thứ tự thâm niên
                    order = ["Dưới 1 năm", "1-3 năm", "3-5 năm", "Trên 5 năm"]
                    df_tham_nien["Thâm niên"] = pd.Categorical(df_tham_nien["Thâm niên"], categories=order, ordered=True)
                    df_tham_nien = df_tham_nien.sort_values("Thâm niên")
                    
                    fig = px.pie(
                        df_tham_nien, 
                        values="Số lượng", 
                        names="Thâm niên", 
                        title="Phân bố nhân viên theo thâm niên"
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Không có dữ liệu thâm niên.")
            
            with col2:
                # Biểu đồ phân bố theo giới tính
                if phan_bo_gioi_tinh:
                    df_gioi_tinh = pd.DataFrame(phan_bo_gioi_tinh, columns=["Giới tính", "Số lượng"])
                    fig = px.pie(
                        df_gioi_tinh, 
                        values="Số lượng", 
                        names="Giới tính", 
                        title="Phân bố nhân viên theo giới tính",
                        color_discrete_map={"Nam": "#1f77b4", "Nữ": "#ff7f0e", "Khác": "#2ca02c"}
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Không có dữ liệu giới tính.")
        
        except sqlite3.Error as e:
            st.error(f"Lỗi truy vấn CSDL: {e}")
        
        finally:
            database.close_db(conn)
    else:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 2: Báo cáo Công việc
with tab2:
    st.subheader("Phân tích công việc")
    
    # Kết nối CSDL
    conn = database.connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Tổng số công việc
            cursor.execute("SELECT COUNT(*) FROM CongViec")
            tong_cong_viec = cursor.fetchone()[0]
            
            # Công việc theo trạng thái
            cursor.execute("""
                SELECT TrangThai, COUNT(*) as SoLuong
                FROM CongViec
                GROUP BY TrangThai
            """)
            phan_bo_trang_thai = cursor.fetchall()
            
            # Công việc theo mức độ ưu tiên
            cursor.execute("""
                SELECT MucDoUuTien, COUNT(*) as SoLuong
                FROM CongViec
                GROUP BY MucDoUuTien
            """)
            phan_bo_uu_tien = cursor.fetchall()
            
            # Công việc quá hạn
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COUNT(*) FROM CongViec
                WHERE NgayKetThuc < ? AND TrangThai != 'Đã hoàn thành'
            """, (today,))
            cong_viec_qua_han = cursor.fetchone()[0]
            
            # Hiển thị tổng quan
            st.markdown("### Tổng quan công việc")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tổng số công việc", tong_cong_viec)
            
            with col2:
                # Tính tỷ lệ hoàn thành
                if phan_bo_trang_thai:
                    trang_thai_dict = {row[0]: row[1] for row in phan_bo_trang_thai}
                    da_hoan_thanh = trang_thai_dict.get("Đã hoàn thành", 0)
                    ty_le_hoan_thanh = (da_hoan_thanh / tong_cong_viec * 100) if tong_cong_viec > 0 else 0
                    st.metric("Tỷ lệ hoàn thành", f"{ty_le_hoan_thanh:.1f}%")
                else:
                    st.metric("Tỷ lệ hoàn thành", "0%")
            
            with col3:
                st.metric("Công việc quá hạn", cong_viec_qua_han)
            
            with col4:
                # Công việc ưu tiên cao chưa hoàn thành
                cursor.execute("""
                    SELECT COUNT(*) FROM CongViec
                    WHERE MucDoUuTien = 'Cao' AND TrangThai != 'Đã hoàn thành'
                """)
                cong_viec_uu_tien_cao = cursor.fetchone()[0]
                st.metric("Công việc ưu tiên cao", cong_viec_uu_tien_cao)
            
            # Hiển thị biểu đồ phân tích
            st.markdown("### Phân tích chi tiết")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Biểu đồ theo trạng thái
                if phan_bo_trang_thai:
                    df_trang_thai = pd.DataFrame(phan_bo_trang_thai, columns=["Trạng thái", "Số lượng"])
                    fig = px.pie(
                        df_trang_thai, 
                        values="Số lượng", 
                        names="Trạng thái", 
                        title="Phân bố công việc theo trạng thái",
                        color_discrete_map={
                            "Đã hoàn thành": "#4caf50",
                            "Đang thực hiện": "#2196f3",
                            "Chưa hoàn thành": "#ff9800"
                        }
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Chưa có dữ liệu công việc.")
            
            with col2:
                # Biểu đồ theo mức độ ưu tiên
                if phan_bo_uu_tien:
                    df_uu_tien = pd.DataFrame(phan_bo_uu_tien, columns=["Mức độ ưu tiên", "Số lượng"])
                    fig = px.bar(
                        df_uu_tien, 
                        x="Mức độ ưu tiên", 
                        y="Số lượng", 
                        title="Phân bố công việc theo mức độ ưu tiên",
                        color="Mức độ ưu tiên",
                        color_discrete_map={
                            "Cao": "#f44336",
                            "Bình thường": "#4caf50",
                            "Thấp": "#2196f3"
                        }
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("Chưa có dữ liệu công việc.")
            
            # Biểu đồ tiến độ công việc theo phòng ban
            st.markdown("### Tiến độ công việc theo phòng ban")
            
            # Lấy dữ liệu
            cursor.execute("""
                SELECT pb.TenPhongBan,
                    SUM(CASE WHEN cv.TrangThai = 'Đã hoàn thành' THEN 1 ELSE 0 END) as HoanThanh,
                    SUM(CASE WHEN cv.TrangThai = 'Đang thực hiện' THEN 1 ELSE 0 END) as DangThucHien,
                    SUM(CASE WHEN cv.TrangThai = 'Chưa hoàn thành' THEN 1 ELSE 0 END) as ChuaHoanThanh
                FROM CongViec cv
                JOIN NhanVien nv ON cv.MaNhanVien = nv.MaNhanVien
                JOIN PhongBan pb ON nv.PhongBanID = pb.PhongBanID
                GROUP BY pb.TenPhongBan
            """)
            tien_do_phong_ban = cursor.fetchall()
            
            if tien_do_phong_ban:
                df_tien_do = pd.DataFrame(tien_do_phong_ban, columns=[
                    "Phòng ban", "Hoàn thành", "Đang thực hiện", "Chưa hoàn thành"
                ])
                
                # Tạo dữ liệu cho biểu đồ
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Hoàn thành',
                    x=df_tien_do['Phòng ban'],
                    y=df_tien_do['Hoàn thành'],
                    marker_color='#4caf50'
                ))
                
                fig.add_trace(go.Bar(
                    name='Đang thực hiện',
                    x=df_tien_do['Phòng ban'],
                    y=df_tien_do['Đang thực hiện'],
                    marker_color='#2196f3'
                ))
                
                fig.add_trace(go.Bar(
                    name='Chưa hoàn thành',
                    x=df_tien_do['Phòng ban'],
                    y=df_tien_do['Chưa hoàn thành'],
                    marker_color='#ff9800'
                ))
                
                # Cấu hình hiển thị
                fig.update_layout(
                    title='Tiến độ công việc theo phòng ban',
                    xaxis_title='Phòng ban',
                    yaxis_title='Số lượng công việc',
                    barmode='stack'
                )
                
                st.plotly_chart(fig)
            else:
                st.info("Chưa có dữ liệu tiến độ công việc theo phòng ban.")
        
        except sqlite3.Error as e:
            st.error(f"Lỗi truy vấn CSDL: {e}")
        
        finally:
            database.close_db(conn)
    else:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 3: Báo cáo Chấm công
with tab3:
    st.subheader("Phân tích chấm công")
    
    # Kết nối CSDL
    conn = database.connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Lấy dữ liệu theo tháng
            col1, col2 = st.columns([1, 3])
            
            with col1:
                thang_hien_tai = datetime.now().month
                nam_hien_tai = datetime.now().year
                
                chon_thang = st.selectbox(
                    "Chọn tháng:",
                    options=list(range(1, 13)),
                    index=thang_hien_tai - 1
                )
                
                chon_nam = st.selectbox(
                    "Chọn năm:",
                    options=list(range(2020, nam_hien_tai + 1)),
                    index=nam_hien_tai - 2020
                )
            
            # Tính số ngày trong tháng đã chọn
            so_ngay = calendar.monthrange(chon_nam, chon_thang)[1]
            ngay_dau_thang = f"{chon_nam}-{chon_thang:02d}-01"
            ngay_cuoi_thang = f"{chon_nam}-{chon_thang:02d}-{so_ngay:02d}"
            
            # Tính số ngày làm việc trong tháng (không tính cuối tuần)
            so_ngay_lam_viec = 0
            for day in range(1, so_ngay + 1):
                date = datetime(chon_nam, chon_thang, day)
                if date.weekday() < 5:  # 0-4 tương ứng với thứ 2 đến thứ 6
                    so_ngay_lam_viec += 1
            
            # Lấy dữ liệu chấm công trong tháng
            cursor.execute("""
                SELECT cc.MaNhanVien, nv.HoTen, 
                    COUNT(CASE WHEN cc.TrangThai = 'Đi làm' THEN 1 END) as NgayDiLam,
                    COUNT(CASE WHEN cc.TrangThai = 'Nghỉ phép' THEN 1 END) as NgayNghiPhep,
                    COUNT(CASE WHEN cc.TrangThai = 'Nghỉ không phép' THEN 1 END) as NgayNghiKhongPhep
                FROM ChamCong cc
                JOIN NhanVien nv ON cc.MaNhanVien = nv.MaNhanVien
                WHERE cc.NgayLamViec BETWEEN ? AND ?
                GROUP BY cc.MaNhanVien
            """, (ngay_dau_thang, ngay_cuoi_thang))
            
            du_lieu_cham_cong = cursor.fetchall()
            
            # Tổng hợp dữ liệu
            st.markdown(f"### Báo cáo chấm công tháng {chon_thang}/{chon_nam}")
            st.markdown(f"Tổng số ngày làm việc trong tháng: **{so_ngay_lam_viec}** ngày")
            
            if du_lieu_cham_cong:
                # Tạo DataFrame
                df_cham_cong = pd.DataFrame(du_lieu_cham_cong, columns=[
                    "Mã NV", "Họ tên", "Ngày đi làm", "Ngày nghỉ phép", "Ngày nghỉ không phép"
                ])
                
                # Thêm cột tỷ lệ đi làm
                df_cham_cong["Tỷ lệ đi làm (%)"] = (df_cham_cong["Ngày đi làm"] / so_ngay_lam_viec * 100).round(1)
                
                # Hiển thị bảng
                st.dataframe(df_cham_cong)
                
                # Hiển thị biểu đồ
                st.markdown("### So sánh tỷ lệ đi làm")
                
                fig = px.bar(
                    df_cham_cong,
                    x="Họ tên",
                    y="Tỷ lệ đi làm (%)",
                    title=f"Tỷ lệ đi làm tháng {chon_thang}/{chon_nam}",
                    color="Tỷ lệ đi làm (%)",
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                # Thêm đường tham chiếu 100%
                fig.add_hline(
                    y=100, 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text="Mục tiêu 100%", 
                    annotation_position="top right"
                )
                
                st.plotly_chart(fig)
                
                # Thống kê nghỉ phép
                st.markdown("### Thống kê nghỉ phép")
                
                df_nghi_phep = df_cham_cong[["Họ tên", "Ngày nghỉ phép", "Ngày nghỉ không phép"]]
                
                # Chuyển đổi dữ liệu để vẽ biểu đồ
                df_nghi_phep_long = pd.melt(
                    df_nghi_phep, 
                    id_vars=["Họ tên"], 
                    value_vars=["Ngày nghỉ phép", "Ngày nghỉ không phép"],
                    var_name="Loại nghỉ", 
                    value_name="Số ngày"
                )
                
                fig = px.bar(
                    df_nghi_phep_long,
                    x="Họ tên",
                    y="Số ngày",
                    color="Loại nghỉ",
                    barmode="group",
                    title=f"Thống kê nghỉ phép tháng {chon_thang}/{chon_nam}",
                    color_discrete_map={
                        "Ngày nghỉ phép": "#2196f3",
                        "Ngày nghỉ không phép": "#f44336"
                    }
                )
                
                st.plotly_chart(fig)
            else:
                st.info(f"Không có dữ liệu chấm công trong tháng {chon_thang}/{chon_nam}.")
        
        except sqlite3.Error as e:
            st.error(f"Lỗi truy vấn CSDL: {e}")
        
        finally:
            database.close_db(conn)
    else:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
