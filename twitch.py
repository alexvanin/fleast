import cherrypy
import requests
import threading
import time
from urllib.parse import quote


class TwitchClient:
    def __init__(self, token, oath, freq=2):
        self.token = token
        self.oath = oath
        self.lock = threading.Lock()

        self.header_v5 = {'Client-ID': self.token,
                          'Authorization': 'Bearer ' + self.oath,
                          'Accept': 'application/vnd.twitchtv.v5+json'}
        self.header_v6 = {'Client-ID': self.token, 'Authorization': 'Bearer ' + self.oath}
        self.urlbase_v5 = 'https://api.twitch.tv/kraken'
        self.urlbase_v6 = 'https://api.twitch.tv/helix'

        self.last_q = time.time()
        self.delay = 1 / freq

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
            self.last_q = time.time()
            cherrypy.log('Request: OK')
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
        if ver == 'v5':
            return self.header_v5, self.urlbase_v5
        elif ver == 'v6':
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
        return self.do_q(base + q, header)

    def raw_query_v5(self, q):
        """
            Do a query with API v5
            :param q: query string
            :return: string with get query result or None
        """
        header, base = self.get_base('v5')
        return self.do_q(base + q, header)

    def get_game_id(self, name):
        """
            Getting game id
            :param name: string with the name of game
            :return: tuple of integer with game id and string with game name or None, None
        """
        return self.get_game_id_v5(name)

    def get_live_streams(self, name, lang):
        """
            Getting list of livestreams
            :param name: string with the name of game
            :param lang: string with the shortcut of language
            :return: list of all streams which are live
        """
        return self.get_live_streams_v6(name, lang)

    def get_game_id_v5(self, name):
        """
            Getting game id with API v5
            :param name: string with the name of game
            :return: tuple of integer with game id and string with game name or None, None
        """
        header, base = self.get_base('v5')
        r = self.do_q('{}/search/games?query={}'.format(base, name), header)
        if r and r.get('games'):
            return r['games'][0]['_id'], r['games'][0]['name']
        return None, None

    def get_game_id_v6(self, name):
        """
        Getting game id with API v6
        :param name: string with the name of game
        :return: tuple of integer with game id and string with game name or (None,None)
        """

        header, base = self.get_base('v6')
        r = self.do_q('{}/games?name={}'.format(base, name), header)
        if r and r.get('data'):
            return r['data'][0]['id'], r['data'][0]['name']

    def get_live_streams_v5(self, name, lang):
        header, base = self.get_base('v5')
        init_q_template = '{}/search/streams?query={}&limit={}'
        q_template = '{}/search/streams?query={}&limit={}&offset={}'
        data = self.do_q(init_q_template.format(base, name, 100), header)
        if data is None:
            return []
        total = data['_total']
        streams = len(data['streams'])

        while total > streams:
            r = self.do_q(q_template.format(base, name, 100, streams), header)
            if r is None:
                return None
            data['streams'].extend(r['streams'])
            total = r['_total']
            streams = len(data['streams'])
        # Tweak for getting only live sterams
        data['streams'] = [x for x in data['streams'] if
                           x['stream_type'] == 'live' and x['channel']['language'] == lang and x['game'] == name]
        data['_total'] = len(data['streams'])
        return data

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
        data = self.do_q(init_q_template.format(base, lang, 100, game_id[0]), header)
        result['streams'].extend(data['data'])
        while len(data.get('data', [])) > 0:  # there must be non zero value, but search is kinda broken now
            result['streams'].extend(data['data'])
            data = self.do_q(q_template.format(base, lang, 100, data['pagination']['cursor'], game_id[0]), header)
        return self.unique_streams_v6(result)

    def get_irl_live_streams_v6(self, lang):
        header, base = self.get_base('v6')
        init_q_template = "{}/streams?language={}&first={}{}"
        q_template = "{}/streams?language={}&first={}&after={}{}"

        game_id = ''
        irl_ids = ["509660", "509673", "509667", "509669", "509670", "509658",
                   "509672", "509671", "509664", "509663", "417752", "509659"]
        for irl_id in irl_ids:
            game_id += '&game_id={}'.format(irl_id)

        result = {'_total': 0, 'streams': []}
        data = self.do_q(init_q_template.format(base, lang, 100, game_id), header)
        result['streams'].extend(data['data'])
        while len(data.get('data', [])) > 0:  # there must be non zero value, but search is kinda broken now
            result['streams'].extend(data['data'])
            data = self.do_q(q_template.format(base, lang, 100, data['pagination']['cursor'], game_id), header)
        return self.unique_streams_v6(result)

    def unique_streams_v6(self, result):
        uniq_streams = []
        streams = sorted(result['streams'], key=lambda k: k['viewer_count'])
        for s in streams:
            if s['user_name'] not in uniq_streams:
                uniq_streams.append(s['user_name'])
        result['streams'] = uniq_streams
        result['_total'] = len(result['streams'])
        return result
