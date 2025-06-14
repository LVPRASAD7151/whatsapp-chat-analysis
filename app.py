import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set page config
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #25D366;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #25D366;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #c62828;
    }
    .info-message {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">📱 WhatsApp Chat Analyzer</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔧 Configuration")
st.sidebar.markdown("---")

# File upload instructions
st.sidebar.markdown("""
### 📋 How to export WhatsApp chat:
1. Open WhatsApp chat
2. Tap on chat name
3. Select "Export Chat"
4. Choose "Without Media"
5. Upload the .txt file here
""")

uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file", type=['txt'])

if uploaded_file is not None:
    try:
        # Read and decode file
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        
        # Show loading spinner
        with st.spinner('Processing chat data...'):
            df = preprocessor.preprocess(data)
        
        # Check if data was processed successfully
        if df.empty:
            st.markdown('<div class="error-message">❌ <strong>Error:</strong> Could not process the chat file. Please make sure you uploaded a valid WhatsApp chat export file.</div>', unsafe_allow_html=True)
            st.stop()
        
        # Show success message
        st.markdown(f'<div class="info-message">✅ <strong>Success:</strong> Processed {len(df)} messages from the chat!</div>', unsafe_allow_html=True)
        
        # Get unique users
        user_list = df['user'].unique().tolist()
        
        # Remove group notifications if present
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        
        # Filter out empty or invalid users
        user_list = [user for user in user_list if user and str(user).strip() and str(user) != 'nan']
        
        if not user_list:
            st.markdown('<div class="error-message">❌ <strong>Error:</strong> No valid users found in the chat data.</div>', unsafe_allow_html=True)
            st.stop()
        
        user_list.sort()
        user_list.insert(0, "Overall")

        # User selection
        selected_user = st.sidebar.selectbox("👤 Show analysis for:", user_list)
        
        # Add analyze button
        analyze_button = st.sidebar.button("🚀 Start Analysis", type="primary")
        
        # Show basic info
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Quick Stats")
        st.sidebar.write(f"**Total Messages:** {len(df)}")
        st.sidebar.write(f"**Participants:** {len(user_list)-1}")
        st.sidebar.write(f"**Date Range:** {df['only_date'].min()} to {df['only_date'].max()}")

        if analyze_button:
            # Fetch statistics
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            
            # Display top statistics
            st.markdown("## 📈 Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Messages", num_messages, delta=None)
            with col2:
                st.metric("Total Words", words, delta=None)
            with col3:
                st.metric("Media Shared", num_media_messages, delta=None)
            with col4:
                st.metric("Links Shared", num_links, delta=None)

            # Only show detailed analysis if there's data
            if num_messages > 0:
                
                # Timeline Analysis
                st.markdown("## 📅 Timeline Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Monthly Timeline")
                    timeline = helper.monthly_timeline(selected_user, df)
                    if not timeline.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(timeline['time'], timeline['message'], color='#25D366', linewidth=2, marker='o')
                        ax.set_xlabel('Time')
                        ax.set_ylabel('Number of Messages')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("📊 No data available for monthly timeline")

                with col2:
                    st.markdown("### Daily Timeline")
                    daily_timeline = helper.daily_timeline(selected_user, df)
                    if not daily_timeline.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#075E54', linewidth=1)
                        ax.set_xlabel('Date')
                        ax.set_ylabel('Number of Messages')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("📊 No data available for daily timeline")

                # Activity Map
                st.markdown("## 🗺️ Activity Map")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Most Busy Day")
                    busy_day = helper.week_activity_map(selected_user, df)
                    if not busy_day.empty:
                        fig, ax = plt.subplots(figsize=(8, 6))
                        bars = ax.bar(busy_day.index, busy_day.values, color='#25D366')
                        ax.set_xlabel('Day of Week')
                        ax.set_ylabel('Number of Messages')
                        plt.xticks(rotation=45)
                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{int(height)}', ha='center', va='bottom')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("📊 No data available")

                with col2:
                    st.markdown("### Most Busy Month")
                    busy_month = helper.month_activity_map(selected_user, df)
                    if not busy_month.empty:
                        fig, ax = plt.subplots(figsize=(8, 6))
                        bars = ax.bar(busy_month.index, busy_month.values, color='#FF6B35')
                        ax.set_xlabel('Month')
                        ax.set_ylabel('Number of Messages')
                        plt.xticks(rotation=45)
                        # Add value labels on bars
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{int(height)}', ha='center', va='bottom')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("📊 No data available")

                # Weekly Activity Heatmap
                st.markdown("### 🔥 Weekly Activity Heatmap")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                if not user_heatmap.empty and user_heatmap.size > 0:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    sns.heatmap(user_heatmap, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
                    ax.set_xlabel('Time Period')
                    ax.set_ylabel('Day of Week')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("📊 No data available for heatmap")

                # Most Busy Users (only for Overall analysis)
                if selected_user == 'Overall':
                    st.markdown("## 👥 Most Busy Users")
                    x, new_df = helper.most_busy_users(df)
                    if not x.empty:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            bars = ax.bar(range(len(x)), x.values, color='#E74C3C')
                            ax.set_xticks(range(len(x)))
                            ax.set_xticklabels(x.index, rotation=45, ha='right')
                            ax.set_xlabel('Users')
                            ax.set_ylabel('Number of Messages')
                            # Add value labels on bars
                            for i, bar in enumerate(bars):
                                height = bar.get_height()
                                ax.text(bar.get_x() + bar.get_width()/2., height,
                                       f'{int(height)}', ha='center', va='bottom')
                            plt.tight_layout()
                            st.pyplot(fig)
                        
                        with col2:
                            st.markdown("#### Percentage Breakdown")
                            st.dataframe(new_df, use_container_width=True)

                # Word Analysis
                st.markdown("## 💬 Word Analysis")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🔤 Most Common Words")
                    most_common_df = helper.most_common_words(selected_user, df)
                    if not most_common_df.empty:
                        fig, ax = plt.subplots(figsize=(8, 10))
                        ax.barh(most_common_df[0].head(15), most_common_df[1].head(15), color='#3498DB')
                        ax.set_xlabel('Frequency')
                        ax.set_ylabel('Words')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("📊 No common words data available")

                with col2:
                    st.markdown("### ☁️ Word Cloud")
                    df_wc = helper.create_wordcloud(selected_user, df)
                    if df_wc is not None:
                        fig, ax = plt.subplots(figsize=(8, 8))
                        ax.imshow(df_wc, interpolation='bilinear')
                        ax.axis('off')
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("☁️ No word cloud data available")

                # Emoji Analysis
                st.markdown("## 😊 Emoji Analysis")
                emoji_df = helper.emoji_helper(selected_user, df)
                if not emoji_df.empty:
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown("### 📊 Emoji Usage")
                        st.dataframe(emoji_df.head(10), use_container_width=True)

                    with col2:
                        st.markdown("### 🥧 Top Emojis Distribution")
                        if len(emoji_df) > 0:
                            fig, ax = plt.subplots(figsize=(8, 8))
                            top_emojis = emoji_df.head(5)
                            colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                            wedges, texts, autotexts = ax.pie(
                                top_emojis[1], 
                                labels=top_emojis[0], 
                                autopct='%1.1f%%',
                                colors=colors,
                                startangle=90,
                                textprops={'fontsize': 12}
                            )
                            plt.tight_layout()
                            st.pyplot(fig)
                else:
                    st.info("😊 No emoji data available")
                    
            else:
                st.markdown('<div class="error-message">❌ <strong>No Data:</strong> The selected user has no messages to analyze.</div>', unsafe_allow_html=True)

    except UnicodeDecodeError:
        st.markdown('<div class="error-message">❌ <strong>Error:</strong> Could not decode the file. Please make sure it\'s a valid text file with UTF-8 encoding.</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<div class="error-message">❌ <strong>Error:</strong> An unexpected error occurred: {str(e)}</div>', unsafe_allow_html=True)
        st.error("Please check your file format and try again.")

else:
    # Welcome message when no file is uploaded
    st.markdown("""
    ## Welcome to WhatsApp Chat Analyzer! 👋
    
    This tool helps you analyze your WhatsApp chat data and discover interesting insights about your conversations.
    
    ### 🌟 Features:
    - 📊 **Message Statistics** - Total messages, words, media, and links
    - 📅 **Timeline Analysis** - Monthly and daily activity patterns  
    - 🗺️ **Activity Maps** - Busiest days and months
    - 🔥 **Heatmaps** - Hour-wise activity throughout the week
    - 👥 **User Analysis** - Most active participants
    - 💬 **Word Analysis** - Most common words and word clouds
    - 😊 **Emoji Analysis** - Most used emojis and distributions
    
    ### 🚀 Get Started:
    1. Export your WhatsApp chat (without media)
    2. Upload the .txt file using the sidebar
    3. Select a user or choose "Overall" for group analysis
    4. Click "Start Analysis" to begin!
    
    ---
    *Made with ❤️ using Streamlit*
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>WhatsApp Chat Analyzer | Built with Streamlit 🚀</p>
    </div>
    """, 
    unsafe_allow_html=True
)