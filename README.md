Crawler and parser utilities for Russian talk radio http://echo.msk.ru.

**Important Note:** the parser is brittle and depends on HTML mark-up evolution of http://echo.msk.ru.

```shell
# directory "echo.msk.ru" will be created in the working directory to store all HTML files downloaded with wget

# print the list of available current and archvied radio shows
# precomputed programs.txt (147 current shows, 301 archived shows) is available at:
# https://github.com/vadimkantorov/echomsk/releases/download/data/programs.txt
#Current shows (excerpt):
#personalno                      Особое мнение
#personalnovash                  Персонально ваш
bash programs.sh > programs.txt

# download and print URLs of all episodes of a given talk show provided its latin name
bash archive.sh "personalno" > personalno.txt

# download and filter episodes by date in yyyymmdd format
MINDATE=20160101 MAXDATE=20170101 bash archive.sh "personalno" > personalno_20160101_20170101.txt

# download and extract transcripts from all episodes from the URL list
bash episodes.sh personalno.txt > personalno.txt.json

# download and extract transcript from a given episode
python3 echomsk.py http://echo.msk.ru/programs/personalno/2589698-echo/

# download and extract episodes from a given archive page
python3 echomsk.py http://echo.msk.ru/programs/personalno/archive/2/ --archive
```

### Dependencies
wget, python3

### License
MIT
