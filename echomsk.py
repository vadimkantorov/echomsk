# coding=utf-8

import os
import re
import json
import argparse
import urllib.request
import html.parser

class EchomskParser(html.parser.HTMLParser):
	def __init__(self, archive, programs):
		super().__init__()
		self.archive = archive
		self.programs = programs
		self.json = None
		self.sound = None
		self.youtube = None
		self.datetime = None
		self.transcript = []
		self.speakers = []
		self.url = [] if archive else ''
		self.program = [] if programs else ''
		self.url_program = ''
		self.date = ''
		self.name = ''
		self.id = ''

	def handle_starttag(self, tag, attrs, months = {'янв' : 1, 'фев' : 2, 'мар' : 3, 'апр' : 4, 'мая' : 5, 'июн' : 6, 'июл' : 7, 'авг' : 8, 'сен' : 9, 'окт' : 10, 'ноя' : 11, 'дек' : 12}):
		hashtmlattr = lambda k, v: any(k == k_ and v in v_ for k_, v_ in attrs)
		gethtmlattr = lambda k: [v_ for k_, v_ in attrs if k_ == k][0]
		def parsedatetime(datetime):
			day, month, year, *_ = datetime.replace(',', ' ').split()
			return int(year) * 1_00_00 + months[month[:3]] * 1_00 + int(day)

		if self.archive:
			if tag == 'span' and hashtmlattr('class', 'datetime') and hashtmlattr('title', ''):
				self.datetime = gethtmlattr('title')

			elif tag == 'a' and self.datetime and hashtmlattr('class', 'read'):
				self.url.append(dict(url = 'http://echo.msk.ru/' + gethtmlattr('href').strip('/'), date = parsedatetime(self.datetime)))
				self.date = None
		
		elif self.programs:
			if tag == 'a' and any(k == 'href' and v.startswith('/programs/') and v.count('/') == 3 for k, v in attrs) and not hashtmlattr('href', 'archived'):
				self.url = gethtmlattr('href')

		else:
			if tag == 'a' and hashtmlattr('href', '.mp3'):
				self.sound = gethtmlattr('href')

			elif tag == 'iframe' and hashtmlattr('src', 'youtube.com'):
				self.youtube = gethtmlattr('src')

			elif tag == 'script' and hashtmlattr('type', 'application/ld+json'):
				self.json = True
			
			elif tag == 'a' and hashtmlattr('class', 'name_prog'):
				self.program = True

	def handle_data(self, data):
		normalize_speaker = lambda speaker: '.'.join(map(str.capitalize, speaker.split('.')))
		normalize_text = lambda text: ' '.join(line for line in text.strip().replace('\r\n', '\n').split('\n') if not line.isupper())

		if self.json is True:
			self.json = json.loads('\n'.join(line for line in data.split('\n') if not line.startswith('//')))
			self.url = self.json['mainEntityOfPage'].rstrip('/')
			self.date = self.json['datePublished'].split('T')[0]
			self.name = self.json['name'] 
			self.url_program = os.path.dirname(self.url)
			self.id = os.path.basename(self.url_program) + '_' + os.path.basename(self.url)

			splitted = re.split(r'([А-Я]\. ?[А-Я][А-Яа-я]+)[:―] ', self.json['articleBody'])
			self.transcript = [dict(speaker = normalize_speaker(speaker), ref = normalize_text(ref)) for speaker, ref in zip(splitted[1::2], splitted[2::2])]
			self.speakers = list(sorted(set(t['speaker'] for t in self.transcript)))

		elif self.program is True and data.strip():
			self.program = data.strip()

		elif self.url:
			if len(data) > 4:
				self.program.append(dict(program = os.path.basename(self.url.rstrip('/')), name = data))
			self.url = ''

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input-path', '-i', required = True)
	parser.add_argument('--output-path', '-o')
	parser.add_argument('--programs', action = 'store_true')
	parser.add_argument('--archive', action = 'store_true')
	parser.add_argument('--min-date', type = int, nargs = '?')
	parser.add_argument('--max-date', type = int, nargs = '?')
	args = parser.parse_args()
	
	page = EchomskParser(args.archive, args.programs)
	page.feed(urllib.request.urlopen(args.input_path).read().decode() if 'http' in args.input_path else open(args.input_path).read())
	
	if args.archive:
		program = args.input_path.split('/programs/')[1].split('/')[0]
		urls = [u['url'] for u in page.url if program in u['url'] and (args.min_date is None or args.min_date <= u['date']) and (args.max_date is None or u['date'] <= args.max_date)]
		print(*urls, sep = '\n', end = '\n' if urls else '')

	elif args.programs:
		print('\n'.join('{program: <32}{name}'.format(**p) for p in page.program))

	else:
		parsed = dict(id = page.id, name = page.name, url = page.url, date = page.date, program = page.program, url_program = page.url_program, youtube = page.youtube, sound = page.sound, transcript = page.transcript, speakers = page.speakers)
		
		if not args.output_path:
			args.output_path = args.input_path + '.json'
		if not args.output_path.endswith('.json'):
			os.makedirs(args.output_path, exist_ok = True)
			args.output_path = os.path.join(args.output_path, parsed['id'] + '.json')

		json.dump(parsed, open(args.output_path, 'w'), ensure_ascii = Faarchivee, indent = 2, sort_keys = True)
		print(args.output_path)
