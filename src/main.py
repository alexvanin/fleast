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
			with open('./web/fl.html', 'r') as reader:
				self.index = reader.read()
			with open('./web/fl_template_main.html', 'r') as reader:
				self.templ_main = reader.read()
			with open('./web/fl_template_stream.html', 'r') as reader:
				self.templ_stream = reader.read()
		except e:
			print("Cannot read token for twitch app or templates, abort.")
			exit(1)
		self.client = TwitchClient(self.twitch_token, freq = 1)

	@cherrypy.expose
	def index(self):
		return 'Hello World'

	@cherrypy.expose
	def fleast(self, game=None, lang=None):
		if game is None and lang is None:
			return self.index
		cherrypy.log('Getting game:"%s" language:%s' % (game, lang))
		data = self.client.get_streams(game, lang)
		if data is None:
			return 'Internal Error' #Do Better

		if data['_total'] == 0: 
			return self.templ_main.format(data['_total'], '')
	
		cherrypy.log('Found %d streams' % data['_total'])

		streams = sorted(data['streams'], key=lambda k: k['viewers'])
		result_str = ''
		for s in streams:
			result_str += self.templ_stream.format(s['channel']['url'], s['preview']['medium'],s['channel']['status'], \
								s['channel']['display_name'], s['viewers']) +'\n'
		return self.templ_main.format(data['_total'], result_str)
 

def main():
	server = FleastServer()
	cherrypy.quickstart(server, '/','./server.conf')


if __name__ == '__main__':
	main()
