cd /home/maxwell/mjcom &&
    # cp lockfile lockfile.old &&
    git pull origin master &&
    # diff fresh lockfile and lockfile.old; if diff, poetry update &&
    # rm lockfile.old &&
    stop-gunicorn.sh &&
    start-gunicorn.sh &
