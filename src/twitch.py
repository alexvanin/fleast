import requests
import time

class TwitchClient:
	def __init__(self, token, freq=2):
		self.token = token

		self.header_v5 = {'Client-ID': self.token, 'Accept': 'application/vnd.twitchtv.v5+json'}
		self.header_v6 = {'Client-ID': self.token}

		self.urlbase_v5 = 'https://api.twitch.tv/kraken/'
		self.urlbase_v6 = 'https://api.twitch.tv/helix/'

		self.last_q = time.time()
		self.delay = 1/freq

	def do_q(self, base, header):
		if time.time() - self.last_q < self.delay:
			time.sleep(self.delay)
		r = requests.get(base, headers=header).json()	 
		self.last_q = time.time()
		return r	
		
	def get_base(self, ver):
		if ver == 'v5': return (self.header_v5, self.urlbase_v5)
		elif ver == 'v6': return (self.header_v6, self.urlbase_v6)
		else: return (None, None)

	# - # - #
	
	def raw_query_v6(self, q):
		header, base = self.get_base('v6')
		return self.do_q(base+q, header)

	# Returns (ID, GAMENAME) or None
	def get_game_id(self, name):
		header, base = self.get_base('v5')
		r = self.do_q('%s/search/games?query=%s' % (base, name), header)
		if r.get('games', None): return (r['games'][0]['_id'], r['games'][0]['name'])
		return None
		
