# -*- coding: utf-8 -*-
import os
import pandas as pd
from config import RESULT_FILE
from models.merge_model import MergeModel
from models.split_model import SplitModel
from models.standardize_model import StandardizeModel
from models.export_model import ExportModel

class Processor:
    @staticmethod
    def process(uploaded_file):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext == ".xls":
            df = pd.read_excel(uploaded_file, engine="xlrd")
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        df.columns = df.columns.str.strip()

        df = MergeModel.process(df)
        df = SplitModel.process(df)
        df = StandardizeModel.process(df)

        if not df.empty:
            sort_cols = [c for c in ["Ngày thi", "Giờ thi", "Phòng thi", "Vai trò"] if c in df.columns]
            if sort_cols:
                df = df.sort_values(by=sort_cols, kind="stable").reset_index(drop=True)
            df["STT"] = range(1, len(df) + 1)

        ExportModel.save(df)
        return RESULT_FILE
