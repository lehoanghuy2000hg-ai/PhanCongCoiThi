import streamlit as st

from controllers.filter_controller import FilterController


class FilterPanel:

    @staticmethod
    def show(df):

        st.sidebar.header("🔍 Bộ lọc")

        # ============================================
        # GIẢNG VIÊN
        # ============================================

        teachers = FilterController.teachers(df)

        teacher = st.sidebar.selectbox(
            "Giảng viên",
            teachers,
            key="teacher"
        )

        temp = FilterController.filter(
            df,
            teacher=teacher
        )

        # ============================================
        # THÁNG
        # ============================================

        months = FilterController.months(temp)

        month = st.sidebar.selectbox(
            "Tháng",
            months,
            key="month"
        )

        temp = FilterController.filter(
            df,
            teacher=teacher,
            month=month
        )

        # ============================================
        # NGÀY THI
        # ============================================

        dates = FilterController.dates(temp)

        exam_date = st.sidebar.selectbox(
            "Ngày thi",
            dates,
            key="date"
        )

        temp = FilterController.filter(
            df,
            teacher=teacher,
            month=month,
            date=exam_date
        )

        # ============================================
        # VAI TRÒ
        # ============================================

        roles = FilterController.roles(temp)

        role = st.sidebar.selectbox(
            "Vai trò",
            roles,
            key="role"
        )

        temp = FilterController.filter(
            df,
            teacher=teacher,
            month=month,
            date=exam_date,
            role=role
        )

        # ============================================
        # HÌNH THỨC
        # ============================================

        exam_types = FilterController.exam_types(temp)

        exam_type = st.sidebar.selectbox(
            "Hình thức",
            exam_types,
            key="exam_type"
        )

        temp = FilterController.filter(
            df,
            teacher=teacher,
            month=month,
            date=exam_date,
            role=role,
            exam_type=exam_type
        )

        # ============================================
        # THỜI GIAN
        # ============================================

        work_times = FilterController.work_times(temp)

        work_time = st.sidebar.selectbox(
            "Thời gian",
            work_times,
            key="work_time"
        )

        # ============================================
        # RESET
        # ============================================

        st.sidebar.divider()

        if st.sidebar.button(
            "🔄 Làm mới bộ lọc",
            use_container_width=True
        ):

            keys = [
                "teacher",
                "month",
                "date",
                "role",
                "exam_type",
                "work_time"
            ]

            for key in keys:

                if key in st.session_state:

                    del st.session_state[key]

            st.rerun()

        return {

            "teacher": teacher,

            "month": month,

            "date": exam_date,

            "role": role,

            "exam_type": exam_type,

            "work_time": work_time

        }