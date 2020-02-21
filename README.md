Crawler and parser utilities for Russian talk radio echo.msk.ru

```
# prints the list of available current and archvied radio shows
# precomputed programs.txt is available at 
bash programs.sh > programs.txt

# downloads and prints URLs of all episodes of a given talk show provided its latin name
# bash archive.sh "personalno" > "personalno".txt

# filter the episodes by date in yyyymmdd format
# MINDATE=20160101 MAXDATE=20170101 bash archive.sh "personalno" > "personalno".txt
```
