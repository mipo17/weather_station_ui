import streamlit as st
import pandas as pd
import data_wrapper
import staticStrings as ss

# Title
st.title("Wetterdaten Auswertung")

# Connect to SQLite database
conn = st.connection("Wetterdaten_db", type="sql")


years = ['2021','2022', '2023', '2024', '2025']

year_of_interest = st.selectbox("Wähle ein Jahr", years, 0)
feature_of_interest = st.selectbox("Wähle eine Kategorie", [ss.TEMP, ss.SOLAR, ss.WINDSP, ss.HUM, ss.PRECIPACC], 0)


df_to_show = data_wrapper.get_min_max_value_per_month(conn, feature_of_interest, int(year_of_interest))

height = None
if len(df_to_show) > 8:
    height:int = int( 460 * ( len(df_to_show) / 12))

st.dataframe(df_to_show, use_container_width=True, hide_index=True,height=height)
