# -*- coding: utf-8 -*-
import os
import io
import streamlit as st
import pandas as pd
from config import RESULT_FILE
from models.summary_model import SummaryModel
from models.payment_model import PaymentModel

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='BaoCao')
    return output.getvalue()

def show_search_page(forced_teacher_name=None):
    st.title("📋 HỆ THỐNG TRA CỨU PHÂN CÔNG COI THI")

    # HIỂN THỊ TÊN TÀI KHOẢN ĐANG ĐĂNG NHẬP
    user_info = st.session_state.get("user_info", {})
    if user_info:
        st.info(f"👤 **Tài khoản đang sử dụng:** `{user_info.get('username', '')}` ({user_info.get('name', '')})")

    df_detail = None
    if os.path.exists(RESULT_FILE):
        try:
            df_detail = pd.read_excel(RESULT_FILE)
        except Exception:
            pass

    if df_detail is None or df_detail.empty:
        if "df_detail" in st.session_state and st.session_state.df_detail is not None:
            df_detail = st.session_state.df_detail

    if df_detail is None or df_detail.empty:
        st.warning("⚠️ Chưa có dữ liệu phân công. Vui lòng vào trang Quản trị để tải file lên.")
        return

    # BỘ LỌC SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 Bộ lọc")

    if forced_teacher_name:
        selected_gv = forced_teacher_name
        st.sidebar.text_input("Giảng viên", value=forced_teacher_name, disabled=True)
    else:
        gv_list = ["Tất cả"] + sorted([str(x) for x in df_detail["Họ tên"].dropna().unique() if str(x).strip() != ""]) if "Họ tên" in df_detail.columns else ["Tất cả"]
        selected_gv = st.sidebar.selectbox("Giảng viên", gv_list)

    thang_list = ["Tất cả"] + sorted([str(int(x)) for x in df_detail["Tháng"].dropna().unique() if pd.notna(x)]) if "Tháng" in df_detail.columns else ["Tất cả"]
    selected_thang = st.sidebar.selectbox("Tháng", thang_list)

    ngay_col = "Ngày" if "Ngày" in df_detail.columns else ("Ngày thi" if "Ngày thi" in df_detail.columns else None)
    ngay_list = ["Tất cả"] + sorted([str(x) for x in df_detail[ngay_col].dropna().unique()]) if ngay_col else ["Tất cả"]
    selected_ngay = st.sidebar.selectbox("Ngày thi", ngay_list)

    vaitro_list = ["Tất cả"] + sorted([str(x) for x in df_detail["Vai trò"].dropna().unique()]) if "Vai trò" in df_detail.columns else ["Tất cả"]
    selected_vaitro = st.sidebar.selectbox("Vai trò", vaitro_list)

    hinhthuc_list = ["Tất cả"] + sorted([str(x) for x in df_detail["Hình thức"].dropna().unique()]) if "Hình thức" in df_detail.columns else ["Tất cả"]
    selected_hinhthuc = st.sidebar.selectbox("Hình thức", hinhthuc_list)

    thoigian_list = ["Tất cả"] + sorted([str(x) for x in df_detail["Thời gian"].dropna().unique()]) if "Thời gian" in df_detail.columns else ["Tất cả"]
    selected_thoigian = st.sidebar.selectbox("Thời gian", thoigian_list)

    if st.sidebar.button("🔄 Làm mới bộ lọc", use_container_width=True):
        st.rerun()

    df_filtered = df_detail.copy()
    if selected_gv != "Tất cả" and "Họ tên" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Họ tên"].astype(str) == selected_gv]
    if selected_thang != "Tất cả" and "Tháng" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Tháng"].astype(str).str.replace(".0", "") == selected_thang]
    if selected_ngay != "Tất cả" and ngay_col:
        df_filtered = df_filtered[df_filtered[ngay_col].astype(str) == selected_ngay]
    if selected_vaitro != "Tất cả" and "Vai trò" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Vai trò"].astype(str) == selected_vaitro]
    if selected_hinhthuc != "Tất cả" and "Hình thức" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Hình thức"].astype(str) == selected_hinhthuc]
    if selected_thoigian != "Tất cả" and "Thời gian" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Thời gian"].astype(str) == selected_thoigian]

    # METRICS
    col1, col2, col3, col4, col5 = st.columns(5)
    def count_dur(df, keyword):
        if "TG (đề)" in df.columns:
            return sum(df["TG (đề)"].astype(str).str.contains(keyword))
        elif "Thời gian" in df.columns:
            return sum(df["Thời gian"].astype(str).str.contains(keyword))
        return 0

    c_tronggio = sum(df_filtered["Thời gian"].astype(str) == "Trong giờ") if "Thời gian" in df_filtered.columns else 0
    c_ngoaigio = sum(df_filtered["Thời gian"].astype(str) == "Ngoài giờ") if "Thời gian" in df_filtered.columns else 0
    c_thi60 = count_dur(df_filtered, "60")
    c_thi75 = count_dur(df_filtered, "75") + count_dur(df_filtered, "90")
    c_thi120 = count_dur(df_filtered, "120")

    with col1:
        st.metric("☀️ Trong giờ", c_tronggio)
    with col2:
        st.metric("🌙 Ngoài giờ", c_ngoaigio)
    with col3:
        st.metric("⏱️ Thi 60", c_thi60)
    with col4:
        st.metric("⏱️ Thi 75-90", c_thi75)
    with col5:
        st.metric("⏱️ Thi 120", c_thi120)

    st.markdown("---")

    # TABS
    tab1, tab2, tab3 = st.tabs(["📄 Chi tiết phân công", "📊 Thống kê", "💰 Thanh toán"])

    with tab1:
        st.subheader("📄 Chi tiết phân công")
        cols_display = [
            "STT", "Họ tên", "Vai trò", "Ngày", "Giờ thi", "Phòng thi", 
            "Tên học phần", "Mã lớp HP", "TG (đề)", "SLSV", "Hình thức", "Thời gian", "Số phiếu CT"
        ]
        
        if "Ngày" not in df_filtered.columns and "Ngày thi" in df_filtered.columns:
            df_filtered["Ngày"] = pd.to_datetime(df_filtered["Ngày thi"], errors="coerce").dt.strftime("%d/%m/%Y")
        if "Số phiếu CT" not in df_filtered.columns and "Mã ca thi" in df_filtered.columns:
            df_filtered["Số phiếu CT"] = df_filtered["Mã ca thi"]

        existing_cols = [c for c in cols_display if c in df_filtered.columns]
        df_show = df_filtered[existing_cols].copy()
        if "STT" in df_show.columns:
            df_show["STT"] = range(1, len(df_show) + 1)

        st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.download_button(
            label="📊 Xuất danh sách chi tiết (Excel)",
            data=to_excel(df_show),
            file_name="Chi_tiet_phan_cong.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.subheader("📊 Thống kê theo giảng viên")
        df_summary = SummaryModel.process(df_filtered)
        cols_to_drop = ["Ngày thi", "Giờ thi", "Phòng thi"]
        df_summary_clean = df_summary.drop(columns=[c for c in cols_to_drop if c in df_summary.columns], errors="ignore")
        st.dataframe(df_summary_clean, use_container_width=True, hide_index=True)

        st.download_button(
            label="📊 Xuất thống kê theo giảng viên (Excel)",
            data=to_excel(df_summary_clean),
            file_name="Thong_ke_phan_cong.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab3:
        st.subheader("💰 Bảng thanh toán")
        df_payment = PaymentModel.calculate(df_filtered)
        cols_to_drop = ["Ngày thi", "Giờ thi", "Phòng thi"]
        df_payment_clean = df_payment.drop(columns=[c for c in cols_to_drop if c in df_payment.columns], errors="ignore")
        st.dataframe(df_payment_clean, use_container_width=True, hide_index=True)

        st.download_button(
            label="💰 Xuất bảng thanh toán (Excel)",
            data=to_excel(df_payment_clean),
            file_name="Bang_thanh_toan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
