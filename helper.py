from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import os

extract = URLExtract()

# Default stop words if file doesn't exist
DEFAULT_STOP_WORDS = """
i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with through during before after above below up down out off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now d ll m o re ve y ain aren couldn didn doesn hadn isn mightn mustn needn shan shouldn wasn weren won wouldn
"""

def get_stop_words():
    """Get stop words from file or use default"""
    try:
        if os.path.exists('stop_hinglish.txt'):
            with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = f.read().lower()
        else:
            stop_words = DEFAULT_STOP_WORDS.lower()
        return set(stop_words.split())
    except:
        return set(DEFAULT_STOP_WORDS.lower().split())

def fetch_stats(selected_user, df):
    if df.empty:
        return 0, 0, 0, 0
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        if pd.notna(message):
            words.extend(str(message).split())

    # fetch number of media messages
    num_media_messages = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        if pd.notna(message):
            links.extend(extract.find_urls(str(message)))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    if df.empty:
        return pd.Series(), pd.DataFrame()
    
    x = df['user'].value_counts().head()
    user_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    user_df.columns = ['name', 'percent']
    return x, user_df

def create_wordcloud(selected_user, df):
    if df.empty:
        return None
    
    stop_words = get_stop_words()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]
    
    if temp.empty:
        return None

    def remove_stop_words(message):
        if pd.isna(message):
            return ""
        y = []
        for word in str(message).lower().split():
            if word not in stop_words and len(word) > 2:
                y.append(word)
        return " ".join(y)

    temp_copy = temp.copy()
    temp_copy['message'] = temp_copy['message'].apply(remove_stop_words)
    
    # Combine all messages
    text = temp_copy['message'].str.cat(sep=" ")
    
    if not text.strip():
        return None
    
    try:
        wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        df_wc = wc.generate(text)
        return df_wc
    except:
        return None

def most_common_words(selected_user, df):
    if df.empty:
        return pd.DataFrame()
    
    stop_words = get_stop_words()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]
    
    if temp.empty:
        return pd.DataFrame()

    words = []
    for message in temp['message']:
        if pd.notna(message):
            for word in str(message).lower().split():
                if word not in stop_words and len(word) > 2:
                    words.append(word)

    if not words:
        return pd.DataFrame()
    
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if df.empty:
        return pd.DataFrame()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        if pd.notna(message):
            # Updated emoji detection for newer emoji library versions
            try:
                emojis.extend([c for c in str(message) if c in emoji.EMOJI_DATA])
            except:
                # Fallback for older versions
                try:
                    emojis.extend([c for c in str(message) if c in emoji.UNICODE_EMOJI['en']])
                except:
                    # Simple emoji detection as fallback
                    import re
                    emoji_pattern = re.compile("["
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags=re.UNICODE)
                    emojis.extend(emoji_pattern.findall(str(message)))

    if not emojis:
        return pd.DataFrame()
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):
    if df.empty:
        return pd.DataFrame()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if df.empty:
        return pd.DataFrame()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if df.empty:
        return pd.Series()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.Series()
    
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if df.empty:
        return pd.Series()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.Series()
    
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if df.empty:
        return pd.DataFrame()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()
    
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap