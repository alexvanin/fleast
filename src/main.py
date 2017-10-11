#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 

import json
import cherrypy

class FleastServer(object):
	def __init__(self):
		try:
			with open('.token', 'r') as reader:
				self.twitch_token = reader.read().strip()
		except:
			print("Cannot read token for twitch app, abort.")
			exit(1)
		self.client = TwitchClient(self.twitch_token, freq = 1)
	
	@cherrypy.expose
	def index(self):
		return 'Hello World'

	@cherrypy.expose
	def fleast(self, game, lang):
		cherrypy.log('Getting game:"%s" language:%s' % (game, lang))
		data = self.client.get_streams(game, lang)
		if data is None:
			return 'Error!' #Do better
		if data['_total'] == 0: 
			return 'No streams found' #Do better
	
		cherrypy.log('Found %d streams' % data['_total'])

		result = '<html><head><title>Test</title></head><body>'
		streams = sorted(data['streams'], key=lambda k: k['viewers'])
		count = 0
		for s in streams:
			result += '<a href="{0}"><img src="{1}"></a><br>{2}  ::  {3}<br>{4}<hr>'.format( \
						s['channel']['url'], s['preview']['medium'], s['channel']['status'], \
						s['channel']['display_name'], s['viewers'])
		return result
 

def main():
	cherrypy.quickstart(FleastServer())


if __name__ == '__main__':
	main()
