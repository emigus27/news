from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import pandas as pd
from textblob import TextBlob




load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")


def fetch_news(api_key, days=30, query="Sweden"):
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

    return pd.DataFrame(all_articles)

def article_per_date(df):
    df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.date
    return df.groupby('publishedAt').size().reset_index(name='article_count')


def analyze_sentiment(text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

def sentiment_category(polarity):
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def sentiment_analysis(df):
    df['sentiment'] = df['description'].fillna('').apply(analyze_sentiment)
    df['sentiment_category'] = df['sentiment'].apply(sentiment_category)
    return df

try:
    df = fetch_news(api_key)
except:
    raise

df = sentiment_analysis(df)
df_stats = article_per_date(df)


sentiment_counts = (df.groupby('publishedAt')['sentiment_category']
                      .value_counts()
                      .unstack(fill_value=0)
                      .reindex(df_stats['publishedAt'])
                      .fillna(0)
                      .rename(columns=lambda c: f"{c}_count"))
df_stats = df_stats.join(sentiment_counts[['positive_count','negative_count','neutral_count']], on='publishedAt').fillna(0)


df_stats.to_csv("data/news_summary.csv", index=False)



