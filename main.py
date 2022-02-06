#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
from twitch import TwitchClient

ver = '1.10.0'


class FleastServer(object):
    def __init__(self):
        try:
            with open('.token', 'r') as reader:
                self.twitch_token = reader.read().strip()
            with open('.secret', 'r') as reader:
                self.secret = reader.read().strip()
            with open('./web/fl.html', 'r') as reader:
                self.index_page = reader.read()
            with open('./web/fl_template_main.html', 'r') as reader:
                self.templ_main = reader.read()
            with open('./web/fl_template_stream.html', 'r') as reader:
                self.templ_stream = reader.read()
            with open('./web/fl_template_lang.html', 'r') as reader:
                self.templ_lang = reader.read().splitlines()
            self.client = TwitchClient(self.twitch_token, self.secret, freq=1)
        except:
            print("Cannot read token for twitch app or templates, abort.")
            exit(1)

    def set_templ_lang(self, lang):
        """
            Set autoselected language in html
            :param lang: string with the shortcut of language
            :return: string with html list of languages and one is selected
        """
        templ = ''
        end = False
        for l in self.templ_lang:
            if not end and 'option value="{}"'.format(lang) in l:
                templ += l.format('selected') + '\n'
                end = True
                continue
            templ += l.format(' ') + '\n'
        return templ.rstrip()

    def to_html(self, text):
        """
            Relace all non xml symbols with aliases
            :param text: string with html source code
            :return: filtered string with html source code
        """
        repl = {'"': '&quot;', '<': '&lt;', '>': '&gt;'}
        text.replace('&', '&amp;')
        for i in repl:
            text = text.replace(i, repl[i])
        return text

    @cherrypy.expose
    def index(self, game=None, lang=None):
        return self.fleast(game, lang)

    @cherrypy.expose
    def fleast(self, game=None, lang=None):
        if game is None or game == '':
            return self.index_page.format(_version_=ver,
                                          _opt_langs_=self.set_templ_lang('ru'))
        game = game.rstrip()
        cherrypy.log('Getting game:"{}" language:{}'.format(game, lang))
        if game == "IRL":
            data = self.client.get_irl_live_streams_v6(lang)
        else:
            data = self.client.get_live_streams_v6(game, lang)

        if data is None:
            return 'Internal Error<br>Tell me more at ' \
                   '<a href="https://twitter.com/alexvanin">https://twitter.com/alexvanin</a>'

        if data['_total'] == 0:
            return self.templ_main.format(_stream_num_=data['_total'],
                                          _game_name_=game,
                                          _opt_langs_=self.set_templ_lang(lang),
                                          _stream_list_='',
                                          _version_=ver)

        cherrypy.log('Found %d streams' % data['_total'])
        result_str = ''
        irl_url = 'https://twitch.tv/{}'
        for s in data['streams']:
            result_str += self.templ_stream.format(irl_url.format(s['user_name']),
                                                   s['thumbnail_url'].format(width=320, height=180),
                                                   self.to_html(s['title']),
                                                   s['user_name'],
                                                   s['viewer_count'])

        return self.templ_main.format(_stream_num_=len(data['streams']),
                                      _game_name_=game,
                                      _opt_langs_=self.set_templ_lang(lang),
                                      _stream_list_=result_str,
                                      _version_=ver)


def main():
    server = FleastServer()
    cherrypy.quickstart(server, '/', './server.conf')


if __name__ == '__main__':
    main()
