set -e

URLLIST=$1

wget --no-verbose --no-clobber --html-extension --force-directories -i "$URLLIST"

COMMA=
echo "["
while read url; do 
	echo $COMMA
	python3 echomsk.py ./${url#"http://"}index.html
	COMMA=,
done < "$URLLIST"
echo "]"
