import streamlit as st
import sqlite3
import pandas as pd
from utils import database
from datetime import datetime, timedelta
from components import header, profile_card, employee_card
import calendar

# Thiết lập tiêu đề trang
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Áp dụng CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "dang_nhap" not in st.session_state or not st.session_state.dang_nhap:
    st.warning("Vui lòng đăng nhập để xem dashboard.")
    st.stop()

# Hiển thị header
header.header(st.session_state.ten_nguoi_dung, st.session_state.quyen_han)

# Lấy thông tin người dùng hiện tại
conn = database.connect_db()
if conn:
    # Lấy thông tin tài khoản
    tai_khoan = database.lay_tai_khoan_theo_ten_dang_nhap(conn, st.session_state.ten_nguoi_dung)
    
    if tai_khoan:
        # Lấy mã nhân viên từ thông tin tài khoản
        ma_nhan_vien = tai_khoan[1]
        
        # Lấy thông tin nhân viên từ bảng NhanVien
        nhan_vien = database.lay_nhan_vien_theo_id(conn, ma_nhan_vien)
        
        if nhan_vien:
            st.title(f"Xin chào, {nhan_vien[1]}!")
            
            # Hiển thị thông tin cơ bản
            col1, col2, col3 = st.columns([1, 2, 1])
            
            # Cột 1: Thông tin nhân viên + Thành tích
            with col1:
                # Hiển thị profile card
                st.subheader("Thông tin cá nhân")
                profile_card.profile_card(nhan_vien)
                
                # Hiển thị thành tích
                st.subheader("Thành tích gần đây")
                
                # Lấy thành tích từ database
                thanh_tich = database.lay_danh_sach_thanh_tich(conn, ma_nhan_vien)
                
                if thanh_tich:
                    # Sắp xếp theo thời gian gần nhất
                    thanh_tich.sort(key=lambda x: x[3] if x[3] else "", reverse=True)
                    
                    # Hiển thị 3 thành tích gần nhất
                    for tt in thanh_tich[:3]:
                        employee_card.achievement_card(tt)
                else:
                    st.info("Bạn chưa có thành tích nào.")
                    
                    # Hiển thị thành tích mẫu nếu không có thành tích thực
                    if st.session_state.quyen_han != "admin":  # Chỉ hiển thị mẫu cho nhân viên thường
                        example_achievement = [
                            0,  # ID
                            "Hoàn thành xuất sắc dự án ABC",  # Tiêu đề
                            "Hoàn thành trước thời hạn 3 ngày với chất lượng cao",  # Mô tả
                            datetime.now().strftime("%Y-%m-%d"),  # Ngày đạt
                            "Xuất sắc",  # Loại thành tích
                            ma_nhan_vien  # Mã nhân viên
                        ]
                        employee_card.achievement_card(example_achievement)
            
            # Cột 2: Công việc và thống kê
            with col2:
                # Hiển thị các công việc hiện tại
                st.subheader("Công việc hiện tại")
                
                # Lấy công việc từ database
                cong_viec = database.lay_danh_sach_cong_viec(conn, ma_nhan_vien)
                
                if cong_viec:
                    # Lọc công việc chưa hoàn thành
                    cong_viec_chua_hoan_thanh = [cv for cv in cong_viec if cv[5] != "Đã hoàn thành"]
                    
                    # Sắp xếp theo deadline gần nhất
                    cong_viec_chua_hoan_thanh.sort(key=lambda x: x[4] if x[4] else "")
                    
                    # Hiển thị tối đa 5 công việc
                    remaining_tasks = len(cong_viec_chua_hoan_thanh)
                    displayed_tasks = min(remaining_tasks, 5)
                    
                    for cv in cong_viec_chua_hoan_thanh[:displayed_tasks]:
                        employee_card.task_card(cv, False)
                    
                    if remaining_tasks > 5:
                        st.info(f"... và {remaining_tasks - 5} công việc khác. [Xem tất cả](/pages/quan_ly_cong_viec)")
                else:
                    st.info("Bạn chưa có công việc nào.")
                    
                    # Hiển thị công việc mẫu nếu không có công việc thực
                    if st.session_state.quyen_han != "admin":  # Chỉ hiển thị mẫu cho nhân viên thường
                        example_task = [
                            0,  # ID
                            "Thiết kế giao diện người dùng mới",  # Tiêu đề
                            "Tạo mẫu giao diện người dùng cho ứng dụng di động",  # Mô tả
                            datetime.now().strftime("%Y-%m-%d"),  # Ngày bắt đầu
                            (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),  # Ngày kết thúc
                            "Đang thực hiện",  # Trạng thái
                            "Cao",  # Mức độ ưu tiên
                            ma_nhan_vien,  # Mã nhân viên
                            None  # Người giao
                        ]
                        employee_card.task_card(example_task, False)
                
                # Hiển thị thống kê ngày làm việc
                st.subheader("Thống kê ngày làm việc")
                
                # Lấy thông tin chấm công
                thang_hien_tai = datetime.now().month
                nam_hien_tai = datetime.now().year
                
                # Tính tổng số ngày trong tháng
                so_ngay_trong_thang = calendar.monthrange(nam_hien_tai, thang_hien_tai)[1]
                
                # Lấy danh sách chấm công trong tháng hiện tại
                ngay_dau_thang = f"{nam_hien_tai}-{thang_hien_tai:02d}-01"
                ngay_cuoi_thang = f"{nam_hien_tai}-{thang_hien_tai:02d}-{so_ngay_trong_thang:02d}"
                
                cham_cong = database.lay_danh_sach_cham_cong(
                    conn, ma_nhan_vien, ngay_dau_thang, ngay_cuoi_thang
                )
                
                # Đếm số ngày đã làm việc
                so_ngay_lam_viec = 0
                if cham_cong:
                    so_ngay_lam_viec = len([cc for cc in cham_cong if cc[5] == "Đi làm"])
                
                # Tính tổng số ngày làm việc (không tính thứ 7, chủ nhật)
                tong_so_ngay = 0
                for day in range(1, so_ngay_trong_thang + 1):
                    date = datetime(nam_hien_tai, thang_hien_tai, day)
                    if date.weekday() < 5:  # 0-4 tương ứng với thứ 2 đến thứ 6
                        tong_so_ngay += 1
                
                # Hiển thị thẻ chấm công
                employee_card.attendance_card(cham_cong, tong_so_ngay, so_ngay_lam_viec)
            
            # Cột 3: Chấm công và thông báo
            with col3:
                # Hiển thị form chấm công 
                st.subheader("Chấm công hôm nay")
                
                # Kiểm tra xem đã chấm công hôm nay chưa
                today = datetime.now().date().strftime("%Y-%m-%d")
                da_cham_cong = False
                
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM ChamCong WHERE MaNhanVien = ? AND NgayLamViec = ?", 
                    (ma_nhan_vien, today)
                )
                cham_cong_hom_nay = cursor.fetchone()
                
                if cham_cong_hom_nay:
                    da_cham_cong = True
                    
                    # Hiện trạng thái đã chấm công
                    st.success(f"Bạn đã chấm công vào lúc: {cham_cong_hom_nay[3]}")
                    
                    if cham_cong_hom_nay[4]:  # Nếu đã có giờ ra
                        st.info(f"Bạn đã check-out lúc: {cham_cong_hom_nay[4]}")
                    else:
                        # Nút check-out
                        if st.button("Check-out"):
                            gio_ra = datetime.now().strftime("%H:%M:%S")
                            database.cap_nhat_cham_cong(
                                conn, 
                                cham_cong_hom_nay[0], 
                                cham_cong_hom_nay[3], 
                                gio_ra, 
                                "Đi làm", 
                                ""
                            )
                            st.success(f"Đã check-out lúc: {gio_ra}")
                            st.rerun()
                else:
                    # Nút check-in
                    if st.button("Check-in"):
                        gio_vao = datetime.now().strftime("%H:%M:%S")
                        database.them_cham_cong(
                            conn,
                            ma_nhan_vien,
                            today,
                            gio_vao,
                            None,
                            "Đi làm",
                            ""
                        )
                        st.success(f"Đã check-in lúc: {gio_vao}")
                        st.rerun()
                
                # Hiển thị thông báo
                st.subheader("Thông báo gần đây")
                
                # Tạo thông báo mẫu
                notifications = [
                    {
                        "title": "Họp nhóm phòng Marketing",
                        "time": "Hôm nay, 15:30",
                        "description": "Phòng họp A3, tầng 3"
                    },
                    {
                        "title": "Bạn có công việc mới",
                        "time": "Hôm qua, 09:15",
                        "description": "Thiết kế banner cho sự kiện tháng 9"
                    },
                    {
                        "title": "Đánh giá hiệu suất Q3",
                        "time": "25/08/2023, 13:00",
                        "description": "Vui lòng hoàn thành báo cáo trước ngày 30/08"
                    }
                ]
                
                # Hiển thị các thông báo
                for notification in notifications:
                    st.markdown(
                        f"""
                        <div style="padding: 10px; border-radius: 8px; background-color: #f5f5f5; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>{notification['title']}</strong>
                                <span style="color: #777; font-size: 0.8em;">{notification['time']}</span>
                            </div>
                            <p style="margin: 5px 0 0 0; color: #555;">{notification['description']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Nút xem tất cả thông báo
                st.markdown("<a href='#' style='display: block; text-align: center;'>Xem tất cả thông báo</a>", unsafe_allow_html=True)
                
                # Hiển thị lịch làm việc
                st.subheader("Lịch làm việc")
                
                # Tạo mẫu lịch làm việc
                today = datetime.now().date()
                weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
                
                # Hiển thị lịch 7 ngày tới
                for i in range(7):
                    date = today + timedelta(days=i)
                    day_of_week = weekdays[date.weekday()]
                    date_str = date.strftime("%d/%m/%Y")
                    
                    # Định dạng màu sắc (highlight ngày hiện tại)
                    if i == 0:
                        bg_color = "#e8f5e9"  # Màu xanh nhạt cho ngày hiện tại
                        border_color = "#4caf50"  # Viền xanh đậm
                    elif date.weekday() >= 5:  # Thứ 7 hoặc Chủ nhật
                        bg_color = "#f5f5f5"  # Màu xám nhạt cho ngày nghỉ
                        border_color = "#9e9e9e"  # Viền xám đậm
                    else:
                        bg_color = "#ffffff"  # Màu trắng cho ngày thường
                        border_color = "#e0e0e0"  # Viền xám nhạt
                    
                    # Hiển thị ngày làm việc với màu sắc tương ứng
                    st.markdown(
                        f"""
                        <div style="padding: 10px; border-radius: 8px; background-color: {bg_color}; 
                                    margin-bottom: 10px; border: 1px solid {border_color};">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>{day_of_week}</strong>
                                <span>{date_str}</span>
                            </div>
                            <div style="margin-top: 5px; font-size: 0.9em;">
                                {"Giờ làm: 8:30 - 17:30" if date.weekday() < 5 else "Ngày nghỉ"}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.error("Không tìm thấy thông tin nhân viên.")
    else:
        st.error("Không tìm thấy thông tin tài khoản.")
    
    database.close_db(conn)
else:
    st.error("Không thể kết nối đến cơ sở dữ liệu.") 