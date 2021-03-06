### Crawler and parser utilities for Russian talk radio http://echo.msk.ru.

**Important Note:** the parser is extremely brittle and will very likely fail when the HTML layout of http://echo.msk.ru evolves. The parser worked OK on 2020-06-01.

### Usage
```shell
# download and extract transcript from a given episode
python3 echomsk.py http://echo.msk.ru/programs/personalno/2589698-echo/

# download and extract episodes from a given archive page
python3 echomsk.py http://echo.msk.ru/programs/personalno/archive/2/ --archive

# download and extract shows from the current shows page
python3 echomsk.py http://echo.msk.ru/programs/ --programs

# directory "./echo.msk.ru" will be created to cache all HTML files downloaded with wget
# print the list of available current and archvied radio shows
# precomputed programs.txt (147 current shows, 301 archived shows) is available at:
# https://github.com/vadimkantorov/echomsk/releases/download/data/programs.txt
# excerpt:
# current_show personalno                      Особое мнение
# current_show personalnovash                  Персонально ваш
bash echomsk.sh LIST > programs.txt

# download and print URLs of all episodes of a given talk show provided its latin name
bash echomsk.sh LIST victory > victory.txt

# download and filter the episodes by date in yyyymmdd format
# https://github.com/vadimkantorov/echomsk/releases/download/data/personalno_20000101_20191231.txt
MINDATE=20000101 MAXDATE=20191231 bash echomsk.sh LIST "personalno" > personalno_20000101_20191231.txt

# download and extract transcripts from all episodes from the URL list
# Total wall clock time: 1h 16m 21s, downloaded: 7120 files, 1.4G
# https://github.com/vadimkantorov/echomsk/releases/download/data/personalno_20000101_20191231.txt.json.gz
bash echomsk.sh RETR personalno_20000101_20191231.txt > personalno_20000101_20191231.txt.json

# download and print all URLs for all programs and dump speakers
# https://github.com/vadimkantorov/echomsk/releases/download/data/dump_20000101_20191231.tar.gz
export MINDATE=20000101
export MAXDATE=20191231
OUT=dump_${MINDATE}_${MAXDATE}
for PROG in $(cut -d' ' -f2 programs.txt); do
	bash echomsk.sh LIST $PROG > $OUT/${PROG}.txt
	bash echomsk.sh RETR $OUT/${PROG}.txt > $OUT/${PROG}.json 
done
tar -czf $OUT.tar.gz $OUT
# ls $OUT/*.json | xargs -n1 python3 echomsk.py --speakers | sort | uniq  > speakers_${MINDATE}_${MAXDATE}.txt
```

### Example parser output
```shell
python3 echomsk.py https://echo.msk.ru/programs/personalno/2594534-echo
```
```
{
  "contributors": {
    "А.Нарышкин": "https://echo.msk.ru/contributors/717722-echo/",
    "К.Рогов": "https://echo.msk.ru/guests/762/"
  },
  "copyright": "© Радиостанция \"Эхо Москвы\", https://echo.msk.ru. При полном или частичном использовании материалов ссылка на \"Эхо Москвы\" обязательна.",
  "date": 20200226,
  "id": "personalno_2594534-echo",
  "input_path": "https://echo.msk.ru/programs/personalno/2594534-echo",
  "name": "Интервью / Кирилл Рогов",
  "program": "Особое мнение",
  "rutube": null,
  "sound": [
    "https://cdn.echo.msk.ru/snd/2020-02-26-osoboe-1908.mp3"
  ],
  "sound_seconds": 2236,
  "speakers": [
    "А.Нарышкин",
    "К.Рогов"
  ],
  "transcript": [
    {
      "ref": "Всем добрый вечер, в эфире \"Эха\" Москвы программа \"Особое мнение\". Меня зовут Алексей Нарышкин, напротив меня Кирилл Рогов, я вас приветствую.",
      "speaker": "А.Нарышкин"
    },
    {
      "ref": "Добрый вечер.",
      "speaker": "К.Рогов"
    },
    ...
  ],
  "url": "https://echo.msk.ru/programs/personalno/2594534-echo",
  "url_program": "https://echo.msk.ru/programs/personalno",
  "youtube": "https://www.youtube.com/embed/zTIYZXVUGfw"
}
```

### Data Copyright
Examples of crawled data are provided in [repo releases](https://github.com/vadimkantorov/echomsk/releases/tag/data) for research purposes only. [Echo of Moscow Radio](http://echo.msk.ru) has all rights reserved on [released data](https://github.com/vadimkantorov/echomsk/releases/tag/data). If you are using the released corpus, you must make sure yourself you are abiding all relevant copyright laws.

### Dependencies
python3 (for parser), wget (for crawler) 

### Code License
MIT
