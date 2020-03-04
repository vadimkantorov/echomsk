set -e

CMD=$1

case $CMD in
    programs)
        wget --quiet --html-extension --force-directories http://echo.msk.ru/programs http://echo.msk.ru/programs/archived

				printf "Current shows:\n\n"
				python3 echomsk.py echo.msk.ru/programs.html --programs

				printf "\nArchived shows:\n\n"
				python3 echomsk.py echo.msk.ru/programs/archived.html --programs
			  ;;

    archive)
        PROG=$2
				wget --no-verbose --no-clobber --no-parent --recursive --level inf -I /programs/$PROG/archive/ echo.msk.ru/programs/$PROG/index.html

				for p in echo.msk.ru/programs/$PROG/index.html echo.msk.ru/programs/$PROG/archive/*/index.html; do
					python3 echomsk.py "$p" --archive --min-date $MINDATE --max-date $MAXDATE
				done | sort | uniq
				;;
				
		episodes)
				URLLIST=$2
				wget --no-verbose --no-clobber --html-extension --force-directories -i "$URLLIST"

				COMMA=
				echo "["
				while read url; do 
					echo $COMMA
					python3 echomsk.py ./${url#"http://"}index.html
					COMMA=,
				done < "$URLLIST"
				echo "]"
				;;
esac
