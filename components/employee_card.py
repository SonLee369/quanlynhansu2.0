import streamlit as st
import datetime

def employee_card(nhan_vien):
    """
    Hiển thị thẻ thông tin tóm tắt nhân viên trong dashboard
    """
    name = nhan_vien[1] if nhan_vien[1] else "Chưa có tên"
    chuc_vu = nhan_vien[8] if nhan_vien[8] else "Chưa có vị trí"
    
    # Lấy ảnh đại diện nếu có
    anh_dai_dien = nhan_vien[11] if nhan_vien[11] else "https://via.placeholder.com/150"
    
    # Tính thâm niên làm việc
    tham_nien = 0
    if nhan_vien[9]:  # Ngày vào công ty
        try:
            ngay_vao = datetime.datetime.strptime(nhan_vien[9], "%Y-%m-%d")
            today = datetime.datetime.now()
            tham_nien = (today - ngay_vao).days // 365
        except:
            tham_nien = 0
    
    # Thiết kế card
    card_css = """
    <style>
        .employee-card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
        }
        .employee-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .employee-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .employee-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 15px;
        }
        .employee-info {
            flex-grow: 1;
        }
        .employee-name {
            font-size: 18px;
            font-weight: bold;
            margin: 0;
            color: #333;
        }
        .employee-position {
            font-size: 14px;
            color: #666;
            margin: 5px 0 0 0;
        }
        .employee-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        .stat-item {
            text-align: center;
            flex-grow: 1;
            padding: 0 10px;
            border-right: 1px solid #eee;
        }
        .stat-item:last-child {
            border-right: none;
        }
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #4caf50;
            margin: 0;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin: 5px 0 0 0;
        }
    </style>
    """
    
    # HTML template cho thẻ nhân viên
    card_html = f"""
    {card_css}
    <div class="employee-card">
        <div class="employee-header">
            <img src="{anh_dai_dien}" class="employee-avatar" alt="Avatar">
            <div class="employee-info">
                <h3 class="employee-name">{name}</h3>
                <p class="employee-position">{chuc_vu}</p>
            </div>
        </div>
        <div class="employee-stats">
            <div class="stat-item">
                <p class="stat-value">{tham_nien}</p>
                <p class="stat-label">Năm làm việc</p>
            </div>
            <div class="stat-item">
                <p class="stat-value">5</p>
                <p class="stat-label">Công việc</p>
            </div>
            <div class="stat-item">
                <p class="stat-value">3</p>
                <p class="stat-label">Thành tích</p>
            </div>
        </div>
    </div>
    """
    
    # Hiển thị HTML
    st.markdown(card_html, unsafe_allow_html=True)

def task_card(task, is_completed=False):
    """
    Hiển thị thẻ công việc/nhiệm vụ trong dashboard
    """
    # Lấy thông tin từ task
    title = task[1] if task[1] else "Công việc không tên"
    description = task[2] if task[2] else "Không có mô tả"
    start_date = task[3] if task[3] else "N/A"
    end_date = task[4] if task[4] else "N/A"
    priority = task[6] if task[6] else "Bình thường"
    
    # Xác định màu sắc dựa trên mức độ ưu tiên
    priority_color = "#4caf50"  # Mặc định: màu xanh lá (bình thường)
    if priority == "Cao":
        priority_color = "#f44336"  # Đỏ
    elif priority == "Thấp":
        priority_color = "#2196f3"  # Xanh dương
    
    # Xác định trạng thái hoàn thành
    status_bg = "#e8f5e9" if is_completed else "#fff8e1"
    status_icon = "✓" if is_completed else "⏳"
    status_text = "Đã hoàn thành" if is_completed else "Đang thực hiện"
    
    # Thiết kế card
    card_css = """
    <style>
        .task-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            border-left: 4px solid var(--priority-color);
            transition: transform 0.2s;
        }
        .task-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .task-title {
            font-size: 16px;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #333;
        }
        .task-description {
            font-size: 14px;
            color: #666;
            margin: 0 0 15px 0;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .task-info {
            display: flex;
            flex-wrap: wrap;
            font-size: 12px;
            color: #666;
        }
        .task-dates {
            margin-right: 15px;
        }
        .task-status {
            margin-left: auto;
            background-color: var(--status-bg);
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .status-icon {
            margin-right: 5px;
        }
    </style>
    """
    
    # HTML template cho thẻ công việc
    card_html = f"""
    {card_css}
    <div class="task-card" style="--priority-color: {priority_color}; --status-bg: {status_bg};">
        <h4 class="task-title">{title}</h4>
        <p class="task-description">{description}</p>
        <div class="task-info">
            <div class="task-dates">
                <span>Bắt đầu: {start_date}</span> | <span>Kết thúc: {end_date}</span>
            </div>
            <div class="task-status">
                <span class="status-icon">{status_icon}</span> {status_text}
            </div>
        </div>
    </div>
    """
    
    # Hiển thị HTML
    st.markdown(card_html, unsafe_allow_html=True)

