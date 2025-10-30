from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")


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

    return pd.DataFrame(all_articles)


try:
    df = fetch_news(api_key)
    df.to_csv("news_articles.csv", index=False)
except Exception as e:
    if os.path.exists("news_articles.csv"):
        df = pd.read_csv("news_articles.csv")
    else:
        raise


