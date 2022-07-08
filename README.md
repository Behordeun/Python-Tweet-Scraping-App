# Tweet Scraping App

## App Directory

streamlit-tweet-scraping-app/streamlit-tweet-scraping-app/
├── app.py

├── _config.yml

├── .git

├── Images

├── keywords

├── LICENSE

├── Procfile

├── requirements.txt

├── setup.sh

├── .streamlit

└──  └── secrets.toml

## About the App

A python web app built on Streamlit for automating tweet scraping and sentiment analysis of the respective tweets.

This application presents users with two options while scrating historical tweets. These options are:

1. Scrape without location.
2. Scrape with location (location and radius specification enabled).

With either option, users are required to specify a ***search keyword of choice, number of tweets to retrieve, date range (start and end),  location & radius (where applicable) from which the tweet will be retrieved.*** After having filled in the required fields, the app will fetch relevant tweets, clean the tweet text, perform a sentiment analysis on the retrieved tweets by calculating both the polarity and subjectivity score of each tweet, while also indicating their respective labels. Here, the **polarity label** could be either of:

1. Positive
2. Neutral or
3. Negative.

While the **subjectivity label** is either of:

1. Subjective or
2. Objective.

The retrieved information is thereafter converted in a data frame, that can be downloaded as a ***csv* file **which can be used for further analysis by the user.

The app used ***deta** *database to log essential events on the app. To avoid erros while trying to run this app (either locally, or through the deployed version of the app), you can create a deta account [here](https://web.deta.sh/), and create a key for your account. Next:

```
# Create a folder to hold the deta database credentials

mkdir .streamlit
cd .streamlit
touch secrets.toml
```

Copy the following content into the created **toml** file.

```
# .streamlit/secrets.toml

deta_key = "xxx.....xxx"
```

Please replace the deta_key with the your own deta_key.

***Please note that the app is continously being worked on, and new features will continue to be added to the app over time.***

## How to run the App

To run the application from your choice IDE, please ensure that you have **Streamlit** and **Heroku** installed on your computer. Simply clone the repository using these commands:

```
git clone https://github.com/Behordeun/Python-Tweet_Scraping-App.git
```

```
cd Python_Tweet_Scraping-App
```

```
pip install -r requirements.txt
```

```
streamlit run app.py
```

# Contact

Feel free to contact me if you need some help with your python automation projects via:

1. LinkedIn: [Muhammad Abiodun Sulaiman](https://www.linkedin.com/in/muhammad-abiodun-sulaiman)
2. Twitter: [@Prince_Analyst](https://www.twitter.com/prince_analyst)
3. E-mail: [abiodun.msulaiman@gmail.com](mailto:abiodun.msulaiman@gmail.com)

# THANK YOU FOR USING MY APP
