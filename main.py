import praw
import os
import requests
import keys
from psaw import PushshiftAPI
from profanity_check import predict, predict_prob
import openai
import json
from prawcore.exceptions import NotFound

def initialize_gpt():
    openai.organization = keys.OPENAI_ORGANIZATION
    openai.api_key = keys.OPENAI_API_KEY

def initialize_reddit_session():
    reddit_session = praw.Reddit(
    client_id=keys.CLIENT_ID,
    client_secret=keys.CLIENT_SECRET,
    username=keys.USERNAME,
    password=keys.PASSWORD,
    user_agent='<HelperBot 1.0>'
 )
    return reddit_session

def make_gpt_request(text):
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{text}"}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=keys.GPT_REQUEST_HEADER, data=json.dumps(data))
    return response.json()['choices'][0]['message']['content']

def isValidUser(name, reddit_session):
    try:
        reddit_session.redditor(name).id
    except NotFound:
        return False
    return True


def main():
    reddit_session = initialize_reddit_session()
    initialize_gpt()

    print("Checking for mentions...")
    for mention in reddit_session.inbox.mentions(limit=25):
        if not mention.new:  # Skip if already seen
            continue

        body_array = mention.body.split()[1:]
        if len(body_array) > 100:
            return
        
        body = ' '.join(body_array)

        if predict([body])[0]:
            return

        response = make_gpt_request(body)

        print(f"New mention by {mention.author} in {mention.subreddit}")
        mention_text = (
            f"Hello, there. I am a ChatGPT search bot summoned by {mention.author}.\n"
            "\n"  # This creates an empty line
            f"The original prompt is: \"{body}\"\n"  # This creates an empty line
            "\n"
            "I made a request to OpenAI's 'gpt-3.5-turbo' and this is its response:\n"
            "\n"
            f"{response}\n"
            "\n"
            "ChatGPT is a language model that can make mistakes, so if you believe that this "
            "response is not accurate, please downvote it and I will delete my response."
            "Thanks for using me!"
            )
        mention.reply(mention_text)
        mention.mark_read()


if __name__ == "__main__":
    main()