from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")



def fetch_news(api_key, days=5, max_pages=4):

    to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d") 
    from_date = (datetime.now() - timedelta(days=days+1)).strftime("%Y-%m-%d")  

    page = 1
    all_articles = []

    while page <= max_pages:
        url = (
        f"https://newsapi.org/v2/everything?"
        f"q=Sweden&"
        f"searchIn=title,description&"
        f"language=en&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"sortBy=popularity&"
        f"pageSize=100&"
        f"page={page}&"
        f"apiKey={api_key}")

        response = requests.get(url)
        if not response.ok:
            raise RuntimeError(f"News API request failed: {response.status_code} {response.text}")

        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            break
        all_articles.extend(articles)
        page += 1


    return pd.DataFrame(all_articles)


df = fetch_news(api_key)
print('Fetched', len(df), 'articles')
df.to_csv("news_articles.csv", index=False)


    