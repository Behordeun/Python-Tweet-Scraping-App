# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 11:18:37 2018
Latest Update on Fri Jul 08 2022

@author: Behordeun
"""
###################################################################################
# 1 This script is for scraping tweets from Twitter API and saving them to a csv file
# 2 The script is also able to filter the tweets by the keywords in the list
# 3 The script is also able to filter the tweets by the date ranges
# 4 The script is also able to filter the tweets by the location
# 5 The script also allows users to specify the number of tweets they are interested in scraping
# 6 THe script automates the running of sentiment analysis on the tweets, and assigns both polarity and subjectivity labels to the tweets
##################################################################################


from wordcloud import STOPWORDS, WordCloud
import snscrape.modules.twitter as sntwitter
import pandas as pd
import matplotlib.pyplot as plt
from deta import Deta
from datetime import date, datetime
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import time
from textblob import TextBlob
import re
import os
import plotly.express as px
pd.options.plotting.backend = "plotly"

with st.sidebar:
    choose = option_menu("Main Menu",
                         ["Navigation Guide",
                          "About",
                          "Demo",
                          "App",
                          "Contact"],
                         icons=['compass',
                                'house',
                                'file-slides',
                                'app-indicator',
                                'person lines fill'],
                         menu_icon="list",
                         default_index=0,
                         styles={"container": {"padding": "5!important",
                                               "background-color": "#008000"},
                                 "icon": {"color": "orange",
                                          "font-size": "25px"},
                                 "nav-link": {"font-size": "16px",
                                              "text-align": "left",
                                              "margin": "0px",
                                              "--hover-color": "#ADD8E6"},
                                 "nav-link-selected": {"background-color": "#00008B"},
                                 })

    # Connect to Deta Base with your Project Key
    deta = Deta(st.secrets["deta_key"])
    os.environ['DETA_PROJECT_KEY'] = str(deta)
    db1 = deta.Base("search-db")
    db2 = deta.Base("contact-db")

if choose == "Navigation Guide":
    """ __Navigation Guide__"""
    st.markdown(""" <style> .font {
			font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;}
			</style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Guide to using this app</p>',
                unsafe_allow_html=True)
    st.write(f"""
             ## Please make use of the sidebar to navigate through this app.
             # """)

elif choose == "About":
    """
    A brief description of the app
    """
    col1, col2 = st.columns([0.8, 0.2])
    with col1:               # To display the header text using css style
        st.markdown(""" <style> .font {
		font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;}
		</style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">About the Creator</p>',
                    unsafe_allow_html=True)
    # with col2:               # To display brand log
    #    st.image(logo, width=130, caption="Twitter Logo")

    # You can customize the writeup here to fit your own details
    st.write(
        f"""Muhammad SULAIMAN is a Data Science practitioner, an upcoming Data Engineer, and a part-time blogger.\n\nHe writes Data Science articles and tutorials about Python, Data Visualization, Streamlit, Cloud Automation, etc.\n\nHe is also a game lover who loves adventure games.\n\nTo read his blog posts, please visit his [Medium blog](https://medium.com/@behordeun").\n\nTo follow him on LinkedIn, please visit his [LinkedIn profile](https://www.linkedin.com/in/muhammad-abiodun-sulaiman).\n\nTo follow him on Twitter please visit his [Twitter profile](https://twitter.com/prince_analyst).\n\nHe can also be contacted via his [email address](mailto:abiodun.msulaiman@gmail.com).""")
    # st.image(profile, width=200, caption="Muhammad's Profile Picture")

elif choose == 'Demo':
    """ 
    Insert a link to the demo video 
    """
    st.markdown(""" <style> .font {
	font-size:25px ; font-family: 'Cooper Black'; color: #FF9633;}
	</style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">A short demo of the app</p>',
                unsafe_allow_html=True)
    st.video("https://youtu.be/GKtlnkE5ELc")

elif choose == 'App':
    # Add a description of the app
    st.markdown(""" <style> .font {
	font-size:25px ; font-family: 'Cooper Black'; color: #FF9633;}
	</style> """, unsafe_allow_html=True)
    st.markdown(
        '<p class="font">A Web App for Scraping Data from Twitter</p>',
        unsafe_allow_html=True)  # use st.markdown() with CSS style to create a nice-formatted header/tex
    
    # Specify the scraping options available to users
    
    option = st.selectbox(
        'Which scraping option will you prefer?',
        ('Scrape without location',
         'Scrape with location'),
        index=0)

    st.write('Your selected option is: ', option)

    if option == "Scrape without location":

        # Add a text input field to allow users to enter a search term
        st.write(f"""
	    			 # Please fill in the required details below, and click on the Scrape button to run this app
	    			 """)

        today = date.today()
        tweetcount = st.number_input(
            "Enter the number of tweets to retrieve", min_value=0)
        tweetcount = int(tweetcount)
        keyword = st.text_input("Enter your search word here",
                                placeholder='Enter your search keyword here')
        start_date = st.date_input("Enter your start date here")
        end_date = st.date_input("Enter your end date here")
        start_time = datetime.now()
        end_time = datetime.now()
        scrape = st.button("Scrape")

        if scrape:
            if keyword == "":
                st.warning('Please enter a search keyword')
            else:
                st.write(f"""
	    			# Scraping tweets that contained the keyword {keyword} from {start_date} to {end_date}
	    			 """)

            if keyword:
                # Creating list to append tweet data to
                tweets = []
                # Using TwitterSearchScraper to scrape data and append tweets
                # to list
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
                        f'{keyword} since:{start_date} until:{end_date}').get_items()):
                    if i > tweetcount:
                        break
                    tweets.append([tweet.url,
                                   tweet.date,
                                   tweet.id,
                                   tweet.content,
                                   tweet.likeCount,
                                   tweet.retweetCount,
                                   tweet.hashtags,
                                   tweet.replyCount,
                                   tweet.quoteCount,
                                   tweet.source,
                                   tweet.user.username,
                                   tweet.coordinates])

                @st.cache
                def convert_df(tweets):
                    """
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    """

                    return tweets.to_csv().encode('utf-8')  # type: ignore

                # Creating a dataframe from the tweets list above
                tweets = pd.DataFrame(
                    tweets,
                    columns=[
                        'Url',
                        'Datetime',
                        'Tweet Id',
                        'Tweet',
                        'Likes',
                        'Retweets',
                        'Hashtag',
                        'Replies',
                        'Quotes',
                        'Source',
                        'Username',
                        'Coordinates'])
                platform = [text.split('>')[1].split('<')[0]
                            for text in tweets.Source]
                tweets['Platform'] = platform

                def clean_tweet(tweet):
                    """
                    Clean the tweet text by removing links, special characters, hashtags, etc.
                    Create a new column called 'Clean Tweet that contains the clean tweet text
                    """
                    tweet = re.sub('https://\\S+', '', tweet)
                    tweet = re.sub('http://\\S+', '', tweet)
                    tweet = re.sub('[^A-Za-z]+', ' ', tweet)
                    return tweet

                tweets['Cleaned Tweet'] = tweets['Tweet'].apply(clean_tweet)

                def subjectivity(tweet):
                    """
                    Apply the TextBlob subjectivity function to the cleaned tweet text
                    """
                    return TextBlob(tweet).sentiment.subjectivity

                def polarity(tweet):
                    """
                    Apply the TextBlob polarity function to the cleaned tweet text
                    """
                    return TextBlob(tweet).sentiment.polarity

                def polarity_label(score):
                    """
                    Create a new column called 'Polarity Label' that contains matching polarity label for each tweet
                    """
                    if score < 0:
                        return 'Negative'
                    if score == 0:
                        return 'Neutral'
                    if score > 0:  # type: ignore
                        return 'Positive'

                def subjectivity_label(score):
                    """
                    Create a new column called 'Subjectivity Label' that contains matching subjectivity label for each tweet
                    """
                    if score > 0:  # type: ignore
                        return 'Subjective'
                    if score <= 0:  # type: ignore
                        return 'Objective'

                tweets['Coordinates'] = tweets['Coordinates'].fillna(
                    'Coordinates(latitude=0.00000, longitude=0.00000)', inplace=False)
                coordinates = tweets['Coordinates']
                data = []
                coords = coordinates
                for coordinate_values in coords:
                    cleaned_coord = [
                        float(coord) for coord in re.findall(
                            r"\d+\.\d+", str(coordinate_values))]
                    data.append(cleaned_coord)

                data = pd.DataFrame(data, columns=['Latitude', 'Longitude'])
                data['Latitude'] = data['Latitude'].astype(float)
                data['Longitude'] = data['Longitude'].astype(float)
                tweets['Latitude'] = data['Latitude']
                tweets['Longitude'] = data['Longitude']
                tweets['Polarity'] = tweets['Cleaned Tweet'].apply(polarity)
                tweets['Polarity Label'] = tweets['Polarity'].apply(
                    polarity_label)
                tweets['Subjectivity'] = tweets['Cleaned Tweet'].apply(
                    subjectivity)
                tweets['Subjectivity Label'] = tweets['Subjectivity'].apply(
                    subjectivity_label)
                tweets['Polarity Label Coded'] = tweets['Polarity Label'].map(
                    {'Negative': 0, 'Neutral': 1, 'Positive': 2})
                tweets['Subjectivity Label Coded'] = tweets['Subjectivity Label'].map(
                    {'Subjective': 0, 'Objective': 1})
                tweets = tweets[['Url',
                                 'Datetime',
                                 'Tweet Id',
                                 'Tweet',
                                 'Cleaned Tweet',
                                 'Likes',
                                 'Retweets',
                                 'Hashtag',
                                 'Replies',
                                 'Quotes',
                                 'Platform',
                                 'Username',
                                 'Coordinates',
                                 'Latitude',
                                 'Longitude',
                                 'Polarity',
                                 'Polarity Label',
                                 'Subjectivity',
                                 'Subjectivity Label']]

                polarity_label_count = tweets['Polarity Label'].value_counts()
                subjectivity_label_count = tweets['Subjectivity Label'].value_counts(
                )
                no_of_tweets_retrieved = len(tweets)
                no_of_tweets_retrieved_per_platform = tweets['Platform'].value_counts(
                )

                duration = (f'{(datetime.now() - start_time).seconds} seconds')
                db1.put({'Search Date': str(today),
                         'Start Time': str(start_time),
                         'End Time': str(end_time),
                         'keyword': keyword,
                         'Number of Tweets Retrieved': no_of_tweets_retrieved,
                         'start_date': str(start_date),
                         'end_date': str(end_date),
                         'Time Taken to Scrape': str(duration)})

                st.write(f"""
	    				 # {no_of_tweets_retrieved} tweets has been retrieved by this app in {duration}
	    				 """)

                tweets.to_csv(f'./keywords/{keyword}.csv', index=False)
                csv = convert_df(tweets)

                if start_date < end_date:
                    with st.spinner('Scraping in progress, please wait...'):
                        time.sleep(5)
                        st.success('Done scraping!')
                        # st.write(tweets.head())
                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=str(keyword) + '.csv',
                            mime='text/csv',
                        )

                    # polarity_plot()
                    fig = px.pie(
                        tweets,
                        values=tweets['Polarity Label'].value_counts(),
                        names=tweets['Polarity Label'].value_counts().index)
                    fig.update_layout(
                        title_text='Pie Chart of Tweet Polarity Label',
                        template='ggplot2')
                    fig.write_image(f'./Images/{keyword}_polarity_pie.png')
                    st.plotly_chart(fig, use_container_width=True)

                    # subjectivity_plot()
                    fig = px.pie(
                        tweets,
                        values=tweets['Subjectivity Label'].value_counts(),
                        names=tweets['Subjectivity Label'].value_counts().index)
                    fig.update_layout(
                        title_text='Pie Chart of Tweet Subjectivity Label',
                        template='ggplot2')
                    fig.write_image(f'./Images/{keyword}_subjectivity_pie.png')
                    st.plotly_chart(fig, use_container_width=True)

                    # platform_plot()
                    fig = px.bar(
                        tweets,
                        y=tweets['Platform'].value_counts(),
                        x=tweets['Platform'].value_counts().index,
                        color=tweets['Platform'].value_counts().index,
                        labels={
                            'y': 'Number of Tweets',
                            'x': 'Tweet Platform',
                            'color': 'Tweet Platform'})
                    fig.update_layout(
                        yaxis={'categoryorder': 'total descending'},
                        title='Number of Tweets per Platform',
                        xaxis_title=" ",
                        yaxis_title=" ",
                        legend_title="Tweet Platform",
                        template='ggplot2'
                    )
                    fig.write_image(f'./Images/{keyword}_platform_bar.png')
                    st.plotly_chart(fig)

                    # Tweets WordCloud
                    stopwords = set(STOPWORDS)
                    wordcloud = WordCloud(
                        width=400,
                        height=330,
                        max_words=150,
                        colormap='tab20c',
                        stopwords=stopwords,
                        collocations=True
                    ).generate(' '.join(tweets['Cleaned Tweet']))
                    plt.figure(figsize=(10, 8))
                    plt.imshow(wordcloud)  # image show
                    plt.axis('off')  # to off the axis of x and y
                    plt.savefig(f'./Images/{keyword}-Tweet-Word_Cloud.png')
                    image = Image.open(
                        f'./Images/{keyword}-Tweet-Word_Cloud.png')
                    st.image(image, caption='Tweet Wordcloud')

                    # Hashtag WordCloud
                    stopwords = set(STOPWORDS)
                    wordcloud = WordCloud(
                        width=400,
                        height=330,
                        max_words=150,
                        colormap='tab20c',
                        stopwords=stopwords,
                        collocations=True
                    ).generate(' '.join(tweets['Hashtag'].astype(str)))
                    plt.subplots(figsize=(10, 8))
                    plt.imshow(wordcloud)  # image show
                    plt.axis('off')  # to off the axis of x and y
                    plt.savefig(f'./Images/{keyword}-Hashtag-Word_Cloud.png')
                    image = Image.open(
                        f'./Images/{keyword}-Hashtag-Word_Cloud.png')
                    st.image(image, caption=('Hashtag Wordcloud'))

                    # create a database for uploading wordcloud generated by
                    # the app
                    photos = deta.Drive("photos")
                    photos.put(
                        f"{keyword}-Tweets-Word_Cloud.png",
                        path=f"./Images/{keyword}-Tweet-Word_Cloud.png")
                    photos.put(
                        f"{keyword}-Hashtag-Word_Cloud.png",
                        path=f"./Images/{keyword}-Hashtag-Word_Cloud.png")
                    photos.put(
                        f"{keyword}_polarity_pie.png",
                        path=f"./Images/{keyword}_polarity_pie.png")
                    photos.put(
                        f"{keyword}_subjectivity_pie.png",
                        path=f"./Images/{keyword}_subjectivity_pie.png")

                    csv_files = deta.Drive('csv_files')
                    csv_files.put(
                        f"{keyword}.csv",
                        path=f"./keywords/{keyword}.csv")

                elif start_date == end_date:
                    st.write('Please select different date ranges')
                elif end_date > today:
                    st.write('Please select an end date not later than today')
                elif start_date > end_date:
                    st.write(
                        'Please select an end date later than the start date')
                else:
                    st.write('Please select a valid date range')
        else:
            pass
    else:
        # Add a text input field to allow users to enter a search term
        st.write(f"""
	    			 # Please fill in the required details below, and click on the Scrape button to run this app
	    			 """)

        today = date.today()
        tweetcount = st.number_input(
            "Enter the number of tweets to retrieve", min_value=0)
        tweetcount = int(tweetcount)
        keyword = st.text_input("Enter your search word here",
                                placeholder='Enter your search keyword here')
        location = st.text_input("Enter your preferred search location here")
        within = st.number_input(
            "Enter the radius of the search location here",
            min_value=0)
        start_date = st.date_input("Enter your start date here")
        end_date = st.date_input("Enter your end date here")
        start_time = datetime.now()
        end_time = datetime.now()
        scrape = st.button("Scrape")

        if scrape:
            if keyword == "":
                st.warning('Please enter a search keyword')
            else:
                st.write(f"""
	    			# Scraping tweets that contained the keyword {keyword} made in {location} within {within}km from {start_date} to {end_date}
	    			 """)

            if keyword:
                # Creating list to append tweet data to
                tweets = []
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
                        f'{keyword} since:{start_date} until:{end_date} near:{location}, within:{within}km').get_items()):
                    if i > tweetcount:
                        break
                    tweets.append([tweet.url,
                                   tweet.date,
                                   tweet.id,
                                   tweet.content,
                                   tweet.likeCount,
                                   tweet.retweetCount,
                                   tweet.hashtags,
                                   tweet.replyCount,
                                   tweet.quoteCount,
                                   tweet.source,
                                   tweet.user.username,
                                   tweet.coordinates])

                @st.cache
                def convert_df(tweets):
                    # IMPORTANT: Cache the conversion to prevent computation on
                    # every rerun
                    return tweets.to_csv().encode('utf-8')  # type: ignore

                # Creating a dataframe from the tweets list above
                tweets = pd.DataFrame(
                    tweets,
                    columns=[
                        'Url',
                        'Datetime',
                        'Tweet Id',
                        'Tweet',
                        'Likes',
                        'Retweets',
                        'Hashtag',
                        'Replies',
                        'Quotes',
                        'Source',
                        'Username',
                        'Coordinates'])
                platform = [text.split('>')[1].split('<')[0]
                            for text in tweets.Source]
                tweets['Platform'] = platform

                def clean_tweet(tweet):
                    tweet = re.sub('https://\\S+', '', tweet)
                    tweet = re.sub('http://\\S+', '', tweet)
                    tweet = re.sub('[^A-Za-z]+', ' ', tweet)
                    return tweet

                tweets['Cleaned Tweet'] = tweets['Tweet'].apply(clean_tweet)

                def subjectivity(tweet):
                    return TextBlob(tweet).sentiment.subjectivity

                def polarity(tweet):
                    return TextBlob(tweet).sentiment.polarity

                def label(score):
                    if score < 0:
                        return 'Negative'
                    if score == 0:
                        return 'Neutral'
                    if score > 0:  # type: ignore
                        return 'Positive'

                def subjectivity_label(score):
                    if score > 0:  # type: ignore
                        return 'Subjective'
                    if score <= 0:  # type: ignore
                        return 'Objective'

                tweets['Coordinates'] = tweets['Coordinates'].fillna(
                    'Coordinates(latitude=0.00000, longitude=0.00000)', inplace=False)
                coordinates = tweets['Coordinates']
                data = []
                coords = coordinates
                for coordinate_values in coords:
                    cleaned_coord = [
                        float(coord) for coord in re.findall(
                            r"\d+\.\d+", str(coordinate_values))]
                    data.append(cleaned_coord)

                data = pd.DataFrame(data, columns=['Latitude', 'Longitude'])
                data['Latitude'] = data['Latitude'].astype(float)
                data['Longitude'] = data['Longitude'].astype(float)
                tweets['Latitude'] = data['Latitude']
                tweets['Longitude'] = data['Longitude']
                tweets['Polarity'] = tweets['Cleaned Tweet'].apply(polarity)
                tweets['Polarity Label'] = tweets['Polarity'].apply(label)
                tweets['Subjectivity'] = tweets['Cleaned Tweet'].apply(
                    subjectivity)
                tweets['Subjectivity Label'] = tweets['Subjectivity'].apply(
                    subjectivity_label)
                tweets['Polarity Label Coded'] = tweets['Polarity Label'].map(
                    {'Negative': 0, 'Neutral': 1, 'Positive': 2})
                tweets['Subjectivity Label Coded'] = tweets['Subjectivity Label'].map(
                    {'Subjective': 0, 'Objective': 1})
                tweets = tweets[['Url',
                                 'Datetime',
                                 'Tweet Id',
                                 'Tweet',
                                 'Cleaned Tweet',
                                 'Likes',
                                 'Retweets',
                                 'Hashtag',
                                 'Replies',
                                 'Quotes',
                                 'Platform',
                                 'Username',
                                 'Coordinates',
                                 'Latitude',
                                 'Longitude',
                                 'Polarity',
                                 'Polarity Label',
                                 'Subjectivity',
                                 'Subjectivity Label']]

                polarity_label_count = tweets['Polarity Label'].value_counts()
                subjectivity_label_count = tweets['Subjectivity Label'].value_counts(
                )
                no_of_tweets_retrieved = len(tweets)
                no_of_tweets_retrieved_per_platform = tweets['Platform'].value_counts(
                )

                duration = (f'{(datetime.now() - start_time).seconds} seconds')
                db1.put({'Search Date': str(today),
                         'Start Time': str(start_time),
                         'End Time': str(end_time),
                         'keyword': keyword,
                         'Number of Tweets Retrieved': no_of_tweets_retrieved,
                         'start_date': str(start_date),
                         'end_date': str(end_date),
                         'Time Taken to Scrape': str(duration)})

                st.write(f"""
	    				 # {no_of_tweets_retrieved} tweets has been retrieved by this app in {duration}
	    				 """)

                tweets.to_csv(f'./keywords/{keyword}.csv', index=False)
                csv = convert_df(tweets)

                if start_date < end_date:
                    with st.spinner('Scraping in progress, please wait...'):
                        time.sleep(5)
                        st.success('Done scraping!')
                        # st.write(tweets.head())
                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name=str(keyword) + '.csv',
                            mime='text/csv',
                        )

                    # polarity_plot()
                    fig = px.pie(
                        tweets,
                        values=tweets['Polarity Label'].value_counts(),
                        names=tweets['Polarity Label'].value_counts().index)
                    fig.update_layout(
                        title_text='Pie Chart of Tweet Polarity Label',
                        template='ggplot2')
                    fig.write_image(f'./Images/{keyword}_polarity_pie.png')
                    st.plotly_chart(fig, use_container_width=True)

                    # subjectivity_plot()
                    fig = px.pie(
                        tweets,
                        values=tweets['Subjectivity Label'].value_counts(),
                        names=tweets['Subjectivity Label'].value_counts().index)
                    fig.update_layout(
                        title_text='Pie Chart of Tweet Subjectivity Label',
                        template='ggplot2')
                    fig.write_image(f'./Images/{keyword}_subjectivity_pie.png')
                    st.plotly_chart(fig, use_container_width=True)

                    # platform_plot()
                    fig = px.bar(
                        tweets,
                        y=tweets['Platform'].value_counts(),
                        x=tweets['Platform'].value_counts().index,
                        color=tweets['Platform'].value_counts().index,
                        labels={
                            'y': 'Number of Tweets',
                            'x': 'Tweet Platform',
                            'color': 'Tweet Platform'})
                    fig.update_layout(
                        yaxis={'categoryorder': 'total descending'},
                        title='Number of Tweets per Platform',
                        xaxis_title=" ",
                        yaxis_title=" ",
                        legend_title="Tweet Platform",
                        template='ggplot2'
                    )
                    fig.write_image(f'./Images/{keyword}_platform_bar.png')
                    st.plotly_chart(fig)

                    # Tweets WordCloud
                    stopwords = set(STOPWORDS)
                    wordcloud = WordCloud(
                        width=400,
                        height=330,
                        max_words=150,
                        colormap='tab20c',
                        stopwords=stopwords,
                        collocations=True
                    ).generate(' '.join(tweets['Cleaned Tweet']))
                    plt.figure(figsize=(10, 8))
                    plt.imshow(wordcloud)  # image show
                    plt.axis('off')  # to off the axis of x and y
                    plt.savefig(f'./Images/{keyword}-Tweet-Word_Cloud.png')
                    image = Image.open(
                        f'./Images/{keyword}-Tweet-Word_Cloud.png')
                    st.image(image, caption='Tweet Wordcloud')

                    # Hashtag WordCloud
                    stopwords = set(STOPWORDS)
                    wordcloud = WordCloud(
                        width=400,
                        height=330,
                        max_words=150,
                        colormap='tab20c',
                        stopwords=stopwords,
                        collocations=True
                    ).generate(' '.join(tweets['Hashtag'].astype(str)))
                    plt.subplots(figsize=(10, 8))
                    plt.imshow(wordcloud)  # image show
                    plt.axis('off')  # to off the axis of x and y
                    plt.savefig(f'./Images/{keyword}-Hashtag-Word_Cloud.png')
                    image = Image.open(
                        f'./Images/{keyword}-Hashtag-Word_Cloud.png')
                    st.image(image, caption=('Hashtag Wordcloud'))

                    # create a database for uploading wordcloud generated by
                    # the app
                    photos = deta.Drive("photos")
                    photos.put(f"{keyword}-Tweets-Word_Cloud.png",
                               path=f"./Images/{keyword}-Tweet-Word_Cloud.png")
                    photos.put(
                        f"{keyword}-Hashtag-Word_Cloud.png",
                        path=f"./Images/{keyword}-Hashtag-Word_Cloud.png")
                    photos.put(
                        f"{keyword}_polarity_pie.png",
                        path=f"./Images/{keyword}_polarity_pie.png")
                    photos.put(
                        f"{keyword}_subjectivity_pie.png",
                        path=f"./Images/{keyword}_subjectivity_pie.png")

                    csv_files = deta.Drive('csv_files')
                    csv_files.put(
                        f"{keyword}.csv",
                        path=f"./keywords/{keyword}.csv")

                elif start_date == end_date:
                    st.write('Please select different date ranges')
                elif end_date > today:
                    st.write('Please select an end date not later than today')
                elif start_date > end_date:
                    st.write(
                        'Please select an end date later than the start date')
                else:
                    st.write('Please select a valid date range')
        else:
            pass

elif choose == "Contact":
    st.markdown(""" <style> .font {
	font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;}
	</style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Contact Form</p>', unsafe_allow_html=True)
    # set clear_on_submit=True so that the form will be reset/cleared once
    # it's submitted
    with st.form(key='columns_in_form2', clear_on_submit=True):
        st.write(f"""
		# Please help me improve this app. Your honest feedback is highly appreciated.
		""")
        Name = st.text_input(
            label='Please Enter Your Name')  # Collect user feedback
        # Collect user feedback
        Email = st.text_input(label='Please Enter Email')
        regex = "^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$"

        def check(email):
            if(re.search(regex, email)):
                st.write('Thank you for your feedback')
            else:
                st.warning(
                    "Invalid Email, please fill in a valid Email address")

        # Collect user feedback
        Message = st.text_input(label='Please Enter Your Message')

        submitted = st.form_submit_button('Submit')

        if submitted:
            if Name == "" or Email == "" or Message == "":
                st.error(
                    'Please fill in the required details before hitting the submit button')
            if Email != "":
                check(Email)
            else:
                db2.put({'contact Date': str(datetime.now()),
                        "Name": Name, "Email": Email, "Message": Message})

# the footer and more information
st.info("HELP : You can reach out to me via EMAIL below if you need a simple WEB AUTOMATION for your organization. Thank you for using using my Twitter scraping app")
st.write("")
st.markdown(f"""<p style="color:orange ; text-align:center;font-size:15px;">
Copyright|Behordeun2022(c)
""", unsafe_allow_html=True)
st.markdown(f"""<p style="color:orange; text-align:center;font-size:15px;">
📞+2348108316393
""", unsafe_allow_html=True)
