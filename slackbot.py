# -*- coding: utf-8 -*-
from slacker import Slacker
import websocket
import json
import logging
from utils import detect_url, parse_abstract


class slackbot:
    def __init__(self, token):
        self._token = token
        self.slack = Slacker(token)

        response = self.slack.rtm.start()
        endpoint = response.body['url']
        self.socket = websocket.create_connection(endpoint)

    def recv(self):
        data = self.socket.recv()
        return json.loads(data)

    def read_arxiv(self, urls, channel):
        """Parse Arxiv urls and send abstract of the paper in pretty format"""
        contents = parse_abstract(urls)
        for content in contents:
            attachments = [
                {
                    "color": "#36a64f",
                    "title": content['title'],
                    "title_link": content['url'],
                    "author_name": content['authors'],
                    "text": content['abstract'],
                }
            ]
            self.slack.chat.post_message(
                channel=channel,
                text='Here is Summary :)',
                attachments=attachments,
                as_user=True)


if __name__ == '__main__':
    # Read token for access
    token = open('./token').read()[:-1]

    # Create Log
    logging.basicConfig(filename='./log', level=logging.DEBUG)

    # Launch slack bot!
    bot = slackbot(token)

    while True:
        data = bot.recv()
        logging.info(data)

        # Arxiv reader
        try:
            text = data['text']
            # only check when text is long enough
            if len(text) > 20:
                urls = detect_url(text)
                if len(urls) > 0:
                    bot.read_arxiv(urls, data['channel'])
        except KeyError:
            continue
