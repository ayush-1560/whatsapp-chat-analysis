# --- app.py ---

import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.markdown("## Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)
        with col4:
            st.metric("Links Shared", num_links)

        # monthly timeline
        st.markdown("## Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.markdown("## Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.markdown("## Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.markdown("#### Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.markdown("#### Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        if not user_heatmap.empty:
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.warning("No activity data available to display heatmap.")

        # busiest users
        if selected_user == 'Overall':
            st.markdown("## Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.markdown("## Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # most common words
        st.markdown("## Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # emoji analysis
        st.markdown("## Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        if emoji_df.empty:
            st.warning("No emojis found in this chat.")
        else:
            st.dataframe(emoji_df)
            col_names = emoji_df.columns.tolist()

            if 'emoji' in col_names and 'count' in col_names:
                labels = emoji_df['emoji'].head()
                sizes = emoji_df['count'].head()
            elif 0 in col_names and 1 in col_names:
                labels = emoji_df[0].head()
                sizes = emoji_df[1].head()
            else:
                st.warning("Unexpected emoji DataFrame structure.")
                labels, sizes = [], []

            if len(sizes) != 0:
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct="%0.2f")
                st.pyplot(fig)

        # Sentiment Analysis
        st.markdown("## Sentiment Analysis")
        sentiment_df = helper.sentiment_analysis(selected_user, df)
        st.dataframe(sentiment_df)
        st.bar_chart(sentiment_df['sentiment'].value_counts())
