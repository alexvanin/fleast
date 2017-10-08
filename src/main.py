#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 

def main():
	with open('.token', 'r') as reader:
		twitch_token = reader.read().strip()

	client = TwitchClient(twitch_token)
	print(client.raw_query('streams?first=20'))

if __name__ == '__main__':
	main()
