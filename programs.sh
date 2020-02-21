set -e

wget --quiet --html-extension --force-directories http://echo.msk.ru/programs http://echo.msk.ru/programs/archived

printf "Current shows:\n\n"
python3 echomsk.py echo.msk.ru/programs.html --programs

printf "\nArchived shows:\n\n"
python3 echomsk.py echo.msk.ru/programs/archived.html --programs
