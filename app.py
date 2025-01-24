import streamlit as st
import tweepy
from pytrends.request import TrendReq
import openai
import textwrap
import time
from PIL import Image
import requests
from io import BytesIO

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
    openai.api_key = "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"
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

# Generate Image using OpenAI's DALL·E
def generate_image(prompt):
    try:
        openai.api_key = "YOUR_OPENAI_API_KEY"
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        return image, None  # Image generated successfully
    except Exception as e:
        return None, f"Error generating image: {str(e)}"  # Error in image generation

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
    api_key = st.text_input("SH8ZUiEpdWYw2A7z4w0VUwNXS")
    api_secret = st.text_input("URfbkpLABf8bp4OcCZa0nCHCvD8AxG4Z4lKEPaXzbNJav2W0Dr", type="password")
    access_token = st.text_input("1498625403451318276-brPJCjfiTXwdeIkANDESNY5GSCWhkt")
    access_secret = st.text_input("3Y17XAHO3EbUoxy1YQrFmTEtwuSiDFI6ZEcw5X14FZyF1", type="password")
    
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
    
    # Generate Content and Image
    if st.button("Generate Content & Image"):
        trending_topic = st.selectbox("Select a Trending Topic", sum(list(get_trending_topics(selected_niches).values()), []))
        if trending_topic:
            content = generate_content(trending_topic, call_to_action)
            st.text_area("Generated Content", content, height=200)
            
            # Generate Image for the Tweet
            image_prompt = f"Generate an image related to {trending_topic}"
            generated_image, image_error = generate_image(image_prompt)
            
            if generated_image:
                st.image(generated_image, caption="Generated Image for Tweet", use_column_width=True)
            elif image_error:
                st.warning(image_error)  # Show image generation error but continue
    
    # Split Content into Tweets and Post to Communities
    if st.button("Post to Communities"):
        tweet_list = split_into_tweets(content)
        community_ids = st.text_input("1506802380897202178, 1516848246395752455, 1691063817848123609, 1694710912400408717, 1500219593847103489, 1848846131360653722, 1494607507213459480, 1847770491798638869").split(",")
        if tweet_list and community_ids:
            api = authenticate_twitter(api_key, api_secret, access_token, access_secret)
            post_results = post_to_communities(api, tweet_list, community_ids)
            
            if post_results:
                st.success("Posted to communities successfully!")
            else:
                st.error("Some communities could not be posted to. Please check.")
        else:
            st.error("Please enter the tweet content and community IDs.")

# Post Thread to Multiple Communities
def post_to_communities(api, tweet_list, community_ids):
    """
    Posts a list of tweets as a thread to multiple communities.
    Returns a list of successfully posted community IDs.
    """
    successful_posts = []
    for community_id in community_ids:
        thread_id = None
        try:
            for tweet in tweet_list:
                if thread_id is None:
                    # First tweet in the thread
                    tweet_status = api.update_status(tweet, place_id=community_id)
                else:
                    # Subsequent tweets in the thread
                    tweet_status = api.update_status(tweet, in_reply_to_status_id=thread_id)
                thread_id = tweet_status.id
                print(f"Posted in Community {community_id}: {tweet}")
                successful_posts.append(community_id)
                time.sleep(2)  # Avoid rate limits
        except tweepy.TweepError as e:
            print(f"Failed to post to Community {community_id}: {str(e)}")
            continue  # Skip this community and continue with the others

    return successful_posts  # Returns communities that were successfully posted to

if __name__ == "__main__":
    main()
