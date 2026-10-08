import streamlit as st
import pandas as pd
from io import BytesIO

from models.payment_model import PaymentModel


def show_payment(summary_df):

    st.subheader("💰 Bảng thanh toán")

    if summary_df is None or summary_df.empty:

        st.info("Không có dữ liệu thanh toán.")

        return

    payment = PaymentModel.calculate(summary_df)

    if payment.empty:

        st.warning(
            "Chưa có bảng đơn giá hoặc không khớp dữ liệu."
        )

        return

    # ==========================================
    # Tính tổng kinh phí
    # ==========================================

    total_amount = int(
        payment["Tổng tiền"].sum()
    )

    # ==========================================
    # Định dạng hiển thị
    # ==========================================

    display = payment.copy()

    money_cols = [

        "Đơn giá 60",

        "Đơn giá 75-90",

        "Đơn giá 120",

        "Tiền Thi 60",

        "Tiền Thi 75-90",

        "Tiền Thi 120",

        "Tổng tiền"

    ]

    for col in money_cols:

        if col in display.columns:

            display[col] = display[col].map(
                lambda x: f"{int(x):,}"
            )

    # ==========================================
    # Hiển thị
    # ==========================================

    st.dataframe(

        display,

        use_container_width=True,

        hide_index=True,

        height=600

    )

    st.metric(

        "💵 Tổng kinh phí",

        f"{total_amount:,} VNĐ"

    )

    # ==========================================
    # Xuất Excel
    # ==========================================

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        payment.to_excel(

            writer,

            index=False,

            sheet_name="ThanhToan"

        )

    st.download_button(

        "📥 Xuất bảng thanh toán",

        data=output.getvalue(),

        file_name="bang_thanh_toan.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )