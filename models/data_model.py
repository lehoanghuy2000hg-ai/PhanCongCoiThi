import os
import pandas as pd
import streamlit as st

from config import RESULT_FILE


class DataModel:

    @staticmethod
    @st.cache_data
    def load_data():

        if not os.path.exists(RESULT_FILE):

            return pd.DataFrame()

        return pd.read_excel(RESULT_FILE)

    @staticmethod
    def reload():

        DataModel.load_data.clear()