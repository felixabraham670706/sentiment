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
Classify the sentiment of the following comment about a bank.

Return ONLY one word:
Positive
Neutral
Negative

Examples:
"I love ENBD customer service" -> Positive
"ENBD blocked my account" -> Negative
"I opened an ENBD account today" -> Neutral

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
    query = "Emirates NBD OR ENBD OR Liv Bank"
    for submission in reddit.subreddit("all").search(
        query,
        sort="new",
        time_filter="month",
        limit=20
    ):

        submission.comments.replace_more(limit=0)

        for comment in submission.comments.list():
            posts.append(comment.body)

    cleaned = clean_text_list(posts)

    sentiments = []

    for c in cleaned:
        print("Classifying:", c[:30])

        try:
            s = classify_sentiment(c)
        except Exception as e:
            print("Classification error:", e)
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