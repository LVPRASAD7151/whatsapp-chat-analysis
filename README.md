# whatsapp-chat-analysis
I worked on is a WhatsApp Chat Analyzer, which I built using Python and Streamlit. The idea behind the project was to take exported .txt chat files from WhatsApp and transform them into interactive visual insights using a clean web-based dashboard.
My Approach:
I divided the project into three core components:

Preprocessing raw data – using regular expressions to extract dates, users, and messages accurately from the unstructured chat logs.

Data Analysis & Feature Engineering – I created new time-based features like day, month, hour, and message periods to enable timeline and heatmap visualizations.

Frontend Dashboard – I used Streamlit to make the interface interactive, where users can upload files, choose specific participants, and view message/activity statistics dynamically.


Tech Stack Used:
Streamlit for frontend/UI

Pandas for data handling

Matplotlib and Seaborn for visualizations

WordCloud for common word visualization

URLExtract and Emoji libraries for link and emoji analysis



One of the projects I’m particularly proud of is a full-fledged WhatsApp Chat Analyzer that I developed using Python and Streamlit. The goal was to transform raw, unstructured WhatsApp chat exports into clean, insightful, and interactive visual analytics — almost like a personal communication dashboard.

To begin with, I built a preprocessing pipeline using regular expressions to parse chat timestamps, usernames, and messages. Since the data format can vary and often contains system messages or media placeholders like <Media omitted>, I implemented logic to handle those edge cases. After structuring the data into a DataFrame using pandas, I engineered several time-based features like daily and monthly message counts, day names, hours, and even specific time periods (like 10–11 AM), which later helped in detailed heatmap visualizations.

Once the data was ready, I designed an interactive Streamlit dashboard. Users can upload their .txt chat file, select either an individual or the whole group, and instantly view a range of analytics:

Basic stats like number of messages, total words, media shared, and links

Timeline charts showing chat activity trends over days and months

Activity maps and heatmaps that visually capture when users are most active

WordClouds and bar charts for the most common words, after filtering out stop words using a Hinglish stopword list

Emoji usage breakdown and top contributors in group chats

On the backend, I used:

pandas for data manipulation,

matplotlib and seaborn for plotting,

wordcloud for visual word frequency,

and urlextract and emoji libraries for parsing links and emojis.

What sets this project apart is that it mimics real-world product behavior. It’s not just analysis for analysis’ sake — it delivers a clean user experience, smart data filtering, and handles many edge cases gracefully. I kept the code modular by separating logic into a helper.py and preprocessor.py, making it easy to scale and maintain.

This project taught me a lot about working with unstructured data, building clean UIs with Streamlit, and designing solutions that are both functional and user-friendly. If given the opportunity to extend it further, I’d love to add sentiment analysis, chatbot behavior analysis, or even deploy it with user authentication to allow secure multi-user access

