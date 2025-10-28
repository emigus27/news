from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta
import requests

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("NEWS_API_KEY not found in .env file")



def fetch_news(api_key, days=5):

    to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d") 
    from_date = (datetime.now() - timedelta(days=days+1)).strftime("%Y-%m-%d")  

    url = (
    f"https://newsapi.org/v2/everything?"
    f"q=Sweden&"
    f"searchIn=title,description&"
    f"language=en&"
    f"from={from_date}&"
    f"to={to_date}&"
    f"sortBy=popularity&"
    f"pageSize=100&"
    f"apiKey={api_key}")

    response = requests.get(url)
    return pd.DataFrame(response.json().get("articles", [])
)


df = fetch_news(api_key)
print(f"Fetched {len(df)} articles")
df.to_csv("news_articles.csv", index=False)


    