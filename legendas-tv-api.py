#!/usr/bin/env python
#-*- encoding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import re
import requests


class Legenda(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return u'%s (%s)' % (self.title, self.title_ptbr)

    @property
    def download(self):
        if self.id:
            return LegendasTV.URL_DOWNLOAD % self.id
        else: pass # raise exception


class LegendasTV(object):
    URL_BUSCA = 'http://legendas.tv/index.php?opcao=buscarlegenda'

    URL_DOWNLOAD = 'http://legendas.tv/info.php?d=%s&c=1'

    URL_LOGIN = 'http://legendas.tv/login_verificar.php'

    LEGENDA_LANG = { 'pt-br': 1,
                     'pt':    10,
                     'en':    2,
                     'es':    3,
                     'other': 100,
                     'all':   99 }

    LEGENDA_TIPO = { 'release': 1,
                     'filme':   2,
                     'usuario': 3 }

    LEGENDA_REGEX = re.compile(r"gpop\('(?P<title>[^,]+)'," +
                                      "'(?P<title_ptbr>[^,]+)'," + 
                                      "'(?P<filename>[^,]+)'," +
                                      "'(?P<cds>[^,]+)'," + 
                                      "'(?P<fps>[^,]+)'," +
                                      "'(?P<size>[^,]+)'," +
                                      "'(?P<downloads>[^,]+)'," + 
                                      "[^,]+,'" + 
                                      "(?P<submited>[^,]+)'" +
                                "\).*abredown\('(?P<id>.*)'\)")

    def __init__(self, usuario, senha):
        self.usuario = usuario
        self.senha = senha

        self._login()

    def _login(self):
        auth = { 'txtLogin': self.usuario,
                 'txtSenha': self.senha }

        r = requests.post(self.URL_LOGIN, data=auth)
        if r.cookies['PHPSESSID']:
            self.cookie = { 'PHPSESSID': r.cookies['PHPSESSID'] }
        else: self.cookie = None

    def _request(self, url, method='GET', data=None):
        if self.cookie:
            if method == 'GET':
                r = requests.get(url, cookies=self.cookie, stream=True)
            if method == 'POST' and data:
                r = requests.post(url, data=data, cookies=self.cookie)

            return r
        else: pass # raise exception

    def _parser(self, data):
        legendas = []

        html = BeautifulSoup(data)
        results = html.find(id='conteudodest').findAll('span')
        for result in results:
            meta = self.LEGENDA_REGEX.search(unicode(result))
            if meta:
                legenda = Legenda(**meta.groupdict())
                legendas.append(legenda)
            else: pass # raise exception

        return legendas

    def search(self, q, lang='pt-br', tipo='release'):
        if not q:
           pass # raise exception

        if not lang or not self.LEGENDA_LANG.get(lang):
           pass # raise exception

        if not tipo or not self.LEGENDA_TIPO.get(tipo):
           pass # raise exception

        busca = { 'txtLegenda': q,
                  'int_idioma': self.LEGENDA_LANG[lang],
                  'selTipo':    self.LEGENDA_TIPO[tipo] }

        r = self._request(self.URL_BUSCA, method='POST', data=busca)
        legenda = self._parser(r.text)[0]

        r = self._request(legenda.download)
        filename = r.url.split('/')[-1] # TODO
        with open('/home/leandrotoledo/Downloads/' + filename, 'wb') as handle:
	    print u'Downloading:', legenda
            handle.write(r.content)


ltv = LegendasTV('toledd31', 'd4g6970')
ltv.search('A Time to Kill YIFY')
