import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="📰 English-Language News Mentioning Sweden",
    page_icon="📰",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv("data/news_summary.csv")

# load the data and parse dates
df = load_data()
df["publishedAt"] = pd.to_datetime(df["publishedAt"])

# page title and controls
st.title("📰 English-Language News Mentioning Sweden")
num_days = st.slider("Select number of days to include", 3, 30, 7)

# filter rows to the selected date range
latest_date = df["publishedAt"].max()
start_date = latest_date - pd.Timedelta(days=num_days - 1)
recent_df = df[df["publishedAt"] >= start_date]

# sum up sentiment counts for the pie chart
sentiment_df = (
    recent_df[["positive_count", "negative_count", "neutral_count"]]
    .sum()
    .reset_index()
    .rename(columns={"index": "Sentiment", 0: "Count"})
)
sentiment_df["Sentiment"] = sentiment_df["Sentiment"].str.replace("_count", "").str.capitalize()

# define colors: Positive -> green, Neutral -> yellow, Negative -> red
color_map = {"Positive": "#2ca02c", "Neutral": "#f1c40f", "Negative": "#d62728"}

# pie chart showing overall sentiment
fig_pie = px.pie(
    sentiment_df,
    names="Sentiment",
    values="Count",
    title=f"Sentiment Distribution (Last {num_days} Days)",
    color_discrete_map=color_map
)

# prepare stacked bar data by day
melted = recent_df.melt(
    id_vars="publishedAt",
    value_vars=["positive_count", "negative_count", "neutral_count"],
    var_name="Sentiment",
    value_name="Count"
)
melted["Sentiment"] = melted["Sentiment"].str.replace("_count", "").str.capitalize()

# stacked bar chart of articles per day
fig_bar = px.bar(
    melted,
    x="publishedAt",
    y="Count",
    color="Sentiment",
    title=f"Articles per Day (Last {num_days} Days)",
    color_discrete_map=color_map,
    barmode="stack",
    labels={"publishedAt": "Publication Date", "Count": "Number of Articles"}
)

# show charts side by side
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar, use_container_width=True)

# footer with date range
st.caption(
    f"Sentiment analysis performed using **TextBlob**. "
    f"Data collected via **[NewsAPI.org](https://newsapi.org)** — "
    f"covering articles published between **{start_date.date()}** and **{latest_date.date()}**."
)