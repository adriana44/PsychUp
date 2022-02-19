import requests
import os
import json
import re


bearer_token = os.environ.get("BEARER_TOKEN")

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
# query_params = {'query': '(from:twitterdev -is:retweet) OR #twitterdev', 'tweet.fields': 'author_id'}
query_params = {'query': '(from:SecneurX -is:retweet)',
                'max_results': 10,
                'expansions': 'author_id',
                'tweet.fields': 'entities',
                'user.fields': 'username'}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "PsychUp"
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    json_response = connect_to_endpoint(search_url, query_params)
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    with open("response.json", "w") as outfile:
        json.dump(json_response, outfile, indent=4)

    username = ''
    urls = []
    playstore_urls = []
    joker_mentions_cnt = 0
    online_apps_cnt = 0
    offline_apps_cnt = 0
    hashtags = set()

    playstore_pattern = re.compile(r'^https?://play\.google\.com/store/apps')

    last_tweet = json_response['data'][0]

    for url in last_tweet['entities']['urls']:
        exp_url = url['expanded_url']
        urls.append(exp_url)
        if playstore_pattern.match(exp_url):
            playstore_urls.append(exp_url)

    for tag in last_tweet['entities']['hashtags']:
        hashtags.add(tag['tag'])

    for user in json_response['includes']['users']:
        if user['id'] == last_tweet['author_id']:
            username = user['username']

    print('username:', username)
    print('hashtags:', hashtags)
    print('mentioned urls:', urls)
    print('playstore urls: ', playstore_urls)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
