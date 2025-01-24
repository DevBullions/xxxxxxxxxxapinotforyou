import streamlit as st
import tweepy
from pytrends.request import TrendReq
import openai
import textwrap
import time

# Authenticate with X API
def authenticate_twitter(api_key, api_secret, access_token, access_secret):
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)
    return tweepy.API(auth)

# Get Trending Topics for Multiple Niches
def get_trending_topics(niches):
    pytrends = TrendReq()
    trending_topics = {}
    for niche in niches:
        pytrends.build_payload([niche], timeframe="now 1-d")
        related_topics = pytrends.related_topics()
        trends = []
        for search in related_topics.values():
            if search and "top" in search:
                trends += list(search["top"]["query"])
        trending_topics[niche] = trends[:5]  # Top 5 trends per niche
    return trending_topics

# Generate AI Content
def generate_content(trending_topic, call_to_action):
    openai.api_key = "YOUR_OPENAI_API_KEY"
    prompt = f"""
    Write a detailed Twitter thread about '{trending_topic}'. 
    Make it engaging and insightful. 
    End the thread with this call-to-action: {call_to_action}.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700
    )
    return response["choices"][0]["message"]["content"].strip()

# Split Content into Tweets
def split_into_tweets(content, char_limit=280):
    """
    Splits content into chunks that fit within the character limit.
    """
    return textwrap.wrap(content, width=char_limit)

# Main Streamlit App
def main():
    st.title("AI-Generated Twitter Threads")
    
    # Input fields for API keys (optional for advanced users)
    api_key = st.text_input("Enter your Twitter API Key")
    api_secret = st.text_input("Enter your Twitter API Secret", type="password")
    access_token = st.text_input("Enter your Access Token")
    access_secret = st.text_input("Enter your Access Token Secret", type="password")
    
    # Define niches
    niches = [
        "Web3", "AI", "Crypto", "Blockchain Development", "NFTs", 
        "Decentralized Finance (DeFi)", "Smart Contracts", "Metaverse", 
        "Tech Startups", "Machine Learning", "Artificial Intelligence Ethics", 
        "Tech News", "FinTech", "Web Development", "Digital Marketing", 
        "Crypto Trading", "Data Science", "Cloud Computing", "IoT (Internet of Things)", 
        "Cybersecurity", "Game Development", "Tech Entrepreneurship", "Sustainable Tech"
    ]
    
    selected_niches = st.multiselect("Select Niches", niches, default=niches)
    call_to_action = st.text_input("Enter Call to Action", "Follow me for insights into Web3, AI, and Crypto trends!")
    
    # Get Trending Topics
    if st.button("Get Trending Topics"):
        if api_key and api_secret and access_token and access_secret:
            api = authenticate_twitter(api_key, api_secret, access_token, access_secret)
            trending_topics = get_trending_topics(selected_niches)
            st.write("Trending Topics:", trending_topics)
        else:
            st.error("Please provide all the required API keys.")
    
    # Generate Content
    if st.button("Generate Content"):
        trending_topic = st.selectbox("Select a Trending Topic", sum(list(get_trending_topics(selected_niches).values()), []))
        if trending_topic:
            content = generate_content(trending_topic, call_to_action)
            st.text_area("Generated Content", content, height=200)
    
    # Split Content into Tweets
    if st.button("Split Content into Tweets"):
        content_to_split = st.text_area("Enter Content to Split", height=100)
        if content_to_split:
            tweet_list = split_into_tweets(content_to_split)
            st.write("Tweets:", tweet_list)
    
    # Post to Multiple Communities (for simplicity, show a button that simulates posting)
    if st.button("Post to Communities"):
        tweet_list = st.text_area("Enter the Tweets to Post", height=200)
        community_ids = st.text_input("1506802380897202178, 1516848246395752455, 1691063817848123609, 1694710912400408717, 1500219593847103489, 1848846131360653722, 1494607507213459480, 1847770491798638869").split(",")
        if tweet_list and community_ids:
            api = authenticate_twitter(api_key, api_secret, access_token, access_secret)
            post_to_communities(api, tweet_list.splitlines(), community_ids)
            st.success("Posted to communities successfully!")
        else:
            st.error("Please enter the tweet content and community IDs.")

# Post Thread to Multiple Communities
def post_to_communities(api, tweet_list, community_ids):
    """
    Posts a list of tweets as a thread to multiple communities.
    """
    for community_id in community_ids:
        thread_id = None
        for tweet in tweet_list:
            if thread_id is None:
                # First tweet in the thread
                tweet_status = api.update_status(tweet, place_id=community_id)
            else:
                # Subsequent tweets in the thread
                tweet_status = api.update_status(tweet, in_reply_to_status_id=thread_id)
            thread_id = tweet_status.id
            print(f"Posted in Community {community_id}: {tweet}")
            time.sleep(2)  # Avoid rate limits

if __name__ == "__main__":
    main()
