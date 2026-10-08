import streamlit as st
import pandas as pd


def show_dashboard(df):

    if df.empty:

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🕘 Trong giờ", 0)
        c2.metric("🌙 Ngoài giờ", 0)

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("⏱ Thi 60", 0)
        c6.metric("⏱ Thi 75-90", 0)
        c7.metric("⏱ Thi 120", 0)

        return

    temp = df.copy()

    temp["TG (đề)"] = (
        temp["TG (đề)"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .fillna(0)
        .astype(int)
    )

    temp["Mã ca thi"] = (
        temp["Ngày"].astype(str).str.strip()
        + "|"
        + temp["Giờ thi"].astype(str).str.strip()
        + "|"
        + temp["Phòng thi"].astype(str).str.strip()
    )

    exam = temp.drop_duplicates("Mã ca thi")

    trong_gio = (exam["Thời gian"] == "Trong giờ").sum()
    ngoai_gio = (exam["Thời gian"] == "Ngoài giờ").sum()

    tg60 = (exam["TG (đề)"] == 60).sum()
    tg7590 = exam["TG (đề)"].isin([75, 90]).sum()
    tg120 = (exam["TG (đề)"] == 120).sum()

    c1, c2 = st.columns(2)

    c1.metric("🕘 Trong giờ", int(trong_gio))
    c2.metric("🌙 Ngoài giờ", int(ngoai_gio))

    c3, c4, c5 = st.columns(3)

    c3.metric("⏱ Thi 60", int(tg60))
    c4.metric("⏱ Thi 75-90", int(tg7590))
    c5.metric("⏱ Thi 120", int(tg120))