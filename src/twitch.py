import json
import requests

class TwitchClient:
	def __init__(self, token):
		self.token = token

		self.header_v5 = {'Client-ID': self.token, 'Accept': 'application/vnd.twitchtv.v5+json'}
		self.header_v6 = {'Client-ID': self.token}

		self.urlbase_v5 = 'https://api.twitch.tv/kraken/'
		self.urlbase_v6 = 'https://api.twitch.tv/helix/'

	def get_base(self, ver):
		if ver == 'v5': return (self.header_v5, self.urlbase_v5)
		elif ver == 'v6': return (self.header_v6, self.urlbase_v6)
		else: return (None, None)
	
	def raw_query_v6(self, q):
		header, base = self.get_base('v6')
		return requests.get(base+q, headers=header).json()

	# Returns (ID, GAMENAME) or None
	def get_game_id(self, name):
		header, base = self.get_base('v5')
		r = requests.get('%s/search/games?query=%s' % (base, name), headers=header).json()
		if r.get('games', None): return (r['games'][0]['_id'], r['games'][0]['name'])
		return None
		
