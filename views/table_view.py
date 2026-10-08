import streamlit as st
import pandas as pd


def show_table(df):

    st.subheader("📄 Chi tiết phân công")

    show_cols = [
        "STT",
        "Họ tên",
        "Vai trò",
        "Ngày",
        "Giờ thi",
        "Phòng thi",
        "Tên học phần",
        "Mã lớp HP",
        "TG (đề)",
        "SLSV",
        "Hình thức",
        "Thời gian",
        "Số phiếu CT"
    ]

    cols = [c for c in show_cols if c in df.columns]

    st.dataframe(
        df[cols],
        use_container_width=True,
        hide_index=True,
        height=550
    )


def show_summary_table(df):

    temp = df.copy()

    # ==========================================
    # Chuẩn hóa TG (đề)
    # ==========================================

    temp["TG (đề)"] = (
        temp["TG (đề)"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .fillna(0)
        .astype(int)
    )

    # ==========================================
    # Tạo mã ca thi
    # Một ca = Ngày + Giờ + Phòng
    # ==========================================

    temp["Mã ca thi"] = (
        temp["Ngày"].astype(str).str.strip()
        + "|"
        + temp["Giờ thi"].astype(str).str.strip()
        + "|"
        + temp["Phòng thi"].astype(str).str.strip()
    )

    # ==========================================
    # Một giảng viên chỉ tính 1 lần
    # trong cùng một ca thi
    # ==========================================

    temp = temp.drop_duplicates(
        subset=[
            "Họ tên",
            "Vai trò",
            "Mã ca thi"
        ],
        keep="first"
    )
    # ==========================================
    # Phân loại thời lượng đề
    # ==========================================

    temp["Thi 60"] = (
        temp["TG (đề)"] == 60
    ).astype(int)

    temp["Thi 75-90"] = (
        temp["TG (đề)"].isin([75, 90])
    ).astype(int)

    temp["Thi 120"] = (
        temp["TG (đề)"] == 120
    ).astype(int)

    # ==========================================
    # Thống kê theo giảng viên
    # Có thêm Ngày, Giờ, Phòng
    # ==========================================

    summary = (
        temp.groupby(
            [
                "Họ tên",
                "Vai trò",
                "Hình thức",
                "Thời gian",
                "Ngày",
                "Giờ thi",
                "Phòng thi"
            ],
            as_index=False
        )
        .agg(
            {
                "Thi 60": "sum",
                "Thi 75-90": "sum",
                "Thi 120": "sum"
            }
        )
    )

    # ==========================================
    # Tổng số ca
    # ==========================================

    summary["Tổng số ca"] = (
        summary["Thi 60"]
        + summary["Thi 75-90"]
        + summary["Thi 120"]
    )
    # ==========================================
    # Sắp xếp
    # ==========================================

    summary = summary.sort_values(
        [
            "Họ tên",
            "Ngày",
            "Giờ thi",
            "Phòng thi",
            "Vai trò"
        ]
    ).reset_index(drop=True)

    # ==========================================
    # Đổi tên cột
    # ==========================================

    summary = summary.rename(
        columns={
            "Họ tên": "Giảng viên",
            "Ngày": "Ngày thi"
        }
    )

    # ==========================================
    # Thứ tự cột hiển thị
    # ==========================================

    display_cols = [
        "Giảng viên",
        "Vai trò",
        "Hình thức",
        "Thời gian",
        "Ngày thi",
        "Giờ thi",
        "Phòng thi",
        "Thi 60",
        "Thi 75-90",
        "Thi 120",
        "Tổng số ca"
    ]

    summary = summary[
        [c for c in display_cols if c in summary.columns]
    ]
    # ==========================================
    # Định dạng ngày hiển thị
    # ==========================================

    if "Ngày thi" in summary.columns:

        summary["Ngày thi"] = (
           pd.to_datetime(
               summary["Ngày thi"],
               dayfirst=True,
               errors="coerce"
           )
	   .dt.strftime("%d/%m/%Y")
        )

    # ==========================================
    # Hiển thị
    # ==========================================

    st.subheader("📊 Thống kê theo giảng viên")

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        height=550,
        column_config={
            "Giảng viên": st.column_config.TextColumn(
                "Giảng viên",
                width="medium"
            ),
            "Vai trò": st.column_config.TextColumn(
                "Vai trò",
                width="medium"
            ),
            "Hình thức": st.column_config.TextColumn(
                "Hình thức",
                width="small"
            ),
            "Thời gian": st.column_config.TextColumn(
                "Thời gian",
                width="small"
            ),
            "Ngày thi": st.column_config.TextColumn(
                "Ngày thi",
                width="small"
            ),
            "Giờ thi": st.column_config.TextColumn(
                "Giờ thi",
                width="small"
            ),
            "Phòng thi": st.column_config.TextColumn(
                "Phòng thi",
                width="small"
            ),
            "Thi 60": st.column_config.NumberColumn(
                "Thi 60",
                width="small"
            ),
            "Thi 75-90": st.column_config.NumberColumn(
                "Thi 75-90",
                width="small"
            ),
            "Thi 120": st.column_config.NumberColumn(
                "Thi 120",
                width="small"
            ),
            "Tổng số ca": st.column_config.NumberColumn(
                "Tổng số ca",
                width="small"
            )
        }
    )

    return summary