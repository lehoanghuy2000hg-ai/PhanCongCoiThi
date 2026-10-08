# -*- coding: utf-8 -*-
import pandas as pd

class StandardizeModel:
    @staticmethod
    def process(df):
        if df is None or df.empty:
            return pd.DataFrame()

        df = StandardizeModel.standardize_date(df)
        df = StandardizeModel.create_month(df)
        df = StandardizeModel.create_year(df)
        df = StandardizeModel.create_day(df)
        df = StandardizeModel.create_weekday(df)
        df = StandardizeModel.create_exam_type(df)
        df = StandardizeModel.create_work_time(df)
        df = StandardizeModel.create_role_code(df)
        df = StandardizeModel.create_index(df)

        return df

    @staticmethod
    def standardize_date(df):
        if df.empty:
            return df
        col = next((c for c in df.columns if "ngày" in str(c).lower()), None)
        if col:
            df["Ngày thi"] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        else:
            df["Ngày thi"] = pd.NaT
        return df

    @staticmethod
    def create_month(df):
        if "Ngày thi" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Ngày thi"]):
            df["Tháng"] = df["Ngày thi"].dt.month
        return df

    @staticmethod
    def create_year(df):
        if "Ngày thi" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Ngày thi"]):
            df["Năm"] = df["Ngày thi"].dt.year
        return df

    @staticmethod
    def create_day(df):
        if "Ngày thi" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Ngày thi"]):
            df["Ngày"] = df["Ngày thi"].dt.strftime("%d/%m/%Y")
        return df

    @staticmethod
    def create_weekday(df):
        if "Ngày thi" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Ngày thi"]):
            weekday_map = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ nhật"}
            df["Thứ"] = df["Ngày thi"].dt.weekday.map(weekday_map)
        return df

    @staticmethod
    def create_exam_type(df):
        if df.empty:
            return df
        col = next((c for c in df.columns if "hình thức" in str(c).lower() or "htt" in str(c).lower()), None)
        if col:
            df["Hình thức"] = df[col].apply(lambda x: "Trực tuyến" if "LMS" in str(x).upper() else "Trực tiếp")
        else:
            df["Hình thức"] = "Trực tiếp"
        return df

    @staticmethod
    def create_work_time(df):
        if df.empty:
            return df
        def classify(row):
            dt = row.get("Ngày thi")
            hour = str(row.get("Giờ thi", ""))
            if pd.notna(dt) and hasattr(dt, "weekday") and dt.weekday() >= 5:
                return "Ngoài giờ"
            if "17:30" in hour:
                return "Ngoài giờ"
            return "Trong giờ"

        df["Thời gian"] = df.apply(classify, axis=1)
        return df

    @staticmethod
    def create_role_code(df):
        mapping = {"CBCT1": 1, "CBCT2": 2, "Tiếp nhận thông tin": 3}
        if "Vai trò" in df.columns:
            df["Mã vai trò"] = df["Vai trò"].map(mapping)
        return df

    @staticmethod
    def create_index(df):
        if df.empty:
            return df
        df = df.reset_index(drop=True)
        df.insert(0, "STT", range(1, len(df) + 1))
        return df
