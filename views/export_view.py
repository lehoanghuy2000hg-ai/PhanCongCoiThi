from io import BytesIO

import pandas as pd
import streamlit as st


class ExportView:

    @staticmethod
    def export_excel(
        df,
        label="📥 Xuất Excel",
        filename="phan_cong.xlsx"
    ):

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="xlsxwriter"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="DuLieu"
            )

            workbook = writer.book
            worksheet = writer.sheets["DuLieu"]

            header = workbook.add_format({
                "bold": True,
                "bg_color": "#D9EAD3",
                "border": 1,
                "align": "center",
                "valign": "vcenter"
            })

            cell = workbook.add_format({
                "border": 1,
                "align": "center",
                "valign": "vcenter"
            })

            for col_num, value in enumerate(df.columns):

                worksheet.write(
                    0,
                    col_num,
                    value,
                    header
                )

                width = max(
                    len(str(value)) + 3,
                    18
                )

                worksheet.set_column(
                    col_num,
                    col_num,
                    width,
                    cell
                )

            worksheet.freeze_panes(1, 0)

        st.download_button(
            label=label,
            data=buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=filename
        )