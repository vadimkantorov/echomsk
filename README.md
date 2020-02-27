### Crawler and parser utilities for Russian talk radio http://echo.msk.ru.

**Important Note:** the parser is extremely brittle and will very likely fail when layout of http://echo.msk.ru evolves. The parser worked OK on 2020-02-27.

### Usage
```shell
# PARSER USAGE:

# download and extract transcript from a given episode
python3 echomsk.py http://echo.msk.ru/programs/personalno/2589698-echo/

# download and extract episodes from a given archive page
python3 echomsk.py http://echo.msk.ru/programs/personalno/archive/2/ --archive

# download and extract shows from the current shows page
python3 echomsk.py http://echo.msk.ru/programs/ --programs


# CRAWLER USAGE:

# directory "./echo.msk.ru" will be created to cache all HTML files downloaded with wget

# print the list of available current and archvied radio shows
# precomputed programs.txt (147 current shows, 301 archived shows) is available at:
# https://github.com/vadimkantorov/echomsk/releases/download/data/programs.txt
# Current shows (excerpt):
# personalno                      Особое мнение
# personalnovash                  Персонально ваш
bash programs.sh > programs.txt

# download and print URLs of all episodes of a given talk show provided its latin name
bash archive.sh "victory" > victory.txt

# download and filter the episodes by date in yyyymmdd format
# https://github.com/vadimkantorov/echomsk/releases/download/data/personalno_20000101_20191231.txt
MINDATE=20000101 MAXDATE=20191231 bash archive.sh "personalno" > personalno_20000101_20191231.txt

# download and extract transcripts from all episodes from the URL list
# Total wall clock time: 1h 16m 21s, downloaded: 7120 files, 1.4G
# https://github.com/vadimkantorov/echomsk/releases/download/data/personalno_20000101_20191231.txt.json.gz
bash episodes.sh personalno_20000101_20191231.txt > personalno_20000101_20191231.txt.json
```

### Data Copyright
[Echo of Moscow Radio](http://echo.msk.ru) has all rights reserved on the released corpus. If you are using the released corpus, you must make sure yourself you are abiding all relevant copyright laws.

### Dependencies
python3 (for parser), wget (for crawler) 

### Code License
MIT
