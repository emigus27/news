import pandas as pd
from textblob import TextBlob


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

df = pd.read_csv("news_articles.csv")
df = sentiment_analysis(df)

