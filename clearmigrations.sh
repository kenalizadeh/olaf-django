#!/bin/bash -x

cd olaf

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete &&
find . -path "*/migrations/*.pyc"  -delete &&
echo "\nDjango migration files deleted successfully.\n\n\033[0;35mHINT: Run: python olaf/manage.py reset_db to reset current database.\033[0m\n"
