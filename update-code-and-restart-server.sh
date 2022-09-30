cd /home/maxwell/mjcom &&
    # copy old lockfile BEFORE potentially pulling new one
    cp lockfile lockfile.old &&
    git pull origin master;

# $DIFF = diff fresh lockfile and lockfile.old
# poetry install, NOT update. install prioritizes the versions in poetry.lock if it exists
# if diff, poetry install &&
# rm lockfile.old &&

stop-gunicorn.sh; start-gunicorn.sh &
# TODO is this background "start" working right
