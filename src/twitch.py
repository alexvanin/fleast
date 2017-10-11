import requests
import time
import threading

import cherrypy

class TwitchClient:
	def __init__(self, token, freq=2):
		self.token = token
		self.lock = threading.Lock()

		self.header_v5 = {'Client-ID': self.token, 'Accept': 'application/vnd.twitchtv.v5+json'}
		self.header_v6 = {'Client-ID': self.token}
		self.urlbase_v5 = 'https://api.twitch.tv/kraken'
		self.urlbase_v6 = 'https://api.twitch.tv/helix'

		self.last_q = time.time()
		self.delay = 1/freq
		

	def do_q(self, base, header):
		self.lock.acquire()
		try:
			cherrypy.log('Request: %s' % base)
			delta = time.time() - self.last_q 
			if delta < self.delay:
				time.sleep(delta)
			r = requests.get(base, headers=header).json()	 
			self.last_q = time.time()
		except:	
			cherrypy.log('Request: FAIL')
			r = None
		finally:
			cherrypy.log('Request: OK')
			self.lock.release()
			return r
		
	def get_base(self, ver):
		if ver == 'v5': return (self.header_v5, self.urlbase_v5)
		elif ver == 'v6': return (self.header_v6, self.urlbase_v6)
		else: return None

	# - # - #
	
	def raw_query_v6(self, q):
		header, base = self.get_base('v6')
		return self.do_q(base+q, header)

	def raw_query_v5(self, q):
		header, base = self.get_base('v5')
		return self.do_q(base+q, header)

	# Returns (ID, GAMENAME) or None
	def get_game_id(self, name):
		header, base = self.get_base('v5')
		r = self.do_q('%s/search/games?query=%s' % (base, name), header)
		if r and r.get('games'): return (r['games'][0]['_id'], r['games'][0]['name'])
		return None

	def get_streams(self, name, lang):
		header, base = self.get_base('v5')
		data = self.do_q('%s/streams/?game=%s&language=%s&limit=%s&stream_type=live' % (base, name, lang, 100), header)
		if data is None: return None
		total = data['_total']; streams = len(data['streams'])

		while total > streams:
			r = self.do_q('%s/streams/?game=%s&language=%s&limit=%s&stream_type=live&offset=%s' % (base, name, lang, 100, streams), header)
			if r is None: return None
			data['streams'].extend(r['streams'])
			total = r['_total']; streams = len(data['streams'])

		return data


