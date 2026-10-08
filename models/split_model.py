# -*- coding: utf-8 -*-
import re
import pandas as pd

class SplitModel:
    PATTERN = re.compile(r"^(.*?)\((.*?)\)$", re.UNICODE)

    @staticmethod
    def process(df):
        if df is None or df.empty:
            return pd.DataFrame()

        cbct_col = None
        for col in df.columns:
            col_str = str(col).strip().lower()
            if "phân công" in col_str or "cbct" in col_str:
                cbct_col = col
                break

        if not cbct_col:
            return df

        rows = []
        for _, row in df.iterrows():
            text = str(row.get(cbct_col, "")).strip()

            if text == "" or text.lower() in ["nan", "none", "null"]:
                continue

            people = SplitModel.split_people(text)
            for person in people:
                result = SplitModel.extract_person(person)
                if result is None:
                    continue

                new_row = row.copy()

                date_col = next((c for c in df.columns if "ngày" in str(c).lower()), "Ngày thi")
                time_col = next((c for c in df.columns if "giờ" in str(c).lower()), "Giờ thi")
                type_col = next((c for c in df.columns if "hình thức" in str(c).lower() or "htt" in str(c).lower()), "Hình thức")
                dur_col = next((c for c in df.columns if "tg" in str(c).lower() or "thời gian" in str(c).lower()), "Thời gian")

                new_row["Ngày thi"] = row.get(date_col, "N/A")
                new_row["Giờ thi"] = row.get(time_col, "N/A")
                new_row["Hình thức"] = row.get(type_col, "N/A")
                new_row["Thời gian"] = row.get(dur_col, "N/A")

                new_row["Họ tên"] = result["name"]
                new_row["Giảng viên"] = result["name"]
                new_row["Vai trò"] = result["role"]

                rows.append(new_row)

        return pd.DataFrame(rows) if rows else pd.DataFrame()

    @staticmethod
    def split_people(text):
        text = text.replace("\n", ",").replace(";", ",")
        return [x.strip() for x in text.split(",") if x.strip() != ""]

    @staticmethod
    def extract_person(text):
        text = text.strip()
        if not text:
            return None

        m = SplitModel.PATTERN.search(text)
        if m:
            name = m.group(1).strip()
            role_raw = m.group(2).strip().upper()
            role_part = role_raw.split("-")[0].strip()

            if "CBCT1" in role_part:
                role = "CBCT1"
            elif "CBCT2" in role_part:
                role = "CBCT2"
            else:
                role = role_part if role_part else "CBCT"
        else:
            name = text
            role = "CBCT"

        return {"name": name, "role": role}
