Crawler and parser utilities for Russian talk radio echo.msk.ru

```shell
# prints the list of available current and archvied radio shows
# precomputed programs.txt is available at https://github.com/vadimkantorov/echomsk/releases/download/data/programs.txt
bash programs.sh > programs.txt
#147 current shows, 301 archived shows
#Current shows (excerpt):
#personalno                      Особое мнение
#personalnovash                  Персонально ваш

# downloads and prints URLs of all episodes of a given talk show provided its latin name
bash archive.sh "personalno" > "personalno".txt

# filter the episodes by date in yyyymmdd format
MINDATE=20160101 MAXDATE=20170101 bash archive.sh "personalno" > "personalno".txt
```
