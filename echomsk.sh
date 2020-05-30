set -e

CMD=$1

case $CMD in
	LIST)
		PROG=$2
		if [[ $PROG ]]; then
			wget --no-verbose --no-clobber --no-parent --recursive --level inf -I /programs/$PROG/archive/ echo.msk.ru/programs/$PROG/index.html

			for p in echo.msk.ru/programs/$PROG/index.html echo.msk.ru/programs/$PROG/archive/*/index.html; do
				python3 echomsk.py "$p" --archive --min-date $MINDATE --max-date $MAXDATE
			done | sort | uniq
		else
			wget --quiet --html-extension --force-directories http://echo.msk.ru/programs http://echo.msk.ru/programs/archived
			
			python3 echomsk.py echo.msk.ru/programs.html --programs          | sed -e 's/^/current_show /'
			python3 echomsk.py echo.msk.ru/programs/archived.html --programs | sed -e 's/^/archive_show /'
		fi
		;;
				
	RETR)
		URLLIST=$2
		wget --no-verbose --no-clobber --html-extension --force-directories --content-on-error -i "$URLLIST" || true

		COMMA=
		echo "["
		while read p; do 
			echo $COMMA
			p=${p#"http://"}
			p=${p#"https://"}
			python3 echomsk.py "./${p}index.html"
			COMMA=,
		done < "$URLLIST"
		echo "]"
		;;

	SPEAKERS)
		for p in $2; do
			python3 echomsk.py "$p" --speakers
		done | sort | uniq
		;;
	
esac
