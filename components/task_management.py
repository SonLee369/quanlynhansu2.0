import streamlit as st
import datetime
from utils import database

def task_management(user_id=None, is_admin=False):
    """
    Component for managing tasks (công việc)
    
    Args:
        user_id: ID of the current user
        is_admin: Boolean indicating if the user has admin privileges
    """
    st.header("⚙️ Quản lý Công Việc")
    
    # Connect to database
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Danh sách công việc", "Thêm công việc mới", "Cập nhật trạng thái"])
    
    with tab1:
        st.subheader("Danh sách công việc")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Lọc theo trạng thái",
                ["Tất cả", "Chưa hoàn thành", "Đang thực hiện", "Hoàn thành", "Đã hủy"]
            )
        
        with col2:
            if is_admin:
                # Admin can see all tasks or filter by employee
                view_type = st.radio("Xem công việc", ["Tất cả", "Theo nhân viên"])
                if view_type == "Theo nhân viên":
                    employees = database.lay_danh_sach_nhan_vien(conn)
                    employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
                    selected_employee = st.selectbox(
                        "Chọn nhân viên",
                        options=[emp[0] for emp in employee_options],
                        format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), "")
                    )
                    tasks = database.lay_danh_sach_cong_viec(conn, selected_employee)
                else:
                    tasks = database.lay_danh_sach_cong_viec(conn)
            else:
                # Regular user only sees their tasks
                tasks = database.lay_danh_sach_cong_viec(conn, user_id)
        
        # Apply status filter if not "All"
        if filter_status != "Tất cả" and tasks:
            tasks = [task for task in tasks if task[5] == filter_status]
        
        # Display tasks
        if tasks:
            for task in tasks:
                with st.expander(f"{task[1]} - {task[5]}"):
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.write(f"**Mô tả:** {task[2]}")
                        st.write(f"**Thời gian:** {task[3]} - {task[4]}")
                    with cols[1]:
                        st.write(f"**Ưu tiên:** {task[6]}")
                        st.write(f"**Người nhận:** {task[9]}")
                    with cols[2]:
                        st.write(f"**Người giao:** {task[10]}")
                        
                        # Add update button
                        if st.button("Cập nhật", key=f"update_{task[0]}"):
                            st.session_state.selected_task = task[0]
                            st.rerun()
        else:
            st.info("Không có công việc nào.")
            
    with tab2:
        st.subheader("Thêm công việc mới")
        
        # Get list of employees for assignment
        employees = database.lay_danh_sach_nhan_vien(conn)
        employee_options = [(emp[0], emp[1]) for emp in employees] if employees else []
        
        # Form for new task
        with st.form("new_task_form"):
            title = st.text_input("Tiêu đề công việc")
            description = st.text_area("Mô tả công việc")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Ngày bắt đầu", datetime.date.today())
            with col2:
                end_date = st.date_input("Ngày kết thúc", datetime.date.today() + datetime.timedelta(days=7))
            
            col3, col4 = st.columns(2)
            with col3:
                status = st.selectbox("Trạng thái", ["Chưa hoàn thành", "Đang thực hiện", "Hoàn thành", "Đã hủy"])
            with col4:
                priority = st.selectbox("Mức độ ưu tiên", ["Thấp", "Bình thường", "Cao", "Khẩn cấp"])
            
            if is_admin:
                assignee = st.selectbox(
                    "Giao cho nhân viên",
                    options=[emp[0] for emp in employee_options],
                    format_func=lambda x: next((emp[1] for emp in employee_options if emp[0] == x), "")
                )
            else:
                assignee = user_id  # If not admin, can only create tasks for self
            
            submit_button = st.form_submit_button("Thêm công việc")
            
            if submit_button:
                if title and description and start_date and end_date:
                    # Format dates for SQLite
                    start_date_str = start_date.strftime("%Y-%m-%d")
                    end_date_str = end_date.strftime("%Y-%m-%d")
                    
                    # Insert new task
                    result = database.them_cong_viec(
                        conn, title, description, start_date_str, end_date_str, 
                        status, priority, assignee, user_id
                    )
                    
                    if result:
                        st.success("Đã thêm công việc mới thành công!")
                        # Clear form
                        st.rerun()
                    else:
                        st.error("Không thể thêm công việc. Vui lòng thử lại.")
                else:
                    st.warning("Vui lòng điền đầy đủ thông tin.")

    with tab3:
        st.subheader("Cập nhật trạng thái công việc")
        
        # Check if a task was selected for update
        selected_task_id = st.session_state.get('selected_task', None)
        
        # Get tasks for update dropdown
        if is_admin:
            all_tasks = database.lay_danh_sach_cong_viec(conn)
        else:
            all_tasks = database.lay_danh_sach_cong_viec(conn, user_id)
        
        if all_tasks:
            task_options = [(task[0], f"{task[1]} ({task[5]})") for task in all_tasks]
            
            selected_task = st.selectbox(
                "Chọn công việc cần cập nhật",
                options=[task[0] for task in task_options],
                format_func=lambda x: next((task[1] for task in task_options if task[0] == x), ""),
                index=next((i for i, task in enumerate(task_options) if task[0] == selected_task_id), 0) if selected_task_id else 0
            )
            
            # Find the selected task in the list
            task_details = next((task for task in all_tasks if task[0] == selected_task), None)
            
            if task_details:
                new_status = st.selectbox(
                    "Trạng thái mới",
                    ["Chưa hoàn thành", "Đang thực hiện", "Hoàn thành", "Đã hủy"],
                    index=["Chưa hoàn thành", "Đang thực hiện", "Hoàn thành", "Đã hủy"].index(task_details[5]) if task_details[5] in ["Chưa hoàn thành", "Đang thực hiện", "Hoàn thành", "Đã hủy"] else 0
                )
                
                if st.button("Cập nhật trạng thái"):
                    result = database.cap_nhat_trang_thai_cong_viec(conn, selected_task, new_status)
                    if result:
                        st.success(f"Đã cập nhật trạng thái công việc thành '{new_status}'")
                        # Clear selected task
                        if 'selected_task' in st.session_state:
                            del st.session_state.selected_task
                        st.rerun()
                    else:
                        st.error("Không thể cập nhật trạng thái. Vui lòng thử lại.")
        else:
            st.info("Không có công việc nào để cập nhật.")
    
    # Close connection
    database.close_db(conn) 