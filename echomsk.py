# coding=utf-8

import os
import re
import sys
import json
import argparse
import urllib.request
import html.parser

website_root = 'https://echo.msk.ru'

copyright = f'© Радиостанция "Эхо Москвы", {website_root}. При полном или частичном использовании материалов ссылка на "Эхо Москвы" обязательна.'

months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']

contributor_flag = 'Время выхода в эфир'

speaker_regexp = r'''
(?:(?<=[^А-Я])|\b)
(
	(?:РАДИО )?СЛУШАТЕЛЬ(?:НИЦА)?(?:[А-Я ]* *[\.:-]|[А-Я-][а-я]{3,} *[:-])|
	(?:[А-Я] *\.+|[А-Я]{4,}) *(?:[А-Я-]{5,} *[\.:-]|[А-Я-][а-я]{3,}[А-Яа-я]* *[:-] )
)
'''.replace('\n', '').replace('\t', '')

remove = ['РЕКЛАМА', 'Реклама.', 'НОВОСТИ', 'Новости.', 'НВОСТИ', 'ЗАСТАВКА', 'ОТБИВКА', 'ДЖИНГЛ', 'МУЗЫКА', 'АПЛОДИСМЕНТЫ', 'АППЛОДИСМЕНТЫ', 'ПРЕРВАЛСЯ ЗВУК', '&gt;', 'СМЕЕТСЯ', 'СМЕЮТСЯ', '[Смеется]', '[смеется]']

unk = ['НРЗБ', '(нрзб)', 'НЕРАЗБОРЧИВО', 'НЕРЗБ', 'НЕРАЗБ', '[неразборчиво]', 'неразборчиво', '[невнятно]', 'невнятно']

speaker_f = 'СЛУШАТЕЛЬНИЦА'
speaker_m = 'СЛУШАТЕЛЬ'

prepend_space = [speaker_m]

replace_other = {
	'  ' : ': ',
	'[процентов]' : '%', 
	'процентов' : '%', 
	'Кара-Мурза Младший' : 'КАРАМУРЗАМЛАДШИЙ', 
	'КАРА-МУРЗА МЛАДШИЙ' : 'КАРАМУРЗАМЛАДШИЙ', 
	'Кара-Мурза' : 'КАРАМУРЗА', 
	'АВ -' : 'А.Венедиктов -',
	'СДУШАТЕЛЬ' : speaker_m, 
	'СЛУШАТЬЕЛЬ' : speaker_m,
	'СЛУШАЕТЛ' : speaker_m,
	'СЛУШАТЕЬ' : speaker_m,
	'СЛУШАТЬТЕЛЬ' : speaker_m,
	'СЛУШАЬЕЛЬ' : speaker_m,
	'СЛУЩАТЕЛЬ' : speaker_m,
	'СЛУШАТЕЛЬЬ' : speaker_m,
	'СЛУШАТЕЛНЬИЦА' : speaker_f,
	'СЛУШАТЕЛЬНРИЦА' : speaker_f,
	'СЛШАТЕЛЬНИЦА' : speaker_f,
	'СЛУШАТЕЛЬИНЦА' : speaker_f
}

normalize_chars = {ord(k) : v for k, v in {'»' : '"', '«' : '"', '‘' : "'", '’' : "'", '“' : '"', '”' : '"', '„' : '"', 'ё' : 'е', 'Ё' : 'Е', '\xa0' : ' ', '\t' : ' ', '\r' : ' ', '…' : '...', '—' : '-', '―' : '-', '–' : '-', '-' : '-', '—' : '-', '⁄' : '/', '°' : 'о', '¸' : ',', '`' : "`"}.items()}

def normalize_ref(text, strip_chars = ': -'):
	return ' '.join(s for line in text.strip().split('\n') if not line.isupper() for s in line.split()).strip(strip_chars)

def normalize_speaker(speaker, strip_chars = ': -.'):
	splitted = re.split(r'[ \.]', (speaker or '').strip(strip_chars).replace('..', '.'))
	if len(splitted) == 2 and len(splitted[0]) > 1 and not splitted[0].upper().startswith(speaker_m):
		splitted[0] = splitted[0][0]
	if len(splitted) > 0 and len(splitted[0]) == 1:
		splitted[0] += '.'

	return None if not speaker else ''.join(map(str.capitalize, splitted))

class EchomskParser(html.parser.HTMLParser):
	def __init__(self, archive, programs):
		super().__init__()
		self.archive = archive
		self.programs = programs
		self.json = None
		self.youtube = None
		self.rutube = None
		self.datetime = None
		self.contributor = False
		self.contributors = {}
		self.sound_seconds = 0
		self.sound = []
		self.transcript = []
		self.speakers = []
		self.url = [] if archive else ''
		self.program = [] if programs else ''
		self.url_program = ''
		self.date = ''
		self.name = ''
		self.id = ''
		self.last_data = ''
		self.last_attrs = []
		self.last_tag = ''

	def hashtmlattr(self, k, v, startswith = False, proper = False):
		return any(k == k_ and (v in (v_ or '') if not startswith else ((v_ or '').startswith(v) and (not proper or len(v_ or '') > len(v)) )) for k_, v_ in self.last_attrs)
	
	def gethtmlattr(self, k):
		return [v_ for k_, v_ in self.last_attrs if k_ == k][0] or ''

	def handle_starttag(self, tag, attrs):
		self.last_tag = tag
		self.last_attrs = attrs
		def parsedatetime(datetime):
			day, month, year, *_ = datetime.replace(',', ' ').split()
			return int(year) * 100 * 100 + (1 + months.index(month[:3])) * 100 + int(day)

		if self.archive:
			if tag == 'span' and self.hashtmlattr('class', 'datetime') and self.hashtmlattr('title', ''):
				self.datetime = self.gethtmlattr('title')

			elif tag == 'a' and self.datetime and (self.hashtmlattr('class', 'read') or self.hashtmlattr('class', 'view')):
				self.url.append(dict(url = website_root + self.gethtmlattr('href'), date = parsedatetime(self.datetime)))
				self.datetime = None
		
		elif self.programs:
			if tag == 'a' and any(k == 'href' and v.startswith('/programs/') and v.count('/') == 3 for k, v in attrs) and not self.hashtmlattr('href', 'archived'):
				self.url = self.gethtmlattr('href').rstrip('/')

		else:
			if tag == 'a' and self.hashtmlattr('href', '.mp3') and self.hashtmlattr('class', 'load ', startswith = True):
				self.sound.append(self.gethtmlattr('href'))
				duration = self.last_data.strip()
				colons = duration.count(':')
				hh, mm, ss = map(int, ('0:0:0' if colons == 0 else '0:' + duration if colons == 1 else duration).split(':'))
				self.sound_seconds += hh * 60 * 60 + mm * 60 + ss

			elif tag == 'iframe' and self.hashtmlattr('src', 'youtube.com'):
				self.youtube = self.gethtmlattr('src')
			
			elif tag == 'embed' and self.hashtmlattr('src', 'rutube.ru'):
				self.rutube = self.gethtmlattr('src')

			elif tag == 'script' and self.hashtmlattr('type', 'application/ld+json'):
				self.json = True
			
			elif tag == 'a' and self.hashtmlattr('class', 'name_prog'):
				self.program = True

			elif tag == 'a' and self.contributor is not False and (self.hashtmlattr('href', '/contributors/', startswith = True, proper = True) or self.hashtmlattr('href', '/guests/', startswith = True, proper = True)):
				self.contributor = self.gethtmlattr('href')

			elif tag == 'div' and self.hashtmlattr('class', 'multimedia'):
				self.contributor = False

	def handle_data(self, data):
		if data.strip():
			self.last_data = data
		
		if contributor_flag in data:
			self.contributor = True

		if self.json is True:
			self.json = json.loads('\n'.join(line for line in data.split('\n') if not line.startswith('//')))
			self.url = self.json['mainEntityOfPage'].rstrip('/')
			self.date = int(self.json['datePublished'].split('T')[0].replace('-', ''))
			self.name = self.json['name'].translate(normalize_chars) 
			self.url_program = os.path.dirname(self.url)
			self.id = os.path.basename(self.url_program) + '_' + os.path.basename(self.url)

			body = self.json.get('articleBody', '').translate(normalize_chars).strip()
			for replace in remove:
				body = body.replace(replace, '')
			for replace in unk:
				body = body.replace(replace, unk[0])
			for replace in prepend_space:
				body = body.replace(replace, ' ' + replace)
			for src, tgt in replace_other.items():
				body = body.replace(src, tgt)

			for i in range(1):
				splitted = re.split(speaker_regexp, body)
				self.transcript = []
				speaker = None
				for ref in filter(lambda s: bool(s.strip()), splitted):
					if re.match(speaker_regexp, ref):
						speaker = ref
					else:
						self.transcript.append(dict(speaker = normalize_speaker(speaker), ref = normalize_ref(ref)))
						speaker = None

				
				#for speaker, ref in zip(splitted[0::2], splitted[1::2]):
				#	if self.transcript and speaker and not speaker[0].isalpha():
				#		self.transcript[-1]['ref'] += speaker[0]
				#		speaker = speaker[1:]

				self.speakers = list(sorted(filter(bool, set(t['speaker'] for t in self.transcript))))

				#for speaker in (self.speakers if i == 0 else []):
				#	speaker = speaker.upper()
				#	body = body.replace(speaker, ' ' + speaker + ': ')


				#	if '.' in speaker:
				#		speaker = speaker.upper()
				#		a, b = speaker.split('.')
				#		body = body.replace(speaker, ' ' + speaker).replace(a + '. ' + b, ' ' + speaker) # add space before (spaceful) speaker
				#		body = body.replace(b[0] + b, b) # doubled first letter of last name

				#		body = body.replace(a + '. ' + a, a + '.  ' + a).replace(a + '.' + a, a + '.  ' + a) # preparing for auto-inserting first name
				#		body = body.replace(b, speaker) # adding first name
				#		body = body.replace(speaker + ' ', speaker + ': ') # adding colon
				#		body = body.replace(a + speaker, speaker) # doubled first letter of first name

				#		body = body.replace(a + '.' + speaker, speaker).replace(a + '. ' + speaker, speaker) # collapsing doubled first letter with dot present

		elif self.program is True and data.strip():
			self.program = data.strip()

		elif self.programs and self.url:
			if len(data) > 4:
				self.program.append(dict(program = os.path.basename(self.url), name = data))
			self.url = ''

		elif isinstance(self.contributor, str) and len(data.strip()) > 1 and (self.hashtmlattr('class', 'name') or '/contributors/' in self.contributor):
			speaker = normalize_speaker(data)
			self.contributors[speaker] = website_root + self.contributor
			self.contributor = None


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_path')
	parser.add_argument('--programs', action = 'store_true')
	parser.add_argument('--archive', action = 'store_true')
	parser.add_argument('--speakers', action = 'store_true')
	parser.add_argument('--contributors', action = 'store_true')
	parser.add_argument('--min-date', type = int, nargs = '?')
	parser.add_argument('--max-date', type = int, nargs = '?')
	args = parser.parse_args()
	
	print('Parsing', args.input_path, file = sys.stderr)
	
	if args.input_path.endswith('.json'):
		page = json.load(open(args.input_path))
	else:
		page = EchomskParser(args.archive, args.programs)
		page.feed(urllib.request.urlopen(args.input_path).read().decode() if 'http' in args.input_path else open(args.input_path).read() if os.path.exists(args.input_path) else '<html />')
	
	if args.speakers:
		print('\n'.join(sorted(set(speaker for p in page for speaker in p['speakers']))))
	
	elif args.contributors:
		print('\n'.join(sorted(set(contributor for p in page for contributor in p['contributors']))))
	
	elif args.archive:
		program = args.input_path.split('/programs/')[1].split('/')[0]
		urls = [u['url'] for u in page.url if program in u['url'] and (args.min_date is None or args.min_date <= u['date']) and (args.max_date is None or u['date'] <= args.max_date)]
		print(*urls, sep = '\n', end = '\n' if urls else '')

	elif args.programs:
		print('\n'.join('{program: <32}{name}'.format(**p) for p in page.program))
	
	else:
		json.dump(dict(copyright = copyright, id = page.id, input_path = args.input_path.lstrip('./'), name = page.name, url = page.url, date = page.date, program = page.program, url_program = page.url_program, youtube = page.youtube, rutube = page.rutube, sound = page.sound, sound_seconds = page.sound_seconds, transcript = page.transcript, speakers = page.speakers, contributors = page.contributors), sys.stdout, ensure_ascii = False, indent = 2, sort_keys = True)
