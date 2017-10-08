#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 

import json

def main():
	with open('.token', 'r') as reader:
		twitch_token = reader.read().strip()

	client = TwitchClient(twitch_token)
	r = client.raw_query_v5('streams/?game=IRL&language=ru&limit=2')
	print(json.dumps(r, indent=4))


if __name__ == '__main__':
	main()
