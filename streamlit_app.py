import streamlit as st
import pandas as pd

# Title
st.title("Temperaturdatenanzeige (2024)")

# Connect to SQLite database
conn = st.connection("Wetterdaten_db", type="sql")


# Get list of tables from SQLite database
table_query = "SELECT name FROM sqlite_master WHERE type='table';"
table_df = conn.query(table_query)
existing_tables = table_df['name'].tolist()

# Supported years
years_to_check = ["2022", "2023", "2024", "2025"]

# SQL templates
queries = {
    year: f"""
        SELECT 
            DATE(datetime) AS date, 
            AVG(temperature) AS mean_temperature
        FROM '{year}'
        GROUP BY DATE(datetime)
        ORDER BY DATE(datetime)
    """
    for year in years_to_check if year in existing_tables
}

# Run only for existing tables
all_years_data = []
for year, query in queries.items():
    df = conn.query(query, ttl="0s")
    df["year"] = year
    all_years_data.append(df)


# Combine all years
df_all = pd.concat(all_years_data)
df_all["date"] = pd.to_datetime(df_all["date"])

# UI: Sidebar Filters
st.sidebar.header("Filter")
year_options = ["Alle", "2022", "2023", "2024", "2025"]
selected_year = st.sidebar.selectbox("Jahr auswählen", year_options)

months_de = {
    "Januar": "01", "Februar": "02", "März": "03", "April": "04",
    "Mai": "05", "Juni": "06", "Juli": "07", "August": "08",
    "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"
}
selected_month = st.sidebar.selectbox("Monat auswählen", ["Alle"] + list(months_de.keys()))

# Month abbreviation mapping for plotting
month_abbr = {
    "01": "Jan", "02": "Feb", "03": "Mär", "04": "Apr", "05": "Mai", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Dez"
}

# Add 'month' column
df_all["month"] = df_all["date"].dt.strftime("%m")
df_all["month_abbr"] = df_all["month"].map(month_abbr)

# --- Monthly Mean Table Overview ---
monthly_overview = (
    df_all
    .groupby(["year", "month_abbr"])["mean_temperature"]
    .mean()
    .reset_index()
)

# Order months for display
month_order = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
monthly_overview["month_abbr"] = pd.Categorical(monthly_overview["month_abbr"], categories=month_order, ordered=True)

# Pivot for overview
overview_table = monthly_overview.pivot(index="month_abbr", columns="year", values="mean_temperature").sort_index()

st.subheader("Monatliche Durchschnittstemperaturen pro Jahr")
st.dataframe(overview_table.style.format("{:.2f} °C"))

# Filter logic
df_filtered = df_all.copy()
if selected_year != "Alle":
    df_filtered = df_filtered[df_filtered["year"] == selected_year]

if selected_month != "Alle":
    month_num = months_de[selected_month]
    df_filtered = df_filtered[df_filtered["date"].dt.strftime("%m") == month_num]

# Display filtered daily data
st.subheader("Tägliche Durchschnittstemperaturen (gefiltert)")
st.dataframe(df_filtered)

# Line chart of daily averages
daily_chart = df_filtered.pivot(index="date", columns="year", values="mean_temperature")
st.subheader("Temperaturverlauf")
st.line_chart(daily_chart)

# --- 2023 vs 2024 Overlay (Tagesvergleich) ---
if "2023" in queries and "2024" in queries:
    df_2023 = all_years_data[1].copy()
    df_2024 = all_years_data[2].copy()

    df_2023["date"] = pd.to_datetime(df_2023["date"])
    df_2024["date"] = pd.to_datetime(df_2024["date"])

    df_2023["day_of_year"] = df_2023["date"].dt.strftime("%j").astype(int)
    df_2024["day_of_year"] = df_2024["date"].dt.strftime("%j").astype(int)

    df_2023.rename(columns={"mean_temperature": "temp_2023"}, inplace=True)
    df_2024.rename(columns={"mean_temperature": "temp_2024"}, inplace=True)

    df_overlay = pd.merge(
        df_2023[["day_of_year", "temp_2023"]],
        df_2024[["day_of_year", "temp_2024"]],
        on="day_of_year",
        how="outer"
    ).sort_values("day_of_year")

    st.subheader("Tagesvergleich: 2023 vs. 2024")
    st.dataframe(df_overlay)
    df_overlay.set_index("day_of_year", inplace=True)
    st.line_chart(df_overlay)
