import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from utils import database

def leave_card(title, amount, label, color="blue", icon="calendar-alt"):
    """
    Display a leave information card with modern styling
    
    Args:
        title: Title of the leave card
        amount: Amount of leave (days)
        label: Description label
        color: Color theme for the card (green, blue, red, purple)
        icon: Font Awesome icon name
    """
    html = f"""
    <div class="leave-card leave-card-{color}">
        <div class="leave-header">
            <i class="fas fa-{icon} leave-icon"></i>
            <span class="leave-title">{title}</span>
        </div>
        <div class="leave-body">
            <div class="leave-amount">{amount}</div>
            <div class="leave-label">{label}</div>
            <a href="#" class="leave-button">Record time off</a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def stat_card(title, value, description=None, icon="chart-bar", color="#6c7ae0"):
    """
    Display a statistics card with modern styling
    
    Args:
        title: Title of the stat card
        value: Main value to display
        description: Optional description text
        icon: Font Awesome icon name
        color: Accent color for the card
    """
    desc_html = f'<div class="stat-info">{description}</div>' if description else ''
    html = f"""
    <div class="stat-card">
        <div class="stat-icon" style="color: {color}">
            <i class="fas fa-{icon}"></i>
        </div>
        <div class="stat-title">{title}</div>
        <div class="stat-value" style="color: {color}">{value}</div>
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def employee_leave_dashboard(user_id):
    """
    Display leave information dashboard for an employee
    
    Args:
        user_id: The employee ID
    """
    # Connect to database
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    st.subheader("Thông tin nghỉ phép")
    
    # Create row with leave information cards using st.metric
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Annual Leave", "28.0", "days")
        if st.button("Record time off", key="annual_leave_btn"):
            st.toast("Feature coming soon!")
    
    with col2:
        st.metric("Sick Leave", "15.0", "days")
        if st.button("Record time off", key="sick_leave_btn"):
            st.toast("Feature coming soon!")
    
    with col3:
        st.metric("Without Pay", "0.0", "days")
        if st.button("Record time off", key="unpaid_leave_btn"):
            st.toast("Feature coming soon!")
    
    with col4:
        st.metric("Work from Home", "0.0", "days")
        if st.button("Record time off", key="wfh_btn"):
            st.toast("Feature coming soon!")
    
    # Close connection
    database.close_db(conn)

def time_tracking_stats(user_id):
    """
    Display time tracking statistics for an employee
    
    Args:
        user_id: The employee ID
    """
    # Connect to database
    conn = database.connect_db()
    if not conn:
        st.error("Không thể kết nối đến cơ sở dữ liệu.")
        return
    
    st.subheader("Thống kê chấm công")
    
    # Get current month data
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get attendance data
    days_worked = database.tinh_so_ngay_lam_viec(conn, user_id, current_month, current_year)
    
    # Calculate stats
    weekdays_in_month = 0
    today = datetime.now()
    first_day = datetime(current_year, current_month, 1)
    last_day = (datetime(current_year, current_month + 1, 1) - timedelta(days=1)) if current_month < 12 else datetime(current_year + 1, 1, 1) - timedelta(days=1)
    
    # Count weekdays in current month
    current_date = first_day
    while current_date <= last_day:
        if current_date.weekday() < 5:  # Weekday (0-4 is Monday to Friday)
            weekdays_in_month += 1
        current_date += timedelta(days=1)
    
    # Calculate past weekdays up to today
    past_weekdays = 0
    current_date = first_day
    while current_date <= min(today, last_day):
        if current_date.weekday() < 5:  # Weekday
            past_weekdays += 1
        current_date += timedelta(days=1)
    
    # Use metric widgets for stats instead of custom HTML
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tổng ngày làm việc", 
            f"{days_worked}/{past_weekdays}",
            f"Tháng {current_month}/{current_year}"
        )
    
    with col2:
        absent_days = past_weekdays - days_worked
        st.metric(
            "Ngày vắng mặt", 
            f"{absent_days}",
            f"Tháng {current_month}/{current_year}"
        )
    
    with col3:
        # Get overtime hours (this would require additional database functionality)
        overtime_hours = 0
        st.metric(
            "Giờ làm thêm", 
            f"{overtime_hours}h",
            f"Tháng {current_month}/{current_year}"
        )
    
    with col4:
        # Calculate attendance percentage
        attendance_pct = round((days_worked / past_weekdays) * 100 if past_weekdays > 0 else 0)
        st.metric(
            "Tỷ lệ chuyên cần", 
            f"{attendance_pct}%",
            f"Tháng {current_month}/{current_year}",
            delta_color="normal" if attendance_pct >= 70 else "off"
        )
    
    # Close connection
    database.close_db(conn)

