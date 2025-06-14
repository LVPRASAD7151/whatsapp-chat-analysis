import re
import pandas as pd

def preprocess(data):
    # Multiple patterns to handle different WhatsApp export formats
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',  # DD/MM/YYYY, HH:MM - 
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[AP]M\s-\s',  # DD/MM/YYYY, HH:MM AM/PM - 
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]',  # [DD/MM/YYYY, HH:MM:SS AM/PM]
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s-\s'  # DD/MM/YYYY, HH:MM:SS - 
    ]
    
    messages = []
    dates = []
    
    # Try each pattern
    for pattern in patterns:
        messages = re.split(pattern, data)[1:]
        dates = re.findall(pattern, data)
        if messages and dates:
            break
    
    # If no pattern matches, return empty dataframe
    if not messages or not dates:
        return pd.DataFrame(columns=['user', 'message', 'date', 'only_date', 'year', 'month_num', 'month', 'day', 'day_name', 'hour', 'minute', 'period'])
    
    # Create initial dataframe
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Clean message_date by removing brackets and extra characters
    df['message_date'] = df['message_date'].str.replace('[', '').str.replace(']', '').str.strip()
    
    # Try different date formats
    date_formats = [
        '%d/%m/%Y, %H:%M - ',
        '%d/%m/%Y, %H:%M %p - ',
        '%d/%m/%Y, %H:%M:%S - ',
        '%d/%m/%Y, %H:%M:%S %p',
        '%m/%d/%Y, %H:%M - ',
        '%m/%d/%Y, %H:%M %p - '
    ]
    
    for fmt in date_formats:
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format=fmt)
            break
        except:
            continue
    
    # If date parsing fails, try without format
    if df['message_date'].dtype == 'object':
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], infer_datetime_format=True)
        except:
            # If all fails, create dummy dates
            df['message_date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='H')
    
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    
    for message in df['user_message']:
        # Improved regex to handle different name formats
        entry = re.split(r'(.*?):\s', message, maxsplit=1)
        if len(entry) >= 3 and entry[1].strip():  # user name exists
            users.append(entry[1].strip())
            messages.append(entry[2] if len(entry) > 2 else "")
        else:
            users.append('group_notification')
            messages.append(message.strip())

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add date-time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time periods
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + "00")
        elif hour == 0:
            period.append("00" + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df