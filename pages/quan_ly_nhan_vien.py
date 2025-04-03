import streamlit as st
import sqlite3
import pandas as pd
from utils import database
from datetime import datetime
import hashlib

# Thiết lập tiêu đề trang
st.set_page_config(page_title="Quản lý Nhân viên", page_icon=":office:", layout="wide")

# Kiểm tra quyền truy cập
if "dang_nhap" not in st.session_state or not st.session_state.dang_nhap:
    st.warning("Vui lòng đăng nhập để sử dụng chức năng này.")
    st.stop()

if st.session_state.quyen_han != "admin":
    st.error("Bạn không có quyền truy cập chức năng này.")
    st.stop()

st.title("Quản lý Nhân viên")

# Tạo tabs để phân chia chức năng
tab1, tab2, tab3 = st.tabs(["Tìm kiếm & Xem", "Thêm Nhân viên", "Chỉnh sửa / Xóa"])

# Tab 1: Tìm kiếm và xem danh sách nhân viên
with tab1:
    st.subheader("Tìm kiếm Nhân viên")
    
    # Tạo các tùy chọn tìm kiếm
    col1, col2 = st.columns(2)
    
    with col1:
        search_option = st.selectbox(
            "Tìm kiếm theo:",
            ["Tất cả", "Mã nhân viên", "Tên nhân viên", "Phòng ban", "Vị trí"]
        )
    
    with col2:
        search_text = st.text_input("Nhập từ khóa tìm kiếm:")
    
    # Button tìm kiếm
    if st.button("Tìm kiếm", key="search_btn"):
        # Kết nối CSDL
        conn = database.connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Xây dựng câu truy vấn tùy theo lựa chọn
            query = """
                SELECT NV.MaNhanVien, NV.HoTen, NV.NgaySinh, NV.GioiTinh, 
                       NV.SoDienThoai, NV.Email, PB.TenPhongBan, VT.TenViTri, 
                       NV.NgayVaoCongTy, NV.MucLuong
                FROM NhanVien NV
                LEFT JOIN PhongBan PB ON NV.PhongBanID = PB.PhongBanID
                LEFT JOIN ViTri VT ON NV.ViTriID = VT.ViTriID
            """
            
            params = ()
            
            if search_option == "Mã nhân viên" and search_text:
                query += " WHERE NV.MaNhanVien = ?"
                params = (search_text,)
            elif search_option == "Tên nhân viên" and search_text:
                query += " WHERE NV.HoTen LIKE ?"
                params = (f"%{search_text}%",)
            elif search_option == "Phòng ban" and search_text:
                query += " WHERE PB.TenPhongBan LIKE ?"
                params = (f"%{search_text}%",)
            elif search_option == "Vị trí" and search_text:
                query += " WHERE VT.TenViTri LIKE ?"
                params = (f"%{search_text}%",)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if results:
                # Tạo DataFrame từ kết quả
                df = pd.DataFrame(results, columns=[
                    "Mã NV", "Họ tên", "Ngày sinh", "Giới tính", 
                    "Số điện thoại", "Email", "Phòng ban", "Vị trí", 
                    "Ngày vào công ty", "Mức lương"
                ])
                
                # Hiển thị bảng dữ liệu với khả năng chỉnh sửa
                st.dataframe(df)
                
                # Hiển thị số lượng kết quả tìm được
                st.success(f"Tìm thấy {len(results)} nhân viên.")
                
                # Tùy chọn xem chi tiết nhân viên
                selected_employee = st.selectbox("Chọn nhân viên để xem chi tiết:", 
                                                 [f"{row[0]} - {row[1]}" for row in results])
                
                if selected_employee:
                    employee_id = int(selected_employee.split(" - ")[0])
                    
                    # Lấy thông tin chi tiết nhân viên
                    employee_detail = database.lay_nhan_vien_theo_id(conn, employee_id)
                    
                    if employee_detail:
                        # Hiển thị thông tin chi tiết trong 2 cột
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader(f"Thông tin nhân viên: {employee_detail[1]}")
                            st.write(f"**Mã nhân viên:** {employee_detail[0]}")
                            st.write(f"**Họ tên:** {employee_detail[1]}")
                            st.write(f"**Ngày sinh:** {employee_detail[2]}")
                            st.write(f"**Giới tính:** {employee_detail[3]}")
                            st.write(f"**Địa chỉ:** {employee_detail[4]}")
                            st.write(f"**Số điện thoại:** {employee_detail[5]}")
                            
                        with col2:
                            st.write(f"**Email:** {employee_detail[6]}")
                            
                            # Lấy tên phòng ban
                            if employee_detail[7]:
                                cursor.execute("SELECT TenPhongBan FROM PhongBan WHERE PhongBanID = ?", 
                                            (employee_detail[7],))
                                phong_ban = cursor.fetchone()
                                st.write(f"**Phòng ban:** {phong_ban[0] if phong_ban else 'Không có'}")
                            
                            # Lấy tên vị trí
                            if employee_detail[8]:
                                cursor.execute("SELECT TenViTri FROM ViTri WHERE ViTriID = ?", 
                                            (employee_detail[8],))
                                vi_tri = cursor.fetchone()
                                st.write(f"**Vị trí:** {vi_tri[0] if vi_tri else 'Không có'}")
                            
                            st.write(f"**Ngày vào công ty:** {employee_detail[9]}")
                            st.write(f"**Mức lương:** {employee_detail[10]:,} VND")
                            
                            # Tính thâm niên
                            if employee_detail[9]:
                                ngay_vao = datetime.strptime(employee_detail[9], "%Y-%m-%d")
                                today = datetime.now()
                                tham_nien = (today - ngay_vao).days // 365
                                st.write(f"**Thâm niên:** {tham_nien} năm")
            else:
                st.warning("Không tìm thấy nhân viên nào phù hợp với tiêu chí tìm kiếm.")
            
            database.close_db(conn)
        else:
            st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 2: Thêm nhân viên mới
with tab2:
    st.subheader("Thêm Nhân viên Mới")
    
    # Form nhập thông tin nhân viên mới
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            ho_ten = st.text_input("Họ tên:")
            ngay_sinh = st.date_input("Ngày sinh:")
            gioi_tinh = st.selectbox("Giới tính:", ["Nam", "Nữ", "Khác"])
            dia_chi = st.text_area("Địa chỉ:")
            so_dien_thoai = st.text_input("Số điện thoại:")
            email = st.text_input("Email:")
        
        with col2:
            # Lấy danh sách phòng ban và vị trí từ CSDL
            conn = database.connect_db()
            phong_ban_options = []
            vi_tri_options = []
            
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT PhongBanID, TenPhongBan FROM PhongBan")
                phong_ban_data = cursor.fetchall()
                phong_ban_options = [(pb[0], pb[1]) for pb in phong_ban_data]
                
                cursor.execute("SELECT ViTriID, TenViTri FROM ViTri")
                vi_tri_data = cursor.fetchall()
                vi_tri_options = [(vt[0], vt[1]) for vt in vi_tri_data]
                
                database.close_db(conn)
                
            # Dropdown chọn phòng ban và vị trí
            if phong_ban_options:
                phong_ban_id = st.selectbox("Phòng ban:", 
                                              options=[pb[0] for pb in phong_ban_options],
                                              format_func=lambda x: next((pb[1] for pb in phong_ban_options if pb[0] == x), ""))
            else:
                phong_ban_id = st.number_input("ID Phòng ban:", min_value=1)
                st.warning("Không có dữ liệu phòng ban. Vui lòng thêm phòng ban trước.")
            
            if vi_tri_options:
                vi_tri_id = st.selectbox("Vị trí:", 
                                           options=[vt[0] for vt in vi_tri_options],
                                           format_func=lambda x: next((vt[1] for vt in vi_tri_options if vt[0] == x), ""))
            else:
                vi_tri_id = st.number_input("ID Vị trí:", min_value=1)
                st.warning("Không có dữ liệu vị trí. Vui lòng thêm vị trí trước.")
            
            ngay_vao = st.date_input("Ngày vào công ty:")
            muc_luong = st.number_input("Mức lương (VND):", min_value=0, step=1000000)
            so_cmnd = st.text_input("Số CMND/CCCD:")
            anh_dai_dien = st.text_input("Đường dẫn ảnh đại diện (tùy chọn):")
        
        # Nút submit form
        submit_button = st.form_submit_button("Thêm Nhân viên")
        
        if submit_button:
            conn = database.connect_db()
            if conn:
                # Chuyển đổi ngày sinh và ngày vào công ty sang định dạng chuỗi YYYY-MM-DD
                ngay_sinh_str = ngay_sinh.strftime("%Y-%m-%d")
                ngay_vao_str = ngay_vao.strftime("%Y-%m-%d")
                
                # Gọi hàm thêm nhân viên từ database.py
                new_employee_id = database.them_nhan_vien(
                    conn, ho_ten, ngay_sinh_str, gioi_tinh, dia_chi, 
                    so_dien_thoai, email, phong_ban_id, vi_tri_id, 
                    ngay_vao_str, muc_luong, anh_dai_dien, so_cmnd
                )
                
                if new_employee_id:
                    st.success(f"Đã thêm nhân viên {ho_ten} thành công! Mã nhân viên: {new_employee_id}")
                    
                    # Tùy chọn tạo tài khoản cho nhân viên mới
                    create_account = st.checkbox("Tạo tài khoản cho nhân viên này?")
                    
                    if create_account:
                        username = st.text_input("Tên đăng nhập:")
                        password = st.text_input("Mật khẩu:", type="password")
                        quyen_han = st.selectbox("Quyền hạn:", ["nhanvien", "truongphong", "admin"])
                        
                        if st.button("Tạo tài khoản"):
                            if username and password:
                                # Mã hóa mật khẩu
                                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                                # Tạo tài khoản
                                if database.tao_tai_khoan(conn, username, hashed_password, new_employee_id, quyen_han):
                                    st.success(f"Đã tạo tài khoản cho nhân viên {ho_ten} thành công!")
                                else:
                                    st.error("Tạo tài khoản thất bại. Vui lòng thử lại.")
                            else:
                                st.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                else:
                    st.error("Thêm nhân viên thất bại. Vui lòng kiểm tra lại thông tin.")
                
                database.close_db(conn)
            else:
                st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 3: Chỉnh sửa / Xóa nhân viên
with tab3:
    st.subheader("Chỉnh sửa / Xóa Nhân viên")
    
    # Dropdown chọn nhân viên để chỉnh sửa
    conn = database.connect_db()
    
    if conn:
        nhan_vien_list = database.lay_danh_sach_nhan_vien(conn)
        database.close_db(conn)
        
        if nhan_vien_list:
            selected_employee_id = st.selectbox(
                "Chọn nhân viên cần chỉnh sửa hoặc xóa:",
                options=[nv[0] for nv in nhan_vien_list],
                format_func=lambda x: f"{x} - {next((nv[1] for nv in nhan_vien_list if nv[0] == x), '')}"
            )
            
            if selected_employee_id:
                # Lấy thông tin nhân viên đã chọn
                conn = database.connect_db()
                if conn:
                    nhan_vien = database.lay_nhan_vien_theo_id(conn, selected_employee_id)
                    
                    if nhan_vien:
                        # Hiển thị form chỉnh sửa thông tin nhân viên
                        with st.form("edit_employee_form"):
                            st.subheader(f"Chỉnh sửa thông tin: {nhan_vien[1]}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                ho_ten = st.text_input("Họ tên:", value=nhan_vien[1])
                                
                                # Chuyển đổi chuỗi ngày thành đối tượng datetime nếu có
                                default_dob = None
                                if nhan_vien[2]:
                                    try:
                                        default_dob = datetime.strptime(nhan_vien[2], "%Y-%m-%d")
                                    except:
                                        default_dob = datetime.now()
                                
                                ngay_sinh = st.date_input("Ngày sinh:", value=default_dob if default_dob else datetime.now())
                                gioi_tinh = st.selectbox("Giới tính:", ["Nam", "Nữ", "Khác"], index=["Nam", "Nữ", "Khác"].index(nhan_vien[3]) if nhan_vien[3] in ["Nam", "Nữ", "Khác"] else 0)
                                dia_chi = st.text_area("Địa chỉ:", value=nhan_vien[4] if nhan_vien[4] else "")
                                so_dien_thoai = st.text_input("Số điện thoại:", value=nhan_vien[5] if nhan_vien[5] else "")
                                email = st.text_input("Email:", value=nhan_vien[6] if nhan_vien[6] else "")
                            
                            with col2:
                                # Lấy danh sách phòng ban và vị trí từ CSDL
                                cursor = conn.cursor()
                                
                                cursor.execute("SELECT PhongBanID, TenPhongBan FROM PhongBan")
                                phong_ban_data = cursor.fetchall()
                                phong_ban_options = [(pb[0], pb[1]) for pb in phong_ban_data]
                                
                                cursor.execute("SELECT ViTriID, TenViTri FROM ViTri")
                                vi_tri_data = cursor.fetchall()
                                vi_tri_options = [(vt[0], vt[1]) for vt in vi_tri_data]
                                
                                # Dropdown chọn phòng ban và vị trí
                                if phong_ban_options:
                                    phong_ban_id = st.selectbox(
                                        "Phòng ban:", 
                                        options=[pb[0] for pb in phong_ban_options],
                                        format_func=lambda x: next((pb[1] for pb in phong_ban_options if pb[0] == x), ""),
                                        index=[i for i, pb in enumerate(phong_ban_options) if pb[0] == nhan_vien[7]][0] if nhan_vien[7] in [pb[0] for pb in phong_ban_options] else 0
                                    )
                                else:
                                    phong_ban_id = st.number_input("ID Phòng ban:", value=nhan_vien[7] if nhan_vien[7] else 1, min_value=1)
                                
                                if vi_tri_options:
                                    vi_tri_id = st.selectbox(
                                        "Vị trí:", 
                                        options=[vt[0] for vt in vi_tri_options],
                                        format_func=lambda x: next((vt[1] for vt in vi_tri_options if vt[0] == x), ""),
                                        index=[i for i, vt in enumerate(vi_tri_options) if vt[0] == nhan_vien[8]][0] if nhan_vien[8] in [vt[0] for vt in vi_tri_options] else 0
                                    )
                                else:
                                    vi_tri_id = st.number_input("ID Vị trí:", value=nhan_vien[8] if nhan_vien[8] else 1, min_value=1)
                                
                                # Chuyển đổi chuỗi ngày thành đối tượng datetime nếu có
                                default_join_date = None
                                if nhan_vien[9]:
                                    try:
                                        default_join_date = datetime.strptime(nhan_vien[9], "%Y-%m-%d")
                                    except:
                                        default_join_date = datetime.now()
                                
                                ngay_vao = st.date_input("Ngày vào công ty:", value=default_join_date if default_join_date else datetime.now())
                                
                                # Clean and convert salary value to float, handling different formats
                                def clean_salary(salary_value):
                                    if not salary_value:
                                        return 0.0
                                    if isinstance(salary_value, (int, float)):
                                        return float(salary_value)
                                    # Remove currency symbols and other non-numeric characters
                                    cleaned_value = ''.join(c for c in str(salary_value) if c.isdigit() or c == '.')
                                    try:
                                        return float(cleaned_value)
                                    except (ValueError, TypeError):
                                        return 0.0
                                
                                muc_luong = st.number_input("Mức lương (VND):", value=clean_salary(nhan_vien[10]), min_value=0.0, step=1000000.0)
                                anh_dai_dien = st.text_input("Đường dẫn ảnh đại diện:", value=nhan_vien[11] if nhan_vien[11] else "")
                                so_cmnd = st.text_input("Số CMND/CCCD:", value=nhan_vien[12] if nhan_vien[12] else "")
                            
                            # Nút submit form
                            update_button = st.form_submit_button("Cập nhật thông tin")
                            
                            if update_button:
                                # Chuyển đổi ngày sang định dạng chuỗi YYYY-MM-DD
                                ngay_sinh_str = ngay_sinh.strftime("%Y-%m-%d")
                                ngay_vao_str = ngay_vao.strftime("%Y-%m-%d")
                                
                                # Gọi hàm sửa thông tin nhân viên
                                if database.sua_nhan_vien(
                                    conn, selected_employee_id, ho_ten, ngay_sinh_str, gioi_tinh, 
                                    dia_chi, so_dien_thoai, email, phong_ban_id, vi_tri_id, 
                                    ngay_vao_str, muc_luong, anh_dai_dien, so_cmnd
                                ):
                                    st.success(f"Đã cập nhật thông tin nhân viên {ho_ten} thành công!")
                                else:
                                    st.error("Cập nhật thông tin thất bại. Vui lòng thử lại.")
                        
                        # Nút xóa nhân viên (ngoài form)
                        if st.button(f"Xóa nhân viên: {nhan_vien[1]}", key="delete_button"):
                            confirmation = st.checkbox("Tôi xác nhận muốn xóa nhân viên này", key="confirm_delete")
                            
                            if confirmation:
                                if database.xoa_nhan_vien(conn, selected_employee_id):
                                    st.success(f"Đã xóa nhân viên {nhan_vien[1]} thành công!")
                                    # Tải lại trang để cập nhật danh sách
                                    st.rerun()
                                else:
                                    st.error("Xóa nhân viên thất bại. Vui lòng thử lại.")
                                    st.info("Lưu ý: Nếu nhân viên này có tài khoản hoặc liên kết với dữ liệu khác, bạn cần xóa các liên kết trước.")
                    
                    database.close_db(conn)
                else:
                    st.error("Không thể kết nối đến cơ sở dữ liệu.")
        else:
            st.warning("Không có nhân viên nào trong hệ thống.")
    else:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
