set -e

PROG=$1

wget --quiet --recursive --no-clobber --no-parent -I /programs/$PROG/archive/ echo.msk.ru/programs/$PROG/index.html
for p in echo.msk.ru/programs/$PROG/index.html echo.msk.ru/programs/$PROG/archive/*/index.html; do
	python3 echomsk.py "$p" --archive --min-date $MINDATE --max-date $MAXDATE
done | sort | uniq
