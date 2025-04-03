import streamlit as st
import datetime
from utils import database

def achievements(user_id=None, is_admin=False):
    """
    Component for managing achievements (thành tích)
    
    Args:
        user_id: ID of the current user
        is_admin: Boolean indicating if the user has admin privileges
    """
    st.header("🏆 Thành Tích")
    
    # Connect to database
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Danh sách thành tích", "Thêm thành tích mới"])
    
    with tab1:
        st.subheader("Danh sách thành tích")
        
        # Filter options
        if is_admin:
            # Admin can see all achievements or filter by employee
            col1, col2 = st.columns(2)
            with col1:
                view_type = st.radio("Xem thành tích", ["Tất cả", "Theo nhân viên"])
            
            with col2:
                if view_type == "Theo nhân viên":
                    employees = database.lay_danh_sach_nhan_vien(conn)
                    employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
                    selected_employee = st.selectbox(
                        "Chọn nhân viên",
                        options=[emp[0] for emp in employee_options],
                        format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), "")
                    )
                    achievements = database.lay_danh_sach_thanh_tich(conn, selected_employee)
                else:
                    achievements = database.lay_danh_sach_thanh_tich(conn)
        else:
            # Regular users can only see their own achievements
            achievements = database.lay_danh_sach_thanh_tich(conn, user_id)
        
        # Filter by type
        achievement_types = ["Tất cả", "Khen thưởng", "Chứng chỉ", "Giải thưởng", "Khác"]
        filter_type = st.selectbox("Lọc theo loại thành tích", achievement_types)
        
        # Apply type filter if not "All"
        if filter_type != "Tất cả" and achievements:
            achievements = [achievement for achievement in achievements if achievement[4] == filter_type]
        
        # Display achievements
        if achievements:
            for achievement in achievements:
                with st.expander(f"{achievement[1]} - {achievement[3]}"):
                    cols = st.columns([2, 1])
                    with cols[0]:
                        st.write(f"**Mô tả:** {achievement[2]}")
                        st.write(f"**Ngày đạt được:** {achievement[3]}")
                    with cols[1]:
                        st.write(f"**Loại thành tích:** {achievement[4]}")
                        st.write(f"**Nhân viên:** {achievement[6]}")
                    
                    # Add delete button for admins
                    if is_admin:
                        if st.button("Xóa thành tích", key=f"delete_{achievement[0]}"):
                            if database.xoa_thanh_tich(conn, achievement[0]):
                                st.success("Đã xóa thành tích thành công!")
                                st.rerun()
                            else:
                                st.error("Không thể xóa thành tích. Vui lòng thử lại.")
        else:
            st.info("Không có thành tích nào.")
    
    with tab2:
        st.subheader("Thêm thành tích mới")
        
        # Only admins can add achievements for other employees
        if is_admin:
            employees = database.lay_danh_sach_nhan_vien(conn)
            employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
        
        # Form for new achievement
        with st.form("new_achievement_form"):
            title = st.text_input("Tiêu đề thành tích")
            description = st.text_area("Mô tả thành tích")
            achievement_date = st.date_input("Ngày đạt được", datetime.date.today())
            achievement_type = st.selectbox("Loại thành tích", ["Khen thưởng", "Chứng chỉ", "Giải thưởng", "Khác"])
            
            if is_admin:
                recipient = st.selectbox(
                    "Nhân viên đạt thành tích",
                    options=[emp[0] for emp in employee_options],
                    format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), "")
                )
            else:
                recipient = user_id  # Regular users can only add achievements for themselves
            
            submit_button = st.form_submit_button("Thêm thành tích")
            
            if submit_button:
                if title and description and achievement_date:
                    # Format dates for SQLite
                    achievement_date_str = achievement_date.strftime("%Y-%m-%d")
                    
                    # Insert new achievement
                    result = database.them_thanh_tich(
                        conn, title, description, achievement_date_str, achievement_type, recipient
                    )
                    
                    if result:
                        st.success("Đã thêm thành tích mới thành công!")
                        # Clear form
                        st.rerun()
                    else:
                        st.error("Không thể thêm thành tích. Vui lòng thử lại.")
                else:
                    st.warning("Vui lòng điền đầy đủ thông tin.")
    
    # Close connection
    database.close_db(conn) 