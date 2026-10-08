import os

from config import DATA_DIR
from config import RESULT_FILE


class ExportModel:

    @staticmethod
    def save(df):

        if not os.path.exists(DATA_DIR):

            os.makedirs(DATA_DIR)

        df.to_excel(

            RESULT_FILE,

            index=False

        )