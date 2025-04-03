import streamlit as st
import sqlite3
import pandas as pd
from utils import database
from datetime import datetime, timedelta
from components import employee_card

# Thiết lập tiêu đề trang
st.set_page_config(page_title="Quản lý Công việc", page_icon="✅", layout="wide")

# Kiểm tra đăng nhập
if "dang_nhap" not in st.session_state or not st.session_state.dang_nhap:
    st.warning("Vui lòng đăng nhập để sử dụng chức năng này.")
    st.stop()

# Lấy thông tin người dùng hiện tại
conn = database.connect_db()
current_user = None
if conn:
    current_user = database.lay_tai_khoan_theo_ten_dang_nhap(conn, st.session_state.ten_nguoi_dung)
    if current_user:
        current_user_id = current_user[1]  # MaNhanVien từ TaiKhoan
        current_user_info = database.lay_nhan_vien_theo_id(conn, current_user_id)
    else:
        st.error("Không tìm thấy thông tin người dùng.")
        database.close_db(conn)
        st.stop()
    database.close_db(conn)
else:
    st.error("Không thể kết nối đến cơ sở dữ liệu.")
    st.stop()

st.title("Quản lý Công việc")

# Tạo tabs để phân chia chức năng
if st.session_state.quyen_han == "admin":
    tabs = st.tabs(["Công việc của tôi", "Giao việc", "Tất cả công việc"])
else:
    tabs = st.tabs(["Công việc của tôi", "Công việc đã hoàn thành"])

# Tab 1: Công việc của tôi
with tabs[0]:
    st.subheader("Công việc của tôi")
    
    # Lấy danh sách công việc của người dùng hiện tại
    conn = database.connect_db()
    if conn:
        tasks = database.lay_danh_sach_cong_viec(conn, current_user_id)
        database.close_db(conn)
        
        if tasks:
            # Phân loại công việc
            todo_tasks = [t for t in tasks if t[5] == "Chưa hoàn thành"]
            in_progress_tasks = [t for t in tasks if t[5] == "Đang thực hiện"]
            done_tasks = [t for t in tasks if t[5] == "Đã hoàn thành"]
            
            # Hiển thị trong 3 cột
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Cần làm")
                for task in todo_tasks:
                    with st.container():
                        employee_card.task_card(task, False)
                        
                        # Nút cập nhật trạng thái
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Bắt đầu làm", key=f"start_{task[0]}"):
                                conn = database.connect_db()
                                if conn:
                                    if database.cap_nhat_trang_thai_cong_viec(conn, task[0], "Đang thực hiện"):
                                        st.success("Đã cập nhật trạng thái!")
                                        st.rerun()
                                    database.close_db(conn)
            
            with col2:
                st.markdown("### Đang thực hiện")
                for task in in_progress_tasks:
                    with st.container():
                        employee_card.task_card(task, False)
                        
                        # Nút cập nhật trạng thái
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Hoàn thành", key=f"complete_{task[0]}"):
                                conn = database.connect_db()
                                if conn:
                                    if database.cap_nhat_trang_thai_cong_viec(conn, task[0], "Đã hoàn thành"):
                                        st.success("Đã cập nhật trạng thái!")
                                        st.rerun()
                                    database.close_db(conn)
                        
                        with col_btn2:
                            if st.button("Quay lại", key=f"back_{task[0]}"):
                                conn = database.connect_db()
                                if conn:
                                    if database.cap_nhat_trang_thai_cong_viec(conn, task[0], "Chưa hoàn thành"):
                                        st.success("Đã cập nhật trạng thái!")
                                        st.rerun()
                                    database.close_db(conn)
            
            with col3:
                st.markdown("### Đã hoàn thành")
                for task in done_tasks:
                    with st.container():
                        employee_card.task_card(task, True)
                        
                        # Nút đánh dấu chưa hoàn thành (nếu cần)
                        if st.button("Đánh dấu chưa hoàn thành", key=f"undo_{task[0]}"):
                            conn = database.connect_db()
                            if conn:
                                if database.cap_nhat_trang_thai_cong_viec(conn, task[0], "Đang thực hiện"):
                                    st.success("Đã cập nhật trạng thái!")
                                    st.rerun()
                                database.close_db(conn)
        else:
            st.info("Bạn chưa có công việc nào.")
    else:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 2: Admin - Giao việc / User - Công việc đã hoàn thành
