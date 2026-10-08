# -*- coding: utf-8 -*-
import os
import streamlit as st
import pandas as pd
from pathlib import Path
from config import APP_TITLE, PAGE_ICON, LAYOUT
from views.search_view import show_search_page
from views.admin_view import show_admin_page

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

ACCOUNTS_FILE = Path("data/accounts.xlsx")

def get_accounts():
    """Đọc dữ liệu tài khoản từ Excel data/accounts.xlsx"""
    if not ACCOUNTS_FILE.exists():
        default_df = pd.DataFrame([
            {"Username": "admin", "Password": "123", "Role": "admin", "FullName": "Ban Quản Trị"},
            {"Username": "tracuu", "Password": "123", "Role": "user", "FullName": "Tài khoản Tra Cứu Chung"}
        ])
        ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_df.to_excel(ACCOUNTS_FILE, index=False)
        return default_df
    try:
        return pd.read_excel(ACCOUNTS_FILE)
    except Exception:
        return pd.DataFrame()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# MÀN HÌNH ĐĂNG NHẬP
if not st.session_state.logged_in:
    st.title("🔑 ĐĂNG NHẬP HỆ THỐNG PHÂN CÔNG COI THI")
    
    with st.form("login_form"):
        username_input = st.text_input("Tên đăng nhập").strip().lower()
        password_input = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")
        
        if submit:
            df_accounts = get_accounts()
            if not df_accounts.empty:
                df_accounts["Username"] = df_accounts["Username"].astype(str).str.strip().str.lower()
                df_accounts["Password"] = df_accounts["Password"].astype(str).str.strip()
                
                match = df_accounts[
                    (df_accounts["Username"] == username_input) & 
                    (df_accounts["Password"] == password_input)
                ]
                
                if not match.empty:
                    user_data = match.iloc[0]
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": user_data["Username"],
                        "name": user_data["FullName"],
                        "role": user_data["Role"]
                    }
                    st.success(f"✅ Đăng nhập thành công! Chào mừng {user_data['FullName']}")
                    st.rerun()
                else:
                    st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác.")
            else:
                st.error("❌ Không đọc được dữ liệu tài khoản.")
    st.stop()

# ĐÃ ĐĂNG NHẬP
user = st.session_state.user_info

with st.sidebar:
    st.title("📋 PHÂN CÔNG COI THI")
    st.info(f"👤 **{user['name']}**\n\nQuyền: **{'Quản trị viên' if user['role'] == 'admin' else 'Tài khoản Tra cứu'}**")
    
    # Phân quyền Menu
    if user["role"] == "admin":
        menu = st.radio("Chức năng", ["Tra cứu lịch phân công", "Quản trị hệ thống"])
    else:
        menu = "Tra cứu lịch phân công"

    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()

if menu == "Tra cứu lịch phân công":
    # Nếu là tài khoản cá nhân giảng viên -> Lọc tên riêng, nếu là tra cứu chung -> Xem tất cả
    forced_teacher = user["name"] if (user["role"] == "user" and user["name"] != "Tài khoản Tra Cứu Chung") else None
    show_search_page(forced_teacher_name=forced_teacher)
else:
    show_admin_page()
