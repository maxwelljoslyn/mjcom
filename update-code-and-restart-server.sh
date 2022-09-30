# cd /home/maxwell/mjcom &&
#     # cp lockfile lockfile.old &&
#     git pull origin master &&
# NOT poetry update -- poetry install prioritizes the exact versions given in poetry.lock if that file exists
#     # diff fresh lockfile and lockfile.old
    # if diff, poetry install &&
#     # rm lockfile.old &&
#     stop-gunicorn.sh &&
#     start-gunicorn.sh &
