#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 
import json

def main():
	with open('.token', 'r') as reader:
		twitch_token = reader.read().strip()

	client = TwitchClient(twitch_token)
	streams = client.raw_query_v6('streams?game_id=%s&first=100&language=ru&type=live' % client.get_game_id('IRL')[0])
	for i in streams['data']:
		print(i['title'])


if __name__ == '__main__':
	main()
