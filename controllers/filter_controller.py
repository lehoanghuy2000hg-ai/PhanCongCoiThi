import unicodedata
import pandas as pd


class FilterController:

    # =====================================================
    # Chuẩn hóa chuỗi
    # =====================================================

    @staticmethod
    def normalize(text):

        if pd.isna(text):
            return ""

        text = str(text).lower().strip()

        text = unicodedata.normalize("NFD", text)

        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn"
        )

        text = text.replace("đ", "d")

        return text

    # =====================================================
    # Danh sách giảng viên
    # =====================================================

    @staticmethod
    def teachers(df):

        teachers = sorted(df["Họ tên"].dropna().unique())

        return ["Tất cả"] + teachers

    # =====================================================
    # Danh sách tháng
    # =====================================================

    @staticmethod
    def months(df):

        months = sorted(df["Tháng"].dropna().unique())

        return ["Tất cả"] + months

    # =====================================================
    # Danh sách ngày
    # =====================================================

    @staticmethod
    def dates(df):

        dates = sorted(df["Ngày"].dropna().unique())

        return ["Tất cả"] + dates

    # =====================================================
    # Vai trò
    # =====================================================

    @staticmethod
    def roles(df):

        roles = sorted(df["Vai trò"].dropna().unique())

        return ["Tất cả"] + roles

    # =====================================================
    # Hình thức
    # =====================================================

    @staticmethod
    def exam_types(df):

        values = sorted(df["Hình thức"].dropna().unique())

        return ["Tất cả"] + values

    # =====================================================
    # Trong/Ngoài giờ
    # =====================================================

    @staticmethod
    def work_times(df):

        values = sorted(df["Thời gian"].dropna().unique())

        return ["Tất cả"] + values

    # =====================================================
    # Cascade Filter
    # =====================================================

    @staticmethod
    def filter(
        df,
        teacher="Tất cả",
        month="Tất cả",
        date="Tất cả",
        role="Tất cả",
        exam_type="Tất cả",
        work_time="Tất cả",
    ):

        result = df.copy()

        if teacher != "Tất cả":

            teacher = FilterController.normalize(teacher)

            result = result[
                result["Họ tên"]
                .apply(FilterController.normalize)
                .str.contains(
                    teacher,
                    case=False,
                    na=False
                )
            ]

        if month != "Tất cả":

            result = result[
                result["Tháng"] == month
            ]

        if date != "Tất cả":

            result = result[
                result["Ngày"] == date
            ]

        if role != "Tất cả":

            result = result[
                result["Vai trò"] == role
            ]

        if exam_type != "Tất cả":

            result = result[
                result["Hình thức"] == exam_type
            ]

        if work_time != "Tất cả":

            result = result[
                result["Thời gian"] == work_time
            ]

        result = result.reset_index(drop=True)

        result["STT"] = result.index + 1

        return result