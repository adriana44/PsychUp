import requests
import os
import json
from tweets_handling import process_tweets

bearer_token = os.environ.get("BEARER_TOKEN")

# search_url = "https://api.twitter.com/2/tweets/search/recent/"
# search_url = "https://api.twitter.com/2/users/1389110954923724800/tweets"

query_params = {'expansions': 'author_id',
                'tweet.fields': 'entities',
                'user.fields': 'username'}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "PsychUp"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "Joker (#Malware OR #Trojan OR #Android OR #CyberSecurity OR #PlayStore) has:links",
         "tag": "joker tweet"}
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    with requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            auth=bearer_oauth,
            stream=True,
            params=query_params
    ) as response:
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Cannot get stream (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                # print(json.dumps(json_response, indent=4, sort_keys=True))
                with open("response.json", "w") as outfile:
                    json.dump(json_response, outfile, indent=4)
                process_tweets(json_response)


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)

# def connect_to_endpoint(url):
#     response = requests.get(url, auth=bearer_oauth)
#     print(response.status_code)
#     if response.status_code != 200:
#         raise Exception(response.status_code, response.text)
#     return response.json()


# def main():
#     # json_response = connect_to_endpoint(search_url, query_params)
#     # json_response = connect_to_endpoint(search_url)
#     # with open("response.json", "w") as outfile:
#     #     json.dump(json_response, outfile, indent=4)


if __name__ == '__main__':
    main()
