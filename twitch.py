import cherrypy
import requests
import threading
import time

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from urllib.parse import quote


class TwitchClient:
    def __init__(self, token, secret, freq=2):
        self.token = token
        self.lock = threading.Lock()

        self.header_v6 = {'Client-ID': self.token}
        self.urlbase_v6 = 'https://api.twitch.tv/helix'

        self.last_q = time.time()
        self.delay = 1 / freq

        # authentication
        self.oauth = ''
        self.oauth_token_url = 'https://id.twitch.tv/oauth2/token'
        self.auth_secret = secret
        oauth_clint = BackendApplicationClient(client_id=self.token)
        self.oauth_session = OAuth2Session(client=oauth_clint)
        self.update_oauth()

    def update_oauth(self):
        """
            Update self.oauth token based on client id and secret.
            :return: nothing
        """
        token = self.oauth_session.fetch_token(token_url=self.oauth_token_url,
                                               client_secret=self.auth_secret,
                                               include_client_id=True)
        self.oauth = token['access_token']

    def do_q_auth_v6(self, base, header):
        """
            Do query with v6 authentication header and single retry.
            :param base: string with requesting URL
            :param header: dictionary of http headers
            :return: string with response or None
        """
        result = self.do_q(base, header | {'Authorization': 'Bearer ' + self.oauth})
        if result is not None:
            return result
        self.update_oauth()
        return self.do_q(base, header | {'Authorization': 'Bearer ' + self.oauth})

    def do_q(self, base, header):
        """
            Do query for twitch server
            :param base: string with requesting URL
            :param header: dictionary of http headers
            :return: string with response or None
        """
        self.lock.acquire()  # Lock for 1 at time query
        try:
            cherrypy.log('Request: %s' % base)
            delta = time.time() - self.last_q  # Delta for correct query freq
            if delta < self.delay:
                time.sleep(delta)  # Sleep remaining time
            r = requests.get(base, headers=header).json()
            error_message = r.get("error", "")
            if len(error_message) > 0:
                cherrypy.log('Request: fail with error "%s"' % error_message)
                r = None
            else:
                cherrypy.log('Request: OK')
            self.last_q = time.time()
        except requests.exceptions.RequestException as e:
            cherrypy.log('Request: FAIL')
            cherrypy.log('Error: {}'.format(e))
            r = None
        finally:
            self.lock.release()  # Do not forget to release lock
            return r

    def get_base(self, ver):
        """
            Get base which is depended on API version
            :param ver: string with API version ('v5' or 'v6')
            :return: tuple with list of headers and URL string
            :raises: value error on incorrect API version
        """
        if ver == 'v6':
            return self.header_v6, self.urlbase_v6
        else:
            raise ValueError('Not supported API version')

    # - # - #

    def raw_query_v6(self, q):
        """
            Do a query with API v6
            :param q: query string
            :return: string with get query result or None
        """
        header, base = self.get_base('v6')
        return self.do_q_auth_v6(base + q, header)

    def get_game_id_v6(self, name):
        """
        Getting game id with API v6
        :param name: string with the name of game
        :return: tuple of integer with game id and string with game name or (None,None)
        """

        header, base = self.get_base('v6')
        r = self.do_q_auth_v6('{}/games?name={}'.format(base, name), header)
        if r and r.get('data'):
            return r['data'][0]['id'], r['data'][0]['name']

    def get_live_streams_v6(self, name, lang):
        """
            Getting list of livestreams with API v5
            :param name: string with the name of game
            :param lang: string with the shortcut of language
            :return: list of all streams which are live with this format -
                https://dev.twitch.tv/docs/v5/reference/search/#search-streams
        """
        result = {'_total': 0, 'streams': []}
        game_id = self.get_game_id_v6(quote(name))
        if game_id is None:
            return result

        header, base = self.get_base('v6')
        init_q_template = "{}/streams?language={}&first={}&game_id={}"
        q_template = "{}/streams?language={}&first={}&after={}&game_id={}"
        data = self.do_q_auth_v6(init_q_template.format(base, lang, 100, game_id[0]), header)
        result['streams'].extend(data['data'])
        while len(data.get('data', [])) > 0:  # there must be non zero value, but search is kinda broken now
            result['streams'].extend(data['data'])
            data = self.do_q_auth_v6(q_template.format(base, lang, 100, data['pagination']['cursor'], game_id[0]), header)
        return self.unique_streams_v6(result)

    def get_irl_live_streams_v6(self, lang):
        header, base = self.get_base('v6')
        init_q_template = "{}/streams?language={}&first={}{}"
        q_template = "{}/streams?language={}&first={}&after={}{}"

        game_id = ''
        """
        417752: Talk Shows & Podcasts
        509658: Just Chatting
        509659: ASMR
        509660: Art
        509663: Special Events
        509664: Tabletop RPGs
        509667: Food & Drink
        509669: Beauty & Body Art
        509670: Science & Technology
        509671: Fitness & Health [exclude]
        509672: Travel & Outdoors
        509673: Makers & Crafting       
        515214: Politics [exclude]
        518203: Sports
        116747788: Pools, Hot Tubs, and Beaches
        272263131: Animals, Aquariums, and Zoos [exclude]
        1469308723: Software and Game Development
        """
        irl_ids = ["417752", "509658", "509659", "509660", "509663", "509664",
                   "509667", "509669", "509670", "509672", "509673", "518203",
                   "116747788", "1469308723"]
        for irl_id in irl_ids:
            game_id += '&game_id={}'.format(irl_id)

        result = {'_total': 0, 'streams': []}
        data = self.do_q_auth_v6(init_q_template.format(base, lang, 100, game_id), header)
        while len(data.get('data', [])) > 0:  # there must be non zero value, but search is kinda broken now
            result['streams'].extend(data['data'])
            if data['pagination'].get("cursor", None) is None:  # sometimes server return results without cursor
                break
            data = self.do_q_auth_v6(q_template.format(base, lang, 100, data['pagination']['cursor'], game_id), header)
        return self.unique_streams_v6(result)

    def unique_streams_v6(self, result):
        uniq_streams = []
        streams = sorted(result['streams'], key=lambda k: k['viewer_count'])
        result['streams']=[]
        for s in streams:
            if s['user_name'] not in uniq_streams:
                uniq_streams.append(s['user_name'])
                result['streams'].append(s)
        result['_total'] = len(result['streams'])
        return result
