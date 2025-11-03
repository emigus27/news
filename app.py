import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="News Summary", page_icon="📰", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/news_summary.csv")

# --- Load and prepare data ---
df = load_data()
df["publishedAt"] = pd.to_datetime(df["publishedAt"])

# --- Streamlit UI ---
st.title("📰 News Summary Dashboard")
num_days = st.slider("Select number of days to include", 3, 30, 7)

# --- Filter data by date range ---
latest_date = df["publishedAt"].max()
start_date = latest_date - pd.Timedelta(days=num_days - 1)
recent_df = df[df["publishedAt"] >= start_date]

# --- Aggregate sentiment counts for pie chart ---
sentiment_df = (
    recent_df[["positive_count", "negative_count", "neutral_count"]]
    .sum()
    .reset_index()
    .rename(columns={"index": "Sentiment", 0: "Count"})
)
sentiment_df["Sentiment"] = sentiment_df["Sentiment"].str.replace("_count", "").str.capitalize()

# --- Pie chart: Sentiment distribution ---
fig_pie = px.pie(
    sentiment_df,
    names="Sentiment",
    values="Count",
    title=f"Sentiment Distribution (Last {num_days} Days)",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# --- Prepare data for bar chart ---
melted = recent_df.melt(
    id_vars="publishedAt",
    value_vars=["positive_count", "negative_count", "neutral_count"],
    var_name="Sentiment",
    value_name="Count"
)
melted["Sentiment"] = melted["Sentiment"].str.replace("_count", "").str.capitalize()

# --- Bar chart: Articles per day ---
fig_bar = px.bar(
    melted,
    x="publishedAt",
    y="Count",
    color="Sentiment",
    title=f"Articles per Day (Last {num_days} Days)",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    barmode="stack",
    labels={"publishedAt": "Publication Date", "Count": "Number of Articles"}
)

# --- Layout: side-by-side charts ---
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Optional footer / caption ---
st.caption(
    f"Data collected from [NewsAPI.org](https://newsapi.org) — "
    f"showing articles published between **{start_date.date()}** and **{latest_date.date()}**."
)