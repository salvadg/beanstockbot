import tweepy
import os
from dotenv import load_dotenv

# Load environment variables


class Beanbot:
    def __init__(self):
        load_dotenv()
        self.consumer_key = os.getenv("API_KEY")
        self.consumer_secret = os.getenv("API_KEY_SECRET")
        self.key = os.getenv("ACCESS_TOKEN")
        self.secret = os.getenv("ACCESS_TOKEN_SECRET")
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.key, self.secret)
        self.api = tweepy.API(self.auth)

    def send_tweet(self, message):
        self.api.update_status(message)

    # def delete_all_tweets(self):
    #     # Delete all tweets
    #     for status in tweepy.Cursor(api.user_timeline).items():
    #         api.destroy_status(status.id)
