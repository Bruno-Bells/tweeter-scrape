#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys  
import os, re
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
import twitter_marketing_funcs as twt_mark


# In[2]:


"""
Build functionality that gets the tweets
- Actually for the RSS, only use content where the videos have been generated on Bloverse. This would potentially make life easier for us
- So what would happen is that we only generate the comment videos for articles that have already been generated for RSS
"""


# In[3]:


"""
Step 1 - Get the date for today and 7 days ago
"""
time_diff = 1 # This means that we want to get tweets that were posted in the last hour. In production we will probably go for 3
today = datetime.now() 

date = today.date()
hour = max(0, today.hour - time_diff)
minute = '00'
second = '00'
today_date_str = '%s %s:%s:%s' % (date, hour, minute, second)
print(today_date_str)

num_tweets = 5000 # The maximum number of tweets that would be extracted in any given run


# In[4]:


import os
os.getcwd()


# In[5]:


rss_twitter_handles_path = 'C:\\Users\\USER\\Desktop\\NEW_DEMZ\\bloverse\\rss_publications_final.csv'
rss_publication_df = pd.read_csv(rss_twitter_handles_path)
print(rss_publication_df.head())


# In[6]:


## Get expected number of tweets daily
expected_daily_tweets = sum(list(rss_publication_df['Avg Daily Tweets']))
print(expected_daily_tweets)


# In[7]:


latest_tweet_df_list = []
for i in range(len(rss_publication_df)):
    rss_twitter_handle = rss_publication_df['Twitter Handle'].iloc[i]
    print(rss_twitter_handle)
    tweet_df = twt_mark.get_latest_tweets_from_handle(rss_twitter_handle, num_tweets, today_date_str)
    tweet_df['Twitter Handle'] = rss_twitter_handle
    print(len(tweet_df))
    latest_tweet_df_list.append(tweet_df)
    print()


# In[8]:


# latest_tweet_df_list


# In[9]:


latest_tweets_df = pd.concat(latest_tweet_df_list, sort=True)

tweet_w_link_indices = []
link_tweet_w_comment_indices = []
for ii in range(len(latest_tweets_df)):
    tweet_text = latest_tweets_df.iloc[ii]['tweet']
    tweet_urls = latest_tweets_df.iloc[ii]['urls']
    num_tweet_comments = latest_tweets_df.iloc[ii]['nreplies']
    if len(tweet_urls) > 0:
#         print(tweet_text)
#         print(tweet_urls)
#         print()
        tweet_w_link_indices.append(ii)
        if num_tweet_comments > 1:
            link_tweet_w_comment_indices.append(ii)

link_tweets_df = latest_tweets_df.iloc[tweet_w_link_indices]
comment_tweets_df = latest_tweets_df.iloc[link_tweet_w_comment_indices]
total_comments = sum(list(comment_tweets_df['nreplies']))


# In[ ]:





# In[10]:


"""
Save the link_tweets from the latest run to the db for the RSS generation
- Add code in here at this point to filter out any articles that have something missing and as such wont generate videos
"""


# In[11]:


"""
Build algorithm that allocates the tweet ids for where we want to go and get comments from, as well as how many comments we should expect to get
- For the latest extraction, for each handle
1 - get a df of their latest tweets
2 - rank the tweets by n_relies
3 - for the top 5 tweets by replies, store their 
"""
## Assign the target number of comments we want to extract
target_num_comments = 500 
# we should be running this every 3 hours from 6am UK to 6pm and build an algorithm that recommends the exactly the tweet ids for where
# Ukeme will be going to get comments from, as well as how many comments he is expected to be getting from each tweetid

## Now loop through each publication and calculate a weight 
publication_comment_tweet_ids = []
publication_names = []
publisher_num_comments_list = []
publication_handle_list = list(rss_publication_df['Twitter Handle'])
total_comments = sum(list(rss_publication_df['Avg Daily Comments']))

## To make it simple, for each handle, just get 5 comments from each run
## This also adds a bit of fairness to proceedings
for publication in publication_handle_list:
    comment_tweet_id_list = []
    publication_info = rss_publication_df[rss_publication_df['Twitter Handle']==publication]
    target_num_tweets = 5
    try:
        publication_df = comment_tweets_df[comment_tweets_df['Twitter Handle']==publication]
        publication_df = publication_df.sort_values(by=['nreplies'], ascending=False)
        comment_tweet_ids = list(publication_df.iloc[0:5]['id'])
        counter = 0
        for i in range(len(publication_df)):
            tweet_text = publication_df.iloc[i]['tweet']
            tweet_id = publication_df.iloc[i]['id']
            num_comments = publication_df.iloc[i]['nreplies']
            if num_comments > 5:
                comment_tweet_id_list.append(tweet_id)
                counter += 1
                if counter >= 5:
                    break
    except Exception as e:
#         print(e)
        pass
    if len(comment_tweet_id_list) > 0:
        publication_names.append(publication)
        publication_comment_tweet_ids.append(comment_tweet_id_list)
publication_tweet_comment_search_dict = dict(zip(publication_names, publication_comment_tweet_ids))


# In[12]:


print(publication_tweet_comment_search_dict)


# In[ ]:





# In[ ]:





# In[ ]:





# In[13]:


"""
Build a functionaly that will go search for the tweets with the publication ids(publication_tweet_comment_search_dict) 
For each id, get 3 comments, as well as store metrics like num_likes etc etc
"""


# In[57]:


# get dates for the tweets search (since today, until tomorrow)
# today = date.today()
# tomorrow = date.today() + timedelta(days=1)

# tomorrow = tomorrow.strftime('%Y-%m-%d')
# today = today.strftime('%Y-%m-%d')
# # print(tomorrow, today)

time_diff = 3 # This means that we want to get tweets that were posted in the last hour. In production we will probably go for 3
today = datetime.now() 
date = today.date()
since_hour = max(0, today.hour - time_diff)
until_hour = today.hour+1
minute = '00'
second = '00'
since_date_str = '%s %s:%s:%s' % (date, since_hour, minute, second)
until_date_str = '%s %s:%s:%s' % (date, until_hour, minute, second)
# print(since_date_str)
# print(until_date_str)


# In[58]:


def get_replies_from_tweet(handle, today):
    """
    This functionality get all tweets from a handle given a specific date
    """
    c = twint.Config()
    c.Since = today
#     c.Until = tomorrow
    c.Pandas = True
    c.To = handle #the handle of the twitter account
    c.Hide_output = True
    c.Limit = 2500
    c.Store_csv = True
    twint.run.Search(c)
    replies_df = twint.storage.panda.Tweets_df

    return replies_df


# In[ ]:





# In[59]:



def get_top_3_comments_of_tweet_df(replies_df, tweet_id):

    new_df = replies_df[replies_df['conversation_id']==tweet_id]
    new_df = new_df.sort_values(['nlikes'], ascending=[False]).head(3)
    #n_likes = new_df['nlikes']

    comments = new_df['tweet']
    nlikes = new_df['nlikes']
    _id = new_df['id']
    nreplies = new_df['nreplies']

    comments = [re.sub(r'^@\w+',"", a) for a in comments]

    comments = [a.lstrip() for a in comments]

    new_top_3_comments_df = pd.DataFrame(columns=['id', 'username', 'comments', 'nlikes', 'nreplies', 'nretweets'])

    for i in range(len(new_df)):
        id = new_df.iloc[i]['id']
        username = new_df.iloc[i]['username']
        comment = new_df.iloc[i]['tweet'] 
        nlike = new_df.iloc[i]['nlikes']
        nreply = new_df.iloc[i]['nreplies']
        nretweet = new_df.iloc[i]['nretweets']

        comment = re.sub(r'^@\w+',"", comment).lstrip() # remove the @ at the beginning of the comments

        comments_metrics = [id, username, comment, nlike, nreply, nretweet]
        new_top_3_comments_df.loc[i] = comments_metrics

    return new_top_3_comments_df


# In[60]:



tweet_id = "1375468096798998529"

replies_df = get_replies_from_tweet("cnn", since_date_str)
new_top_3_comments_df = get_top_3_comments_of_tweet_df(replies_df, tweet_id)


# In[61]:


new_top_3_comments_df


# In[28]:


# replies_df.info()


# In[ ]:





# In[ ]:


"""
For Bruno Part 1
Next build a function that :
- [Done] Goes through latest tweets for all publication handles and then gets the tweet ids for the top 5 tweets with comments
- [Done] Return a dictionary of tweet handle and tweet id for where we will be getting comments
- For each id, get 3 comments, as well as store metrics like num_likes etc etc
"""


# In[ ]:


"""
For Bruno Part 2
- Next also build the function that identifies the latest tweet threads that we can use for Bloverse stories
- ** FOr the medium, lbogger and subbstack strategies, add functionality where we also automatically get the twitter details of the user who created the article
- Also build the function for the blue tick strategy, this is likely one that Halima will have to personally handle given she has better context, what we can do though
is to identify the nigerian, ghanain and indian blue ticks and then leave those to the respective marketing hands to handle
- Then finally, the algorithm for VC twitter handles, and then getting their latest content that we can push out as Bloverse stories... However lets verify the twitter handles are legit VCs first.
- Also work on the 'trending detection algorithm' for the RSS tweets so users can always get a view of the content/articles that are trending
"""


# In[ ]:


"""

"""

