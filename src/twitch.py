import requests

class TwitchClient:

	def __init__(self, token):
		self.token = token
		self.header = {'Client-ID': self.token}
		self.urlbase = 'https://api.twitch.tv/helix/'
	
	def raw_query(self, q):
		r = requests.get(self.urlbase+q, headers=self.header)
		return r.text
