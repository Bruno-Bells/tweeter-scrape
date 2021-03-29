import sys  
#sys.path.insert(0, '/Users/dr_d3mz/Documents/GitHub/Bloverse_Data_Science/Twitter Marketing/Functions') # insert the path to your functions folder

import os
import twint
import nest_asyncio
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from urllib.parse import urlparse
from newspaper import Article
import numpy as np
nest_asyncio.apply()

import image_utils as img_utils

def twint_to_pandas(columns):
    return twint.output.panda.Tweets_df[columns]

def get_latest_tweets_from_handle(username, num_tweets, date):

    c = twint.Config()
    c.Username = username
    c.Limit = num_tweets
    c.Pandas = True
    c.Since = date
    c.Hide_output = True

    twint.run.Search(c)
    
    try:
        tweet_df = twint_to_pandas(['id', 'conversation_id', 'date', 'tweet', 'language', 'hashtags', 
               'username', 'name', 'link', 'urls', 'photos', 'video',
               'thumbnail', 'retweet', 'nlikes', 'nreplies', 'nretweets', 'source'])
    except Exception as e:
        print(e)
        tweet_df = pd.DataFrame()
        
#     print(tweet_df.head())
#     print()
        
    return tweet_df


def get_tweets_for_date(tweet_df, date):
    """
    This function takes a date and returns all the tweets from that date
    """
#     print(len(tweet_df))
    date_tweet_inds = []
    for i in range(len(tweet_df)):
        tweet_date = tweet_df['date'].iloc[i][0:10]
        if tweet_date == date:
            date_tweet_inds.append(i)
    
    date_tweet_df = tweet_df.iloc[date_tweet_inds]
    
    return date_tweet_df


def publisher_handle_analytics(username, num_tweets, last_week_date):
    """
    Step 1 - Given a username, get the tweets that have been generated in the last 8 days
    Step 2 - Loop through the extracted tweets and run analytics on them
    - Calculate the percentage of tweets that had two comments or more
    - Calculate the average number of daily tweets
    - Calculate the average number of daily article tweets
    - Calculate the average number of comments
    """
    ## Get the tweets over the last week for that publications
    latest_tweet_df = get_latest_tweets_from_handle(username, num_tweets, last_week_date)
    
    ## Now loop through each data from yesterday to 8 days ago down to yesterday
    total_tweets_list = []
    num_article_tweets_list = []
    num_tweets_w_comments_list = []
    day_tweet_comment_perc_list = []
    day_tweet_comment_list = []
    
    for i in range(7):
        ind = i+1
        day = datetime.now() - timedelta(ind)
        day_date = datetime.strftime(day, '%Y-%m-%d')
        date_tweet_df = get_tweets_for_date(latest_tweet_df, day_date) 
        num_tweets = len(date_tweet_df)
        total_tweets_list.append(num_tweets)

        # Loop through all the tweets and identify the ones that have links
        tweet_w_link_indices = []
        link_tweet_w_comment_indices = []
        for ii in range(len(date_tweet_df)):
            tweet_text = date_tweet_df.iloc[ii]['tweet']
            tweet_urls = date_tweet_df.iloc[ii]['urls']
            num_tweet_comments = date_tweet_df.iloc[ii]['nreplies']
            if len(tweet_urls) > 0:
                tweet_w_link_indices.append(ii)
                if num_tweet_comments > 1:
                    link_tweet_w_comment_indices.append(ii)

        link_tweets = date_tweet_df.iloc[tweet_w_link_indices]
        comment_tweets = date_tweet_df.iloc[link_tweet_w_comment_indices]
        num_comment_tweets = len(comment_tweets)
        num_tweets_w_comments_list.append(num_comment_tweets)
        comments_list = list(comment_tweets['nreplies'])
        num_article_tweets_list.append(len(link_tweets))
        try:
            comment_perc = int(round(num_comment_tweets/num_tweets,2) * 100)
        except:
            comment_perc = 0
        day_tweet_comment_perc_list.append(comment_perc)
        day_tweet_comment_list.append(sum(comments_list))


    avg_daily_tweets = int(np.average(total_tweets_list))
    avg_daily_articles = int(np.average(num_article_tweets_list))
    avg_daily_comments = int(np.average(day_tweet_comment_list))
    perc_comment_tweets = int((sum(num_tweets_w_comments_list)/sum(total_tweets_list))*100)
    
    return avg_daily_tweets, avg_daily_articles, avg_daily_comments, perc_comment_tweets


def get_twitter_handle_bio_details(twitter_handle):
    try:
        c = twint.Config()
        c.Username = twitter_handle
        c.Store_object = True
        c.User_full = False
        c.Pandas =True
        c.Hide_output = True

        twint.run.Lookup(c)
        user_df = twint.storage.panda.User_df.drop_duplicates(subset=['id'])

        try:
            user_id = list(user_df['id'])[0]
        except:
            user_id = 'NA'

        try:
            user_name = list(user_df['name'])[0]
        except:
            user_name = 'NA'

        try:
            user_bio = list(user_df['bio'])[0]
        except:
            user_bio = 'NA'

        try:
            user_profile_image_url = list(user_df['avatar'])[0]
        except:
            user_profile_image_url = 'NA'

        try:
            user_url = list(user_df['url'])[0]
        except:
            user_url = 'NA'

        try:
            user_join_date = list(user_df['join_date'])[0]
        except:
            user_join_date = 'NA'

        try:
            user_location = list(user_df['location'])[0]
        except:
            user_location = 'NA'

        try:
            user_following = list(user_df['following'])[0]
        except:
            user_following = 'NA'

        try:
            user_followers = list(user_df['followers'])[0]
        except:
            user_followers = 'NA'

        try:
            user_verified = list(user_df['verified'])[0]
        except:
            user_verified = 'NA'

    except:
        user_name = 'NA'
        user_bio = 'NA'
        user_profile_image_url = 'NA'
        user_url = 'NA'
        user_join_date = 'NA'
        user_location = 'NA'
        user_following = 'NA'
        user_followers = 'NA'
        user_verified = 'NA'
    
    return user_name, user_bio, user_profile_image_url, user_url, user_location, user_following, user_followers, user_verified
