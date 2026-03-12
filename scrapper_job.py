import praw
import pandas as pd
import re
from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")
#api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)


reddit = praw.Reddit(
    client_id="Sluh_7-LceBQjGQ3i61INg",
    client_secret="8LBSwWgIzYEvCitUWz56zL28qf0gQQ",
    user_agent="reddit_sentiment_bot"
)


def clean_text_list(posts):

    cleaned = []

    for p in posts:
        text = re.sub(r"http\S+|@\w+|[^A-Za-z0-9\s]", "", str(p))
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 5:
            cleaned.append(text)

    return cleaned


def classify_sentiment(text):

    prompt = f"""
    Classify sentiment of the post.

    Return only one word:

    Positive
    Neutral
    Negative

    Comment:
    {text}
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text.strip()

def run_pipeline():

    posts = []

    query = "Emirates NBD OR ENBD"

    for submission in reddit.subreddit("all").search(
        query,
        sort="new",
        time_filter="month",
        limit=50
    ):

        # combine title and body for better sentiment context
        text = f"{submission.title} {submission.selftext}"

        if len(text.strip()) > 5:
            posts.append(text)

    cleaned = clean_text_list(posts)

    sentiments = []

    for c in cleaned:

        try:
            s = classify_sentiment(c[:1000])   # avoid extremely long inputs
        except:
            s = "Neutral"

        sentiments.append(s)

    df = pd.DataFrame({
        "comment": cleaned,
        "sentiment": sentiments
    })

    df.to_csv("sentiment.csv", index=False)

    print("CSV updated")

if __name__ == "__main__":
    run_pipeline()