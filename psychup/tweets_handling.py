from pymongo import MongoClient
from google_play_scraper import app
from google_play_scraper.exceptions import NotFoundError
from urllib.parse import urlparse, parse_qs
import re
import os

admin_pwd = os.environ.get("ADMIN_PWD")
client = MongoClient(f'mongodb+srv://admin:{admin_pwd}@cluster0.n6i5h.mongodb.net/?retryWrites=true&w=majority')
db = client.JokerApps


def get_app_data(package_name: str) -> bool:
    """
    Extracts data about a playstore app and stores it in the apps collection.

    :param package_name: package name of a playstore app
    :return: True if the app is online, False otherwise
    """
    print(f'*** Processing app {package_name} ***')

    app_doc = {
        '_id': package_name,
        'online': False
    }
    try:
        app_details = app(package_name)
    except NotFoundError:
        print(package_name, 'is offline')
    else:
        app_doc = {
            '_id': package_name,
            'app_name': app_details['title'],
            'dev_name': app_details['developer'],
            'category': app_details['genre'],
            'last_updated': app_details['released'],
            'installs': app_details['installs'],
            'dev_email': app_details['developerEmail'],
            'privacy_policy_url': app_details['privacyPolicy'],
            'online': True
        }
        print(package_name, 'is online')
    db.apps.update_one({'_id': package_name}, {"$set": app_doc}, upsert=True)
    print(f'*** Finished processing app {package_name} ***')
    return app_doc['online']


def process_one_tweet(tweet: dict, users: list) -> None:
    """
    Extracts data about one given tweet and stores it in the twitter_accounts collection.

    :param tweet: a dictionary representing a tweet
    :param users: a list of dictionaries representing users
    """
    print(f'\n*** Processing tweet {tweet["id"]} ***')
    twitter_accounts = db.twitter_accounts

    acc_id = tweet['author_id']

    account = db.twitter_accounts.find_one({"_id": acc_id})
    if account is None:
        apps_cnt = 0
        online_apps_cnt = 0
        offline_apps_cnt = 0
        app_ids = []
        hashtags = set()
    else:
        apps_cnt = account['apps_cnt']
        online_apps_cnt = account['online_apps_cnt']
        offline_apps_cnt = account['offline_apps_cnt']
        app_ids = account['mentioned_apps']
        hashtags = set(account['hashtags'])

    username = None
    for user in users:
        if user['id'] == acc_id:
            username = user['username']
            break

    playstore_flag = False
    playstore_pattern = re.compile(r'^https?://play\.google\.com/store/apps')
    for url in tweet['entities']['urls']:
        exp_url = url['expanded_url']
        if playstore_pattern.match(exp_url):
            playstore_flag = True
            parsed_url = urlparse(str(exp_url))
            app_id = parse_qs(parsed_url.query)['id'][0]
            if app_id not in app_ids:
                app_ids.append(app_id)
                if get_app_data(app_id) is True:
                    online_apps_cnt += 1
                else:
                    offline_apps_cnt += 1
                apps_cnt += 1

    if playstore_flag is False:
        print('No playstore link found in tweet.')
        print(f'*** Finished processing tweet {tweet["id"]} ***')
        return

    new_hashtags = set([hashtag['tag'] for hashtag in tweet['entities']['hashtags']])
    hashtags.update(new_hashtags)

    account_doc = {
        '_id': acc_id,
        'username': username,
        'hashtags': list(hashtags),
        "mentioned_apps": app_ids,
        'apps_cnt': apps_cnt,
        'online_apps_cnt': online_apps_cnt,
        'offline_apps_cnt': offline_apps_cnt
    }

    twitter_accounts.update_one({'_id': account_doc['_id']}, {"$set": account_doc}, upsert=True)
    print(f'*** Finished processing tweet {tweet["id"]} ***')


def process_tweets(tweets_dict: dict) -> None:
    """
    Extracts data about the given tweets and stores it in the twitter_accounts collection.

    :param tweets_dict: a dictionary of tweets
    """
    tweets = tweets_dict['data']
    users = tweets_dict['includes']['users']

    if isinstance(tweets, list):
        for tweet in tweets:
            process_one_tweet(tweet, users)
    else:
        process_one_tweet(tweets, users)
