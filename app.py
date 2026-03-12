import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pytz
import os

st.title("Emirates NBD Reddit Sentiment Dashboard")

file_time = os.path.getmtime("sentiment.csv")

dubai = pytz.timezone("Asia/Dubai")
last_update = datetime.fromtimestamp(file_time, dubai)

st.write("Last data update:", last_update.strftime("%Y-%m-%d %H:%M:%S"))

st_autorefresh(interval=300000)

df = pd.read_csv("sentiment.csv")

positive = df[df["sentiment"]=="Positive"]
neutral = df[df["sentiment"]=="Neutral"]
negative = df[df["sentiment"]=="Negative"]

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Positive")
    for c in positive["comment"]:
        st.success(c)

with col2:
    st.subheader("Neutral")
    for c in neutral["comment"]:
        st.warning(c)

with col3:
    st.subheader("Negative")
    for c in negative["comment"]:
        st.error(c)