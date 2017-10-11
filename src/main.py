#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 

import json
import cherrypy

class FleastServer(object):
	def __init__(self):
		try:
			with open('.token', 'r') as reader:
				twitch_token = reader.read().strip()
		except:
			print("Cannot read token for twitch app, abort.")
			exit(1)
		client = TwitchClient(twitch_token, freq = 1)
	
	@cherrypy.expose
	def index(self):
		return 'Hello World'

	@cherrypy.expose
	def fleast(self, game, lang):
		return game

def main():
	cherrypy.quickstart(FleastServer())


if __name__ == '__main__':
	main()
