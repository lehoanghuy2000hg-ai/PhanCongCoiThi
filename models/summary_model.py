# -*- coding: utf-8 -*-
import pandas as pd

class SummaryModel:
    @staticmethod
    def process(df):
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()

        def check_duration(row):
            dur = str(row.get("Thời gian", row.get("TG (đề)", ""))).strip()
            if "60" in dur:
                return "Thi 60"
            elif "75" in dur or "90" in dur:
                return "Thi 75-90"
            elif "120" in dur:
                return "Thi 120"
            return "Thi 75-90"

        df["Thi 60"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 60" else 0, axis=1)
        df["Thi 75-90"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 75-90" else 0, axis=1)
        df["Thi 120"] = df.apply(lambda r: 1 if check_duration(r) == "Thi 120" else 0, axis=1)

        group_cols = ["Giảng viên", "Vai trò", "Hình thức", "Thời gian"]
        group_cols = [c for c in group_cols if c in df.columns]

        grouped = df.groupby(group_cols, as_index=False).agg({
            "Thi 60": "sum",
            "Thi 75-90": "sum",
            "Thi 120": "sum"
        })

        grouped["Tổng số ca"] = grouped["Thi 60"] + grouped["Thi 75-90"] + grouped["Thi 120"]
        return grouped