def request_list(user_id):
    """
    Display a list of leave/time off requests with status
    
    Args:
        user_id: The employee ID
    """
    st.markdown("<h3>Yêu cầu</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='filter-label'>Hiển thị 1 - 5 of 13 trong tổng số</div>", unsafe_allow_html=True)
    
    # Create a simple dataframe for the requests
    data = [
        ["Phép năm", "10/01/2025 - 15/01/2025", "Đã duyệt"],
        ["Ốm đau", "05/03/2025", "Chờ duyệt"],
        ["Làm việc tại nhà", "20/03/2025 - 22/03/2025", "Đã duyệt"],
        ["Việc riêng", "15/04/2025", "Từ chối"],
        ["Phép năm", "10/05/2025 - 12/05/2025", "Chờ duyệt"]
    ]
    
    # Display as a Streamlit table
    df = pd.DataFrame(data, columns=["Loại phép", "Thời lượng", "Trạng thái"])
    st.table(df)
    
    # Add view all button
    st.markdown("<div style='text-align: center;'><a href='#' class='view-all-btn'>Xem tất cả</a></div>", unsafe_allow_html=True)

def upcoming_events():
    """
    Display a widget for upcoming events
    """
    st.markdown("<h3>Sự kiện sắp tới</h3>", unsafe_allow_html=True)
    
    # Create simple event cards using st.container
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
            <div style='background-color: #f5f7f9; border-radius: 8px; padding: 10px; text-align: center;'>
                <div style='font-size: 1.5rem; font-weight: 700; color: #333;'>15</div>
                <div style='font-size: 0.7rem; color: #666;'>Tháng 4</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div>
                <div style='font-weight: 600; margin-bottom: 5px;'>Họp phòng ban</div>
                <div style='font-size: 0.8rem; color: #666;'>09:00 - 11:00</div>
                <div style='font-size: 0.8rem; color: #666;'>Phòng họp A</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
            <div style='background-color: #f5f7f9; border-radius: 8px; padding: 10px; text-align: center;'>
                <div style='font-size: 1.5rem; font-weight: 700; color: #333;'>20</div>
                <div style='font-size: 0.7rem; color: #666;'>Tháng 4</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div>
                <div style='font-weight: 600; margin-bottom: 5px;'>Đào tạo kỹ năng mềm</div>
                <div style='font-size: 0.8rem; color: #666;'>14:00 - 17:00</div>
                <div style='font-size: 0.8rem; color: #666;'>Phòng hội thảo</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
            <div style='background-color: #f5f7f9; border-radius: 8px; padding: 10px; text-align: center;'>
                <div style='font-size: 1.5rem; font-weight: 700; color: #333;'>30</div>
                <div style='font-size: 0.7rem; color: #666;'>Tháng 4</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div>
                <div style='font-weight: 600; margin-bottom: 5px;'>Tổng kết tháng</div>
                <div style='font-size: 0.8rem; color: #666;'>16:00 - 17:30</div>
                <div style='font-size: 0.8rem; color: #666;'>Phòng họp lớn</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add view all button
    st.markdown("<div style='text-align: center; margin-top: 10px;'><a href='#' class='view-all-btn'>Xem tất cả</a></div>", unsafe_allow_html=True) 