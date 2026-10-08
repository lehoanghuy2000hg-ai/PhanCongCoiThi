# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

class PaymentModel:
    PRICE_FILE = Path("data/don_gia.xlsx")

    @classmethod
    def load_price_table(cls):
        if not cls.PRICE_FILE.exists():
            return pd.DataFrame()
        try:
            price = pd.read_excel(cls.PRICE_FILE)
            price.columns = price.columns.astype(str).str.strip()
            for col in ["Nhóm vai trò", "Hình thức", "Thời gian"]:
                if col in price.columns:
                    price[col] = price[col].astype(str).str.strip()
            money_cols = ["Thi 60", "Thi 75-90", "Thi 120"]
            for col in money_cols:
                if col in price.columns:
                    price[col] = pd.to_numeric(price[col], errors="coerce").fillna(0).astype(int)
            return price
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def normalize_role(role):
        role_str = str(role).strip().upper()
        if "CBCT" in role_str:
            return "CBCT"
        return "BTC"

    @classmethod
    def calculate(cls, summary_df):
        if summary_df is None or summary_df.empty:
            return pd.DataFrame()

        price = cls.load_price_table()
        df = summary_df.copy()

        # 1. Đảm bảo có sẵn 3 cột đếm số ca thi
        def check_duration(row):
            dur = str(row.get("Thời gian", row.get("TG (đề)", ""))).strip()
            if "60" in dur:
                return "Thi 60"
            elif "75" in dur or "90" in dur:
                return "Thi 75-90"
            elif "120" in dur:
                return "Thi 120"
            return "Thi 75-90"

        if "Thi 60" not in df.columns:
            df["Thi 60"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 60" else 0, axis=1)
        if "Thi 75-90" not in df.columns:
            df["Thi 75-90"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 75-90" else 0, axis=1)
        if "Thi 120" not in df.columns:
            df["Thi 120"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 120" else 0, axis=1)

        # 2. Ánh xạ nhóm vai trò và đơn giá
        df["Nhóm vai trò"] = df["Vai trò"].apply(cls.normalize_role)
        df["Đơn giá 60"] = 0
        df["Đơn giá 75-90"] = 0
        df["Đơn giá 120"] = 0

        if not price.empty:
            for idx, row in df.iterrows():
                match = price[
                    (price["Nhóm vai trò"] == row.get("Nhóm vai trò", "")) &
                    (price["Hình thức"] == row.get("Hình thức", "")) &
                    (price["Thời gian"] == row.get("Thời gian", ""))
                ]
                if not match.empty:
                    m = match.iloc[0]
                    df.at[idx, "Đơn giá 60"] = int(m.get("Thi 60", 0))
                    df.at[idx, "Đơn giá 75-90"] = int(m.get("Thi 75-90", 0))
                    df.at[idx, "Đơn giá 120"] = int(m.get("Thi 120", 0))

        # 3. Tính thành tiền từng ca
        df["Tiền Thi 60"] = df["Thi 60"] * df["Đơn giá 60"]
        df["Tiền Thi 75-90"] = df["Thi 75-90"] * df["Đơn giá 75-90"]
        df["Tiền Thi 120"] = df["Thi 120"] * df["Đơn giá 120"]

        # 4. Gom nhóm tổng hợp theo Giảng viên (Bỏ Ngày thi, Giờ thi, Phòng thi)
        group_cols = ["Giảng viên", "Vai trò", "Hình thức", "Thời gian"]
        group_cols = [c for c in group_cols if c in df.columns]

        grouped = df.groupby(group_cols, as_index=False).agg({
            "Thi 60": "sum",
            "Thi 75-90": "sum",
            "Thi 120": "sum",
            "Đơn giá 60": "first",
            "Đơn giá 75-90": "first",
            "Đơn giá 120": "first",
            "Tiền Thi 60": "sum",
            "Tiền Thi 75-90": "sum",
            "Tiền Thi 120": "sum"
        })

        grouped["Tổng tiền"] = grouped["Tiền Thi 60"] + grouped["Tiền Thi 75-90"] + grouped["Tiền Thi 120"]
        return grouped
