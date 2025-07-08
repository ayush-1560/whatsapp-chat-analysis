# --- app.py ---

import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="centered")
st.sidebar.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("📂 Upload a chat file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("🔍 Analyze chat for", user_list)

    if st.sidebar.button("🚀 Show Analysis"):
        # --- Top Statistics ---
        st.markdown("## 🧮 Top Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Total Messages**")
            st.markdown(f"<h4 style='margin-top:0'>{num_messages}</h4>", unsafe_allow_html=True)
        with col2:
            st.markdown("**Total Words**")
            st.markdown(f"<h4 style='margin-top:0'>{words}</h4>", unsafe_allow_html=True)
        with col3:
            st.markdown("**Media Shared**")
            st.markdown(f"<h4 style='margin-top:0'>{num_media_messages}</h4>", unsafe_allow_html=True)
        with col4:
            st.markdown("**Links Shared**")
            st.markdown(f"<h4 style='margin-top:0'>{num_links}</h4>", unsafe_allow_html=True)

        st.markdown("---")

        # --- Monthly Timeline ---
        st.subheader("📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # --- Daily Timeline ---
        st.subheader("📆 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        # Conversation Highlights - Top 5 Busiest Days
        st.title("🔥 Conversation Highlights")

        top_days = daily_timeline.sort_values(by='message', ascending=False).head(5)

        for idx, row in top_days.iterrows():
            st.markdown(f"**📅 {row['only_date'].strftime('%B %d, %Y')}** — 💬 {row['message']} messages")
        # --- Activity Map ---
        st.subheader("📊 Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Most Busy Day**")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.markdown("**Most Busy Month**")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.subheader("📍 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty:
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.warning("No activity data available to display heatmap.")

        # --- Most Busy Users (only for overall) ---
        if selected_user == 'Overall':
            st.subheader("👥 Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # --- Wordcloud ---
        st.subheader("☁️ Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # --- Most Common Words ---
        st.subheader("🔠 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='teal')
        plt.xticks(rotation='horizontal')
        st.pyplot(fig)

        # --- Emoji Analysis ---
        st.subheader("😊 Emoji Analysis")
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

            if len(sizes) > 0:
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct="%0.2f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
