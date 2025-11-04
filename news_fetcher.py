from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from textblob import TextBlob
import time



# load environment variables and get the API key
load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")


# fetch articles day-by-day from NewsAPI
def fetch_news(api_key, days=7, query="Sweden"):
    all_articles = []

    for i in range(days):
        to_date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=i+2)).strftime("%Y-%m-%d")
        url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"searchIn=title,description&"
        f"language=en&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"sortBy=popularity&"
        f"pageSize=100&"
        f"apiKey={api_key}")

        response = requests.get(url)
        if not response.ok:
            raise RuntimeError(f"News API request failed: {response.status_code} {response.text}")

        data = response.json()
        articles = data.get("articles", [])
        all_articles.extend(articles)
        time.sleep(1)

    return pd.DataFrame(all_articles)

# convert timestamps to dates and count articles per day
def article_per_date(df):
    df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.date
    return df.groupby('publishedAt').size().reset_index(name='article_count')


# sentiment scoring helper
def analyze_sentiment(text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

# map numeric polarity to simple categories
def sentiment_category(polarity):
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

# add sentiment and category columns to the DataFrame
def sentiment_analysis(df):
    df['sentiment'] = df['description'].fillna('').apply(analyze_sentiment)
    df['sentiment_category'] = df['sentiment'].apply(sentiment_category)
    return df

# main: fetch, analyze, aggregate, and save summary
if __name__ == "__main__":
    try:
        df = fetch_news(api_key)
        df = sentiment_analysis(df)
        df_stats = article_per_date(df)

        sentiment_counts = (
            df.groupby("publishedAt")["sentiment_category"]
            .value_counts()
            .unstack(fill_value=0)
            .reindex(df_stats["publishedAt"])
            .fillna(0)
            .rename(columns=lambda c: f"{c}_count")
        )

        df_stats = (
            df_stats.join(
                sentiment_counts[["positive_count", "negative_count", "neutral_count"]],
                on="publishedAt",
            )
            .fillna(0)
        )

        # Ensure output directory exists and save
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)
        output_path = os.path.join(data_dir, "news_summary.csv")

        #Append to existing CSV if present
        if os.path.exists(output_path):
            old_df = pd.read_csv(output_path)
            old_df["publishedAt"] = pd.to_datetime(old_df["publishedAt"]).dt.date
            combined = pd.concat([old_df, df_stats], ignore_index=True)
            combined = combined.drop_duplicates(subset=["publishedAt"]).sort_values("publishedAt")
        else:
            combined = df_stats.sort_values("publishedAt")

        combined.to_csv(output_path, index=False)

        
        print(f"Fetched {len(df)} articles from NewsAPI.")
        print(f"Sentiment breakdown:\n{df['sentiment_category'].value_counts()}")

    except Exception as e:
        print(f"Error: {e}")
        raise



