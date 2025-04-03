import streamlit as st
import datetime
import pandas as pd
from utils import database

def attendance(user_id=None, is_admin=False):
    """
    Component for tracking and managing employee attendance
    
    Args:
        user_id: ID of the current user
        is_admin: Boolean indicating if the user has admin privileges
    """
    st.header("📅 Chấm Công")
    
    # Connect to database
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Chấm công hôm nay", "Lịch sử chấm công", "Báo cáo chấm công"])
    
    # Today's date
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    with tab1:
        st.subheader("Chấm công ngày hôm nay")
        
        # If admin, they can select an employee to check-in
        if is_admin:
            employees = database.lay_danh_sach_nhan_vien(conn)
            employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
            
            selected_employee = st.selectbox(
                "Chọn nhân viên",
                options=[emp[0] for emp in employee_options],
                format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), "")
            )
            check_employee_id = selected_employee
        else:
            # Regular user can only check themselves in
            check_employee_id = user_id
            
            # Get user name for display
            nhan_vien = database.lay_nhan_vien_theo_id(conn, user_id)
            if nhan_vien:
                st.write(f"Nhân viên: **{nhan_vien[1]}**")
        
        # Check if already checked in today
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ChamCong 
                WHERE MaNhanVien = ? AND NgayLamViec = ?
            """, (check_employee_id, today_str))
            todays_record = cursor.fetchone()
        except Exception as e:
            st.error(f"Lỗi kiểm tra chấm công: {e}")
            todays_record = None
            
        # Display current check-in status
        col1, col2 = st.columns(2)
        
        with col1:
            # Current time
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            st.write(f"Ngày: **{today_str}**")
            st.write(f"Thời gian hiện tại: **{current_time}**")
            
            # Attendance status options
            status_options = ["Đi làm", "Làm từ xa", "Nghỉ phép", "Nghỉ ốm", "Vắng mặt"]
            
            if todays_record:
                # Already checked in, show details
                st.info(f"Đã chấm công với trạng thái: **{todays_record[5]}**")
                st.write(f"Giờ vào: **{todays_record[3] or 'Chưa ghi nhận'}**")
                st.write(f"Giờ ra: **{todays_record[4] or 'Chưa ghi nhận'}**")
                
                # Allow check-out if not already checked out
                if not todays_record[4]:  # No check-out time recorded
                    if st.button("Ghi nhận giờ ra"):
                        try:
                            # Update check-out time
                            cursor.execute("""
                                UPDATE ChamCong 
                                SET GioRa = ? 
                                WHERE ChamCongID = ?
                            """, (current_time, todays_record[0]))
                            conn.commit()
                            st.success("Đã ghi nhận giờ ra!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi ghi nhận giờ ra: {e}")
            else:
                # Not checked in yet, show check-in form
                with st.form("checkin_form"):
                    attendance_status = st.selectbox("Trạng thái", status_options)
                    note = st.text_area("Ghi chú", height=100)
                    
                    submit_button = st.form_submit_button("Chấm công")
                    
                    if submit_button:
                        # Only record time if status is "Đi làm" or "Làm từ xa"
                        check_in_time = current_time if attendance_status in ["Đi làm", "Làm từ xa"] else None
                        check_out_time = None  # Will be updated later when checking out
                        
                        try:
                            result = database.them_cham_cong(
                                conn, check_employee_id, today_str, check_in_time, check_out_time, attendance_status, note
                            )
                            
                            if result:
                                st.success("Đã chấm công thành công!")
                                st.rerun()
                            else:
                                st.error("Không thể chấm công. Vui lòng thử lại.")
                        except Exception as e:
                            st.error(f"Lỗi chấm công: {e}")
        
        with col2:
            # Show attendance statistics for the current month if available
            current_month = today.month
            current_year = today.year
            
            try:
                days_worked = database.tinh_so_ngay_lam_viec(conn, check_employee_id, current_month, current_year)
                
                st.write(f"### Thống kê tháng {current_month}/{current_year}")
                st.write(f"Số ngày đi làm: **{days_worked}** ngày")
                
                # More statistics could be added here
            except Exception as e:
                st.error(f"Lỗi tính thống kê: {e}")
    
    with tab2:
        st.subheader("Lịch sử chấm công")
        
        # Date filters
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Từ ngày", today - datetime.timedelta(days=30))
        with col2:
            end_date = st.date_input("Đến ngày", today)
        
        # Format dates for SQLite
        from_date_str = start_date.strftime("%Y-%m-%d")
        to_date_str = end_date.strftime("%Y-%m-%d")
        
        # If admin, they can view any employee's history
        if is_admin:
            employees = database.lay_danh_sach_nhan_vien(conn)
            employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
            
            view_type = st.radio("Xem chấm công", ["Tất cả", "Theo nhân viên"])
            
            if view_type == "Theo nhân viên":
                selected_employee = st.selectbox(
                    "Chọn nhân viên",
                    options=[emp[0] for emp in employee_options],
                    format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), ""),
                    key="history_employee"
                )
                attendance_records = database.lay_danh_sach_cham_cong(conn, selected_employee, from_date_str, to_date_str)
            else:
                attendance_records = database.lay_danh_sach_cham_cong(conn, None, from_date_str, to_date_str)
        else:
            # Regular users can only view their own history
            attendance_records = database.lay_danh_sach_cham_cong(conn, user_id, from_date_str, to_date_str)
        
        # Display attendance records as a table
        if attendance_records:
            # Convert to pandas dataframe for better display
            df_columns = ["ID", "Mã NV", "Ngày làm việc", "Giờ vào", "Giờ ra", "Trạng thái", "Ghi chú", "Tên nhân viên"]
            df = pd.DataFrame(attendance_records, columns=df_columns)
            
            # Display as interactive table
            st.dataframe(df)
            
            # Export option
            if st.button("Xuất Excel"):
                st.info("Chức năng xuất Excel đang được phát triển.")
        else:
            st.info("Không có dữ liệu chấm công trong khoảng thời gian đã chọn.")
    
    with tab3:
        st.subheader("Báo cáo chấm công")
        
        # Only admins can access the full reports
        if is_admin:
            # Month and year selection
            col1, col2 = st.columns(2)
            with col1:
                report_month = st.selectbox("Tháng", list(range(1, 13)), index=today.month - 1)
            with col2:
                report_year = st.selectbox("Năm", list(range(today.year - 2, today.year + 1)), index=2)
                
            # Department filter
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT PhongBanID, TenPhongBan FROM PhongBan")
                departments = cursor.fetchall()
                
                department_options = [("all", "Tất cả phòng ban")] + [(dept[0], dept[1]) for dept in departments]
                selected_dept = st.selectbox(
                    "Phòng ban",
                    options=[dept[0] for dept in department_options],
                    format_func=lambda x: next((dept[1] for dept in department_options if dept[0] == x), "")
                )
            except Exception as e:
                st.error(f"Lỗi lấy danh sách phòng ban: {e}")
                departments = []
                selected_dept = "all"
            
            if st.button("Tạo báo cáo"):
                try:
                    # Get all employees (filtered by department if specified)
                    if selected_dept == "all":
                        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
                    else:
                        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien WHERE PhongBanID = ?", (selected_dept,))
                    
                    employees = cursor.fetchall()
                    
                    if employees:
                        # Create a report dataframe
                        report_data = []
                        
                        for emp in employees:
                            emp_id, emp_name = emp
                            
                            # Calculate attendance statistics
                            days_worked = database.tinh_so_ngay_lam_viec(conn, emp_id, report_month, report_year)
                            
                            # Count different statuses
                            first_day = f"{report_year}-{report_month:02d}-01"
                            last_day = f"{report_year}-{report_month:02d}-31"  # SQL will handle month ends
                            
                            cursor.execute("""
                                SELECT TrangThai, COUNT(*) 
                                FROM ChamCong 
                                WHERE MaNhanVien = ? AND NgayLamViec BETWEEN ? AND ?
                                GROUP BY TrangThai
                            """, (emp_id, first_day, last_day))
                            
                            status_counts = cursor.fetchall()
                            
                            # Calculate various status counts
                            present_count = next((count for status, count in status_counts if status == "Đi làm"), 0)
                            remote_count = next((count for status, count in status_counts if status == "Làm từ xa"), 0)
                            leave_count = next((count for status, count in status_counts if status == "Nghỉ phép"), 0)
                            sick_count = next((count for status, count in status_counts if status == "Nghỉ ốm"), 0)
                            absent_count = next((count for status, count in status_counts if status == "Vắng mặt"), 0)
                            
                            # Add to report
                            report_data.append([
                                emp_id, emp_name, present_count, remote_count, 
                                leave_count, sick_count, absent_count, 
                                present_count + remote_count  # Total working days
                            ])
                        
                        # Create DataFrame and display
                        report_df = pd.DataFrame(
                            report_data, 
                            columns=["Mã NV", "Họ tên", "Đi làm", "Làm từ xa", "Nghỉ phép", "Nghỉ ốm", "Vắng mặt", "Tổng ngày làm việc"]
                        )
                        
                        st.dataframe(report_df)
                        
                        # Visualization
                        st.subheader("Biểu đồ tổng hợp")
                        chart_data = report_df[["Họ tên", "Đi làm", "Làm từ xa", "Nghỉ phép", "Nghỉ ốm", "Vắng mặt"]]
                        chart_data = chart_data.set_index("Họ tên")
                        st.bar_chart(chart_data)
                        
                    else:
                        st.info("Không có nhân viên nào trong bộ lọc đã chọn.")
                    
                except Exception as e:
                    st.error(f"Lỗi tạo báo cáo: {e}")
        else:
            # Regular users can only see their own attendance summary
            try:
                # Show summary for current month
                current_month = today.month
                current_year = today.year
                
                first_day = f"{current_year}-{current_month:02d}-01"
                last_day = f"{current_year}-{current_month:02d}-31"
                
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TrangThai, COUNT(*) 
                    FROM ChamCong 
                    WHERE MaNhanVien = ? AND NgayLamViec BETWEEN ? AND ?
                    GROUP BY TrangThai
                """, (user_id, first_day, last_day))
                
                status_counts = cursor.fetchall()
                
                if status_counts:
                    st.write(f"### Tổng hợp tháng {current_month}/{current_year}")
                    
                    # Calculate statistics
                    present_count = next((count for status, count in status_counts if status == "Đi làm"), 0)
                    remote_count = next((count for status, count in status_counts if status == "Làm từ xa"), 0)
                    leave_count = next((count for status, count in status_counts if status == "Nghỉ phép"), 0)
                    sick_count = next((count for status, count in status_counts if status == "Nghỉ ốm"), 0)
                    absent_count = next((count for status, count in status_counts if status == "Vắng mặt"), 0)
                    
                    # Create a summary table
                    summary_data = {
                        "Trạng thái": ["Đi làm", "Làm từ xa", "Nghỉ phép", "Nghỉ ốm", "Vắng mặt", "Tổng ngày làm việc"],
                        "Số ngày": [present_count, remote_count, leave_count, sick_count, absent_count, present_count + remote_count]
                    }
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.table(summary_df)
                    
                    # Simple chart
                    chart_data = pd.DataFrame({
                        "Số ngày": [present_count, remote_count, leave_count, sick_count, absent_count]
                    }, index=["Đi làm", "Làm từ xa", "Nghỉ phép", "Nghỉ ốm", "Vắng mặt"])
                    
                    st.bar_chart(chart_data)
                else:
                    st.info(f"Không có dữ liệu chấm công trong tháng {current_month}/{current_year}.")
                    
            except Exception as e:
                st.error(f"Lỗi hiển thị báo cáo: {e}")
    
    # Close connection
    database.close_db(conn) 