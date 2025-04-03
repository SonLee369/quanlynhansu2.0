import streamlit as st
from utils import database

def profile_card(nhan_vien_data):
    """Tạo một Profile Card hiện đại với thông tin nhân viên."""

    if not nhan_vien_data:
        st.warning("Không có thông tin nhân viên.")
        return  # Không hiển thị gì nếu không có dữ liệu

    # Lấy thông tin nhân viên
    ma_nhan_vien = nhan_vien_data[0]
    name = nhan_vien_data[1]  # HoTen
    birthdate = nhan_vien_data[2]  # NgaySinh
    gender = nhan_vien_data[3]  # GioiTinh
    address = nhan_vien_data[4]  # DiaChi
    phone = nhan_vien_data[5]  # SoDienThoai
    email = nhan_vien_data[6]  # Email
    phong_ban_id = nhan_vien_data[7]  # PhongBanID
    vi_tri_id = nhan_vien_data[8]  # ViTriID
    join_date = nhan_vien_data[9] or "Chưa cập nhật"  # NgayVaoCongTy
    salary = nhan_vien_data[10]  # MucLuong
    image_url = nhan_vien_data[11] if nhan_vien_data[11] else "https://i.pravatar.cc/300?img=" + str(hash(name) % 70)  # AnhDaiDien

    # Lấy thông tin bổ sung từ database
    conn = database.connect_db()
    position = "Chưa xác định"
    department = "Chưa xác định"
    
    if conn:
        cursor = conn.cursor()
        # Lấy tên phòng ban
        if phong_ban_id:
            cursor.execute("SELECT TenPhongBan FROM PhongBan WHERE PhongBanID = ?", (phong_ban_id,))
            result = cursor.fetchone()
            if result:
                department = result[0]
        
        # Lấy tên vị trí
        if vi_tri_id:
            cursor.execute("SELECT TenViTri FROM ViTri WHERE ViTriID = ?", (vi_tri_id,))
            result = cursor.fetchone()
            if result:
                position = result[0]
        
        database.close_db(conn)

    # Create card container
    with st.container():
        # Add a blue gradient header area for the profile card
        st.markdown(
            f"""
            <div style="background: linear-gradient(90deg, #f0f7ff 0%, #e6f0ff 100%); 
                        height: 150px; 
                        border-radius: 12px 12px 0 0; 
                        position: relative;
                        margin-bottom: 60px;">
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Add profile image overlapping the header
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(image_url, width=120)
        
        with col2:
            st.subheader(name)
            st.caption(position)
        
        # Information sections using expanders
        st.markdown("### Thông tin liên hệ")
        contact_col1, contact_col2 = st.columns(2)
        with contact_col1:
            st.markdown(f"📧 **Email:** {email}")
            st.markdown(f"📞 **Điện thoại:** {phone}")
        with contact_col2:
            st.markdown(f"📍 **Địa chỉ:** {address}")
        
        st.markdown("### Thông tin công việc")
        job_col1, job_col2 = st.columns(2)
        with job_col1:
            st.markdown(f"🏢 **Phòng ban:** {department}")
            st.markdown(f"💼 **Vị trí:** {position}")
        with job_col2:
            st.markdown(f"📅 **Ngày vào công ty:** {join_date}")
            if salary:
                st.markdown(f"💰 **Mức lương:** {format(salary, ',d')} VND")
        
        st.markdown("### Thông tin cá nhân")
        personal_col1, personal_col2 = st.columns(2)
        with personal_col1:
            st.markdown(f"🎂 **Ngày sinh:** {birthdate}")
        with personal_col2:
            st.markdown(f"⚤ **Giới tính:** {gender}")