#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitch import TwitchClient 

import json
import cherrypy

ver = '1.00'


class FleastServer(object):
	def __init__(self):
		try:
			with open('.token', 'r') as reader:
				self.twitch_token = reader.read().strip()
			with open('./web/fl.html', 'r') as reader:
				self.index_page = reader.read()
			with open('./web/fl_template_main.html', 'r') as reader:
				self.templ_main = reader.read()
			with open('./web/fl_template_stream.html', 'r') as reader:
				self.templ_stream = reader.read()
			self.client = TwitchClient(self.twitch_token, freq = 1)
		except e:
			print("Cannot read token for twitch app or templates, abort.")
			exit(1)


	@cherrypy.expose
	def index(self, game=None, lang=None):
		return self.fleast(game, lang)

	@cherrypy.expose
	def fleast(self, game=None, lang=None):
		if game is None and lang is None:
			return self.index_page.format(_version_ = ver)

		cherrypy.log('Getting game:"%s" language:%s' % (game, lang))
		data = self.client.get_streams(game, lang)

		if data is None:
			return 'Internal Error<br>Tell me more at <a href="https://twitter.com/alexvanin">https://twitter.com/alexvanin</a>' 

		if data['_total'] == 0: 
			return self.templ_main.format( _stream_num_ = data['_total'], _stream_list_ = '', _version_ = ver)
	
		cherrypy.log('Found %d streams' % data['_total'])

		streams = sorted(data['streams'], key=lambda k: k['viewers'])
		result_str = ''
		for s in streams:
			result_str += self.templ_stream.format(s['channel']['url'], s['preview']['medium'],s['channel']['status'], \
								s['channel']['display_name'], s['viewers']) +'\n'

		return self.templ_main.format(_stream_num_ = data['_total'], _game_name_ = game,  _stream_list_ = result_str, _version_ = ver)
 

def main():
	server = FleastServer()
	cherrypy.quickstart(server, '/fleast', './server.conf')


if __name__ == '__main__':
	main()
