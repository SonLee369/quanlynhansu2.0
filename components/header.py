import streamlit as st

def header(ten_nguoi_dung=None, quyen_han=None):
    """Tạo header cho trang web với thiết kế hiện đại."""
    
    # Load styles into a class instead of raw HTML
    st.markdown("""
    <style>
    .modern-header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        background-color: white;
        padding: 10px 20px;
        border-bottom: 1px solid #f0f0f0;
    }
    .header-company-name {
        font-size: 24px;
        font-weight: 700;
        color: #333;
        margin-right: 40px;
    }
    .header-company-name span {
        color: #6c7ae0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Determine user image and role display
    user_image = "https://i.pravatar.cc/300?img=" + str(hash(ten_nguoi_dung or "guest") % 70)
    
    role_display = {
        "admin": "Quản trị viên",
        "truongphong": "Trưởng phòng",
        "nhanvien": "Nhân viên"
    }.get(quyen_han, "Khách")
    
    # Create header using Streamlit columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(
            f'<div class="header-company-name">PTIT Telecom<span>.</span></div>',
            unsafe_allow_html=True
        )
    
    with col2:
        # Add search functionality using Streamlit elements
        st.text_input("", placeholder="Tìm kiếm...", label_visibility="collapsed")
    
    with col3:
        # Create user profile information with Streamlit
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: flex-end;">
                <img src="{user_image}" alt="Profile" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 10px;">
                <div>
                    <div style="font-size: 14px; font-weight: 600; color: #333;">{ten_nguoi_dung or 'Khách'}</div>
                    <div style="font-size: 12px; color: #8a94a6;">{role_display}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )