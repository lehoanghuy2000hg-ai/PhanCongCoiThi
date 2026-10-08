# -*- coding: utf-8 -*-
import os
import streamlit as st
import pandas as pd
from pathlib import Path
from models.processor import Processor

ACCOUNTS_FILE = Path("data/accounts.xlsx")
PRICE_FILE = Path("data/don_gia.xlsx")

def load_accounts():
    if not ACCOUNTS_FILE.exists():
        default_df = pd.DataFrame([
            {"Username": "admin", "Password": "123", "Role": "admin", "FullName": "Ban Quản Trị"},
            {"Username": "tracuu", "Password": "123", "Role": "user", "FullName": "Tài khoản Tra Cứu Chung"},
            {"Username": "gv_phuong", "Password": "123", "Role": "user", "FullName": "Dương Nguyễn Thanh Phương"},
            {"Username": "gv_thin", "Password": "123", "Role": "user", "FullName": "Đặng Thị Thìn"}
        ])
        ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_df.to_excel(ACCOUNTS_FILE, index=False)
        return default_df
    try:
        df = pd.read_excel(ACCOUNTS_FILE)
        for col in ["Username", "Password", "Role", "FullName"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()
        df["Username"] = df["Username"].str.lower()
        return df
    except Exception:
        return pd.DataFrame(columns=["Username", "Password", "Role", "FullName"])

def save_accounts(df):
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    for col in df.columns:
        df[col] = df[col].astype(str)
    df.to_excel(ACCOUNTS_FILE, index=False)

def show_admin_page():
    st.title("⚙️ QUẢN TRỊ HỆ THỐNG")

    user_info = st.session_state.get("user_info", {})
    current_username = user_info.get("username", "N/A")
    current_fullname = user_info.get("name", "N/A")

    st.info(f"👤 **Tài khoản đang đăng nhập:** `{current_username}` ({current_fullname})")

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "📁 Xử lý File Phân công & Đơn giá", 
        "👥 Quản lý Tài khoản (Admin)", 
        "🔐 Đổi mật khẩu cá nhân"
    ])

    # Tab 1: Upload File
    with sub_tab1:
        st.subheader("1. Tải lên File Phân công coi thi (Excel)")
        uploaded_file = st.file_uploader("Chọn tệp Excel phân công (.xlsx, .xls)", type=["xlsx", "xls"], key="assign_file")
        
        if uploaded_file is not None:
            if st.button("🚀 Bắt đầu xử lý dữ liệu phân công", type="primary"):
                try:
                    with st.spinner("Đang xử lý và chuẩn hóa dữ liệu..."):
                        Processor.process(uploaded_file)
                    st.success("✅ Đã xử lý và lưu dữ liệu phân công thành công!")
                except Exception as e:
                    st.error(f"❌ Xảy ra lỗi khi xử lý file phân công: {e}")

        st.markdown("---")

        st.subheader("2. Tải lên / Cập nhật File Đơn giá thù lao (don_gia.xlsx)")
        uploaded_price_file = st.file_uploader("Chọn tệp Excel đơn giá (.xlsx, .xls)", type=["xlsx", "xls"], key="price_file")
        
        if uploaded_price_file is not None:
            if st.button("💾 Lưu file Đơn giá vào hệ thống"):
                try:
                    PRICE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    df_price = pd.read_excel(uploaded_price_file)
                    df_price.to_excel(PRICE_FILE, index=False)
                    st.success("✅ Đã cập nhật thành công file đơn giá `data/don_gia.xlsx`!")
                except Exception as e:
                    st.error(f"❌ Xảy ra lỗi khi lưu file đơn giá: {e}")

    # Tab 2: Quản lý Tài khoản
    with sub_tab2:
        st.subheader("👥 Quản lý & Thêm / Xóa Tài khoản")
        df_acc = load_accounts()

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Tổng số tài khoản", len(df_acc))
        col_m2.metric("Số tài khoản Quản trị (Admin)", len(df_acc[df_acc["Role"] == "admin"]))

        st.markdown("---")

        # Form Thêm
        st.markdown("### ➕ Thêm Tài khoản mới")
        with st.form("add_user_form", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_username = st.text_input("Tên đăng nhập (Username)").strip().lower()
                new_password = st.text_input("Mật khẩu", value="123")
            with col_u2:
                new_fullname = st.text_input("Họ và Tên / Tên hiển thị")
                is_admin = st.checkbox("🔑 Cấp quyền Quản trị (Admin)", value=False)

            submit_add = st.form_submit_button("➕ Thêm tài khoản", use_container_width=True, type="primary")

            if submit_add:
                if not new_username or not new_fullname:
                    st.warning("⚠️ Vui lòng điền đầy đủ Tên đăng nhập và Họ tên!")
                elif new_username in df_acc["Username"].values:
                    st.error(f"❌ Tên đăng nhập `{new_username}` đã tồn tại!")
                else:
                    role_value = "admin" if is_admin else "user"
                    new_row = pd.DataFrame([{
                        "Username": str(new_username),
                        "Password": str(new_password),
                        "Role": str(role_value),
                        "FullName": str(new_fullname)
                    }])
                    updated_df = pd.concat([df_acc, new_row], ignore_index=True)
                    save_accounts(updated_df)
                    st.success(f"🎉 Đã thêm tài khoản `{new_username}` thành công!")
                    st.rerun()

        st.markdown("---")

        # Xóa Tài khoản
        st.markdown("### 🗑️ Xóa Tài khoản")
        user_to_delete = st.selectbox(
            "Chọn tài khoản muốn xóa", 
            options=df_acc["Username"].tolist(),
            format_func=lambda u: f"{u} ({df_acc[df_acc['Username']==u]['FullName'].values[0]})" if not df_acc[df_acc['Username']==u].empty else u
        )
        
        if st.button("❌ Xóa tài khoản này", type="secondary"):
            if user_to_delete == current_username:
                st.error("⚠️ Bạn không thể xóa tài khoản của chính mình khi đang đăng nhập!")
            else:
                updated_df = df_acc[df_acc["Username"] != user_to_delete].reset_index(drop=True)
                save_accounts(updated_df)
                st.success(f"🗑️ Đã xóa thành công tài khoản `{user_to_delete}` khỏi file `data/accounts.xlsx`!")
                st.rerun()

        st.markdown("---")

        # Bảng Data Editor
        st.markdown("### 📋 Danh sách tài khoản hiện có")
        st.caption("💡 Chỉnh sửa trực tiếp thông tin trong bảng bên dưới rồi nhấn **Lưu thay đổi**.")

        for col in ["Username", "Password", "Role", "FullName"]:
            if col in df_acc.columns:
                df_acc[col] = df_acc[col].fillna("").astype(str)

        edited_df = st.data_editor(
            df_acc,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Username": st.column_config.TextColumn("Tên đăng nhập", required=True),
                "Password": st.column_config.TextColumn("Mật khẩu", required=True),
                "Role": st.column_config.SelectboxColumn("Quyền", options=["admin", "user"], default="user", required=True),
                "FullName": st.column_config.TextColumn("Họ tên / Tên hiển thị", required=True)
            },
            hide_index=True
        )

        if st.button("💾 Lưu thay đổi bảng tài khoản vào Excel"):
            save_accounts(edited_df)
            st.success("✅ Đã cập nhật file `data/accounts.xlsx` thành công!")
            st.rerun()

    # Tab 3: Đổi mật khẩu
    with sub_tab3:
        st.subheader(f"🔐 Đổi mật khẩu cho tài khoản `{current_username}`")
        
        with st.form("change_pwd_form", clear_on_submit=True):
            old_pwd = st.text_input("Mật khẩu hiện tại", type="password")
            new_pwd = st.text_input("Mật khẩu mới", type="password")
            confirm_pwd = st.text_input("Xác nhận mật khẩu mới", type="password")
            
            submit_change = st.form_submit_button("🔑 Cập nhật mật khẩu", type="primary")

            if submit_change:
                df_acc = load_accounts()
                user_row = df_acc[df_acc["Username"] == current_username]
                
                if user_row.empty:
                    st.error("❌ Không tìm thấy thông tin tài khoản.")
                elif str(user_row.iloc[0]["Password"]) != str(old_pwd):
                    st.error("❌ Mật khẩu hiện tại không đúng.")
                elif new_pwd != confirm_pwd:
                    st.warning("⚠️ Mật khẩu mới và Xác nhận mật khẩu không trùng khớp!")
                elif not new_pwd:
                    st.warning("⚠️ Mật khẩu mới không được để trống!")
                else:
                    df_acc.loc[df_acc["Username"] == current_username, "Password"] = str(new_pwd)
                    save_accounts(df_acc)
                    st.success("🎉 Đổi mật khẩu thành công! Mật khẩu mới đã được lưu vào file Excel.")