with tabs[1]:
    if st.session_state.quyen_han == "admin":
        st.subheader("Giao việc cho nhân viên")
        
        # Form giao việc
        with st.form("assign_task_form"):
            # Lấy danh sách nhân viên
            conn = database.connect_db()
            employees = []
            if conn:
                employees = database.lay_danh_sach_nhan_vien(conn)
                database.close_db(conn)
            
            # Dropdowns và inputs
            selected_employee = st.selectbox(
                "Chọn nhân viên:",
                options=[emp[0] for emp in employees],
                format_func=lambda x: f"{x} - {next((emp[1] for emp in employees if emp[0] == x), '')}"
            )
            
            task_title = st.text_input("Tiêu đề công việc:")
            task_desc = st.text_area("Mô tả công việc:")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Ngày bắt đầu:", value=datetime.now())
            with col2:
                end_date = st.date_input("Ngày kết thúc:", value=datetime.now() + timedelta(days=7))
            
            priority = st.selectbox("Mức độ ưu tiên:", ["Thấp", "Bình thường", "Cao"])
            
            submit_button = st.form_submit_button("Giao việc")
            
            if submit_button:
                if task_title and selected_employee:
                    conn = database.connect_db()
                    if conn:
                        # Chuyển đổi ngày thành chuỗi YYYY-MM-DD
                        start_str = start_date.strftime("%Y-%m-%d")
                        end_str = end_date.strftime("%Y-%m-%d")
                        
                        task_id = database.them_cong_viec(
                            conn, 
                            task_title, 
                            task_desc, 
                            start_str, 
                            end_str, 
                            "Chưa hoàn thành", 
                            priority, 
                            selected_employee, 
                            current_user_id
                        )
                        
                        if task_id:
                            st.success(f"Đã giao công việc cho nhân viên thành công! ID: {task_id}")
                        else:
                            st.error("Giao việc thất bại. Vui lòng thử lại.")
                        
                        database.close_db(conn)
                else:
                    st.warning("Vui lòng nhập đầy đủ thông tin công việc.")
        
        # Hiển thị danh sách công việc đã giao
        st.subheader("Công việc đã giao")
        
        conn = database.connect_db()
        if conn:
            # Lấy công việc do người dùng hiện tại giao
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cv.*, nv.HoTen, nguoigiao.HoTen as NguoiGiao
                FROM CongViec cv
                JOIN NhanVien nv ON cv.MaNhanVien = nv.MaNhanVien
                JOIN NhanVien nguoigiao ON cv.NguoiGiao = nguoigiao.MaNhanVien
                WHERE cv.NguoiGiao = ?
            """, (current_user_id,))
            
            assigned_tasks = cursor.fetchall()
            database.close_db(conn)
            
            if assigned_tasks:
                # Tạo DataFrame
                df = pd.DataFrame(
                    assigned_tasks,
                    columns=[
                        "ID", "Tiêu đề", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc", 
                        "Trạng thái", "Ưu tiên", "MaNV", "NguoiGiao", "Nhân viên", "Người giao"
                    ]
                )
                
                # Bỏ các cột không cần thiết
                df = df[["ID", "Tiêu đề", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "Ưu tiên", "Nhân viên"]]
                
                # Hiển thị bảng
                st.dataframe(df)
                
                # Cho phép chọn công việc để xem chi tiết
                selected_task_id = st.selectbox(
                    "Chọn công việc để xem chi tiết:",
                    options=[task[0] for task in assigned_tasks],
                    format_func=lambda x: f"{x} - {next((task[1] for task in assigned_tasks if task[0] == x), '')}"
                )
                
                if selected_task_id:
                    selected_task = next((task for task in assigned_tasks if task[0] == selected_task_id), None)
                    
                    if selected_task:
                        st.subheader(f"Chi tiết công việc: {selected_task[1]}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Mô tả:** {selected_task[2]}")
                            st.write(f"**Ngày bắt đầu:** {selected_task[3]}")
                            st.write(f"**Ngày kết thúc:** {selected_task[4]}")
                        
                        with col2:
                            st.write(f"**Trạng thái:** {selected_task[5]}")
                            st.write(f"**Ưu tiên:** {selected_task[6]}")
                            st.write(f"**Nhân viên thực hiện:** {selected_task[9]}")
                        
                        # Nút cập nhật hoặc xóa
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("Cập nhật trạng thái"):
                                new_status = st.selectbox(
                                    "Chọn trạng thái mới:",
                                    ["Chưa hoàn thành", "Đang thực hiện", "Đã hoàn thành"]
                                )
                                
                                if st.button("Xác nhận cập nhật"):
                                    conn = database.connect_db()
                                    if conn:
                                        if database.cap_nhat_trang_thai_cong_viec(conn, selected_task_id, new_status):
                                            st.success("Đã cập nhật trạng thái công việc!")
                                            st.rerun()
                                        else:
                                            st.error("Cập nhật thất bại. Vui lòng thử lại.")
                                        database.close_db(conn)
                        
                        with col_btn2:
                            if st.button("Xóa công việc"):
                                confirm = st.checkbox("Tôi xác nhận muốn xóa công việc này")
                                
                                if confirm and st.button("Xác nhận xóa"):
                                    conn = database.connect_db()
                                    if conn:
                                        if database.xoa_cong_viec(conn, selected_task_id):
                                            st.success("Đã xóa công việc thành công!")
                                            st.rerun()
                                        else:
                                            st.error("Xóa công việc thất bại. Vui lòng thử lại.")
                                        database.close_db(conn)
            else:
                st.info("Bạn chưa giao công việc nào.")
        else:
            st.error("Không thể kết nối đến cơ sở dữ liệu.")
    else:
        # Tab Công việc đã hoàn thành cho người dùng thường
        st.subheader("Công việc đã hoàn thành")
        
        conn = database.connect_db()
        if conn:
            # Lấy các công việc đã hoàn thành
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cv.*, nv.HoTen as NguoiNhan, ng.HoTen as NguoiGiao
                FROM CongViec cv
                LEFT JOIN NhanVien nv ON cv.MaNhanVien = nv.MaNhanVien
                LEFT JOIN NhanVien ng ON cv.NguoiGiao = ng.MaNhanVien
                WHERE cv.MaNhanVien = ? AND cv.TrangThai = 'Đã hoàn thành'
                ORDER BY cv.NgayKetThuc DESC
            """, (current_user_id,))
            
            completed_tasks = cursor.fetchall()
            database.close_db(conn)
            
            if completed_tasks:
                # Hiển thị danh sách công việc đã hoàn thành
                for task in completed_tasks:
                    employee_card.task_card(task, True)
                    
                # Hiển thị thống kê
                st.subheader("Thống kê công việc")
                
                # Tính tổng số công việc đã hoàn thành
                total_completed = len(completed_tasks)
                
                # Tính số công việc đã hoàn thành trong tháng hiện tại
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                this_month_tasks = [
                    t for t in completed_tasks 
                    if t[4] and datetime.strptime(t[4], "%Y-%m-%d").month == current_month
                    and datetime.strptime(t[4], "%Y-%m-%d").year == current_year
                ]
                
                this_month_completed = len(this_month_tasks)
                
                # Hiển thị số liệu
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Tổng số công việc đã hoàn thành", total_completed)
                
                with col2:
                    st.metric("Công việc hoàn thành trong tháng này", this_month_completed)
            else:
                st.info("Bạn chưa có công việc đã hoàn thành nào.")
        else:
            st.error("Không thể kết nối đến cơ sở dữ liệu.")

# Tab 3: Admin - Tất cả công việc
if st.session_state.quyen_han == "admin":
    with tabs[2]:
        st.subheader("Tất cả công việc trong hệ thống")
        
        # Lấy tất cả công việc trong hệ thống
        conn = database.connect_db()
        if conn:
            all_tasks = database.lay_danh_sach_cong_viec(conn)
            database.close_db(conn)
            
            if all_tasks:
                # Tạo DataFrame
                df = pd.DataFrame(
                    all_tasks,
                    columns=[
                        "ID", "Tiêu đề", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc", 
                        "Trạng thái", "Ưu tiên", "MaNV", "NguoiGiao", "Nhân viên", "Người giao"
                    ]
                )
                
                # Bỏ các cột không cần thiết
                df = df[["ID", "Tiêu đề", "Ngày bắt đầu", "Ngày kết thúc", "Trạng thái", "Ưu tiên", "Nhân viên", "Người giao"]]
                
                # Lọc dữ liệu
                st.markdown("### Lọc dữ liệu")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filter_status = st.multiselect(
                        "Lọc theo trạng thái:",
                        options=["Chưa hoàn thành", "Đang thực hiện", "Đã hoàn thành"],
                        default=[]
                    )
                
                with col2:
                    filter_priority = st.multiselect(
                        "Lọc theo ưu tiên:",
                        options=["Thấp", "Bình thường", "Cao"],
                        default=[]
                    )
                
                with col3:
                    date_filter = st.radio(
                        "Lọc theo thời gian:",
                        ["Tất cả", "Tuần này", "Tháng này", "Quá hạn"]
                    )
                
                # Áp dụng bộ lọc
                filtered_df = df.copy()
                
                if filter_status:
                    filtered_df = filtered_df[filtered_df["Trạng thái"].isin(filter_status)]
                
                if filter_priority:
                    filtered_df = filtered_df[filtered_df["Ưu tiên"].isin(filter_priority)]
                
                if date_filter != "Tất cả":
                    today = datetime.now().date()
                    
                    if date_filter == "Tuần này":
                        start_of_week = today - timedelta(days=today.weekday())
                        end_of_week = start_of_week + timedelta(days=6)
                        
                        filtered_df = filtered_df[
                            (pd.to_datetime(filtered_df["Ngày kết thúc"]).dt.date >= start_of_week) &
                            (pd.to_datetime(filtered_df["Ngày kết thúc"]).dt.date <= end_of_week)
                        ]
                    
                    elif date_filter == "Tháng này":
                        start_of_month = today.replace(day=1)
                        
                        # Tìm ngày cuối tháng
                        if today.month == 12:
                            end_of_month = today.replace(day=31)
                        else:
                            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
                        
                        filtered_df = filtered_df[
                            (pd.to_datetime(filtered_df["Ngày kết thúc"]).dt.date >= start_of_month) &
                            (pd.to_datetime(filtered_df["Ngày kết thúc"]).dt.date <= end_of_month)
                        ]
                    
                    elif date_filter == "Quá hạn":
                        filtered_df = filtered_df[
                            (pd.to_datetime(filtered_df["Ngày kết thúc"]).dt.date < today) &
                            (filtered_df["Trạng thái"] != "Đã hoàn thành")
                        ]
                
                # Hiển thị kết quả lọc
                st.dataframe(filtered_df)
                
                # Thống kê
                st.markdown("### Thống kê công việc")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_tasks = len(df)
                    st.metric("Tổng số công việc", total_tasks)
                
                with col2:
                    completed_tasks = len(df[df["Trạng thái"] == "Đã hoàn thành"])
                    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                    st.metric("Tỷ lệ hoàn thành", f"{completion_rate:.1f}%")
                
                with col3:
                    in_progress_tasks = len(df[df["Trạng thái"] == "Đang thực hiện"])
                    st.metric("Đang thực hiện", in_progress_tasks)
                
                with col4:
                    # Tính số công việc quá hạn
                    today = datetime.now().date()
                    overdue_tasks = len(df[
                        (pd.to_datetime(df["Ngày kết thúc"]).dt.date < today) &
                        (df["Trạng thái"] != "Đã hoàn thành")
                    ])
                    st.metric("Công việc quá hạn", overdue_tasks)
                
                # Biểu đồ thống kê
                st.markdown("### Biểu đồ phân bố công việc")
                
                # Biểu đồ trạng thái
                status_counts = df["Trạng thái"].value_counts().reset_index()
                status_counts.columns = ["Trạng thái", "Số lượng"]
                
                st.bar_chart(status_counts, x="Trạng thái", y="Số lượng")
            else:
                st.info("Chưa có công việc nào trong hệ thống.")
        else:
            st.error("Không thể kết nối đến cơ sở dữ liệu.") 