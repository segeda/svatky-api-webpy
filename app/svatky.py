# coding: utf-8
#
# Copyright (c) 2011, Petr Severa
# For the full copyright and license information, please view the file LICENSE.txt that was distributed with this source code.

"""Svátky API"""

import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import web
import markdown
import simplejson
from datetime import datetime
from datetime import timedelta


urls = [ ]


def set_headers(format):
	time_format = '%a, %d %b %Y %H:%M:%S GMT'
	last_modified = datetime.strptime(datetime.now().strftime('%a, %d %b %Y 00:00:00 GMT'), time_format)
	
	web.header('Access-Control-Allow-Origin', '*')
	web.http.modified(last_modified)
	web.header('Cache-Control', 'max-age=600')
	web.http.expires(timedelta(days=1))
	
	if format == 'json':
		web.header('Content-Type', 'application/json; charset=UTF-8')
	
	if format == 'xml':
		web.header('Content-Type', 'text/xml; charset=UTF-8')
	
	if format == 'txt':
		web.header('Content-Type', 'text/plain; charset=UTF-8')


def get_svatky(format):
	request = web.input()
	svatky = []
	lang = 'cs'
	name = request.get('name')
	date = request.get('date')
	
	if request.get('lang') == 'sk':
		import sk as slovnik
		lang = 'sk'
	else:
		import cs as slovnik
	
	if not name and not date:
		date = datetime.now().strftime('%d%m')
	
	if name:
		if name in slovnik.jmeno:
			for datum in slovnik.jmeno[name]:
				svatek = datum, name
				svatky.append(svatek)
		response = get_format(set(svatky), format)
		return response
	
	if date:
		if date in slovnik.datum:
			for jmeno in slovnik.datum[date]:
				svatek = date, jmeno
				svatky.append(svatek)
		response = get_format(set(svatky), format)
		return response


def get_format(set_svatky, format):
	if format == 'txt':
		return get_txt(set_svatky)
	
	if format == 'xml':
		return get_xml(set_svatky)
	
	if format == 'json':
		return get_json(set_svatky)


def get_txt(set_svatky):
	txt = ''
	for svatek in set_svatky:
		txt += '%s;%s\n' % svatek
	return txt


def get_xml(set_svatky):
	xml = '<?xml version="1.0" encoding="UTF-8"?>'
	xml += '<svatky>'
	for svatek in set_svatky:
		xml += '<svatek><date>%s</date><name>%s</name></svatek>' % svatek
	xml += '</svatky>'
	return xml


def get_json(set_svatky):
	jsonData = []
	for svatek in set_svatky:
		jsonData.append({'date':svatek[0], 'name':svatek[1]})
	return simplejson.dumps(jsonData)


class ActionMetaClass(type):
	def __init__(klass, name, bases, attrs):
		urls.append(attrs["url"])
		urls.append("%s.%s" % (klass.__module__, name))


class Json:
	__metaclass__ = ActionMetaClass
	url = "/json"
	def GET(self):
		set_headers('json')
		return get_svatky('json')


class Xml:
	__metaclass__ = ActionMetaClass
	url = "/xml"
	def GET(self):
		set_headers('xml')
		return get_svatky('xml')


class Txt:
	__metaclass__ = ActionMetaClass
	url = "/txt"
	def GET(self):
		set_headers('txt')
		return get_svatky('txt')


class Index:
	__metaclass__ = ActionMetaClass
	url = "/"
	def GET(self):
		t_globals = {'debug': web.config.debug, 'markdown': markdown.markdown,}
		curdir = os.path.dirname(__file__)
		render = web.template.render(curdir + '/templates/', globals=t_globals)
		footer = u"Ať Vám slouží. Chyby a připomínky hlašte, prosím, na <segedacz@gmail.com>."
		return render.index(footer)


if web.config.debug:
	application = web.application(urls, globals())
else:
	application = web.application(urls, globals()).wsgifunc()

if __name__ == "__main__":
	application.run()
