# -*- coding: utf-8 -*-
import pandas as pd

class MergeModel:
    @staticmethod
    def process(df):
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()

        # 1. Tìm tiêu đề cột nếu bị tụt dòng
        has_date_col = any("ngày" in str(col).lower() for col in df.columns)
        if not has_date_col:
            for idx, row in df.iterrows():
                row_str = " ".join(row.astype(str).values).lower()
                if "ngày" in row_str or "phân công" in row_str or "buổi" in row_str:
                    df.columns = df.iloc[idx].values
                    df = df.iloc[idx + 1:].reset_index(drop=True)
                    break

        df.columns = [str(col).strip() for col in df.columns]

        # 2. Định danh chính xác 1 ca thi gộp = [Số phiếu CT (hoặc Mã ca thi) + Ngày thi + Giờ thi + Phòng thi]
        group_cols = []
        for col_candidate in ["Số phiếu CT", "Mã ca thi"]:
            if col_candidate in df.columns:
                group_cols.append(col_candidate)
                break

        for c in ["Ngày thi", "Giờ thi", "Phòng thi"]:
            if c in df.columns and c not in group_cols:
                group_cols.append(c)

        if not group_cols:
            return df

        # Chuẩn hóa thời gian đề thi về kiểu số để lấy thời gian lớn nhất
        dur_col = next((c for c in df.columns if "tg" in str(c).lower() or "thời gian" in str(c).lower()), None)
        if dur_col:
            df["TG_num"] = pd.to_numeric(df[dur_col].astype(str).str.extract(r'(\d+)')[0], errors="coerce").fillna(0)

        # 3. Định nghĩa hàm gộp tên chuỗi không lặp và SLSV dạng "11 + 23"
        def join_unique(series):
            vals = [str(s).strip() for s in series.dropna() if str(s).strip() not in ["", "nan", "None"]]
            seen = set()
            out = []
            for v in vals:
                if v not in seen:
                    seen.add(v)
                    out.append(v)
            return " / ".join(out)

        def join_slsv(series):
            vals = []
            for s in series.dropna():
                val_num = pd.to_numeric(s, errors="coerce")
                if pd.notna(val_num):
                    vals.append(str(int(val_num)))
            return " + ".join(vals) if vals else ""

        agg_dict = {}
        for col in df.columns:
            if col in group_cols or col == "TG_num":
                continue
            if col in ["Tên học phần", "Mã lớp HP", "Mã ca thi", "Hình thức thi", "Phân công CBCT"]:
                agg_dict[col] = join_unique
            elif col in ["SLSV"]:
                agg_dict[col] = join_slsv
            else:
                agg_dict[col] = "first"

        if "TG_num" in df.columns:
            agg_dict["TG_num"] = "max"

        grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)

        if "TG_num" in grouped.columns:
            if dur_col:
                grouped[dur_col] = grouped["TG_num"].astype(int).astype(str) + " phút"
            grouped = grouped.drop(columns=["TG_num"])

        return grouped