def achievement_card(achievement):
    """
    Hiển thị thẻ thành tích trong dashboard
    """
    # Lấy thông tin từ thành tích
    title = achievement[1] if achievement[1] else "Thành tích không tên"
    description = achievement[2] if achievement[2] else "Không có mô tả"
    date = achievement[3] if achievement[3] else "N/A"
    category = achievement[4] if achievement[4] else "Khác"
    
    # Xác định biểu tượng dựa trên loại thành tích
    icon = "🏆"  # Mặc định
    if "Xuất sắc" in category:
        icon = "🌟"
    elif "Sáng tạo" in category:
        icon = "💡"
    elif "Teamwork" in category:
        icon = "👥"
    elif "Kỹ năng" in category:
        icon = "🔧"
    
    # Thiết kế card
    card_css = """
    <style>
        .achievement-card {
            background-color: #f3f8ff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            transition: transform 0.2s;
            border: 1px solid #e0e7ff;
        }
        .achievement-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .achievement-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .achievement-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .achievement-title {
            font-size: 16px;
            font-weight: bold;
            margin: 0;
            color: #333;
            flex-grow: 1;
        }
        .achievement-date {
            font-size: 12px;
            color: #666;
        }
        .achievement-description {
            font-size: 14px;
            color: #666;
            margin: 0;
        }
        .achievement-category {
            display: inline-block;
            background-color: #e0e7ff;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 10px;
            color: #3949ab;
        }
    </style>
    """
    
    # HTML template cho thẻ thành tích
    card_html = f"""
    {card_css}
    <div class="achievement-card">
        <div class="achievement-header">
            <div class="achievement-icon">{icon}</div>
            <h4 class="achievement-title">{title}</h4>
            <div class="achievement-date">{date}</div>
        </div>
        <p class="achievement-description">{description}</p>
        <div class="achievement-category">{category}</div>
    </div>
    """
    
    # Hiển thị HTML
    st.markdown(card_html, unsafe_allow_html=True)

def attendance_card(attendance_data, total_days, worked_days):
    """
    Hiển thị thẻ chấm công và ngày làm việc trong dashboard
    """
    # Tính toán phần trăm ngày làm việc
    attendance_percent = (worked_days / total_days * 100) if total_days > 0 else 0
    
    # Thiết kế card
    card_css = """
    <style>
        .attendance-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        .attendance-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .attendance-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin: 0;
        }
        .attendance-summary {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .attendance-stat {
            text-align: center;
            padding: 0 15px;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin: 0;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin: 5px 0 0 0;
        }
        .progress-container {
            width: 100%;
            background-color: #f1f1f1;
            border-radius: 10px;
            margin: 15px 0;
        }
        .progress-bar {
            height: 20px;
            background-color: #4caf50;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            line-height: 20px;
        }
        .attendance-footer {
            text-align: right;
            font-size: 14px;
            color: #666;
        }
    </style>
    """
    
    # HTML template cho thẻ chấm công
    card_html = f"""
    {card_css}
    <div class="attendance-card">
        <div class="attendance-header">
            <h3 class="attendance-title">Thống kê ngày làm việc</h3>
            <span>Tháng {datetime.datetime.now().month}/{datetime.datetime.now().year}</span>
        </div>
        <div class="attendance-summary">
            <div class="attendance-stat">
                <p class="stat-number">{total_days}</p>
                <p class="stat-label">Tổng số ngày</p>
            </div>
            <div class="attendance-stat">
                <p class="stat-number">{worked_days}</p>
                <p class="stat-label">Đã làm việc</p>
            </div>
            <div class="attendance-stat">
                <p class="stat-number">{total_days - worked_days}</p>
                <p class="stat-label">Vắng mặt</p>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {attendance_percent}%;">{attendance_percent:.1f}%</div>
        </div>
        <div class="attendance-footer">
            Cập nhật: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
    </div>
    """
    
    # Hiển thị HTML
    st.markdown(card_html, unsafe_allow_html=True)
