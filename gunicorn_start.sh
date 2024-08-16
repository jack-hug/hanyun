#!/bin/bash
NAME="hanyun"
APP_DIR=/home/hanyun
VENV_DIR=/home/hanyun/venv
SOCKFILE=/home/hanyun/gunicorn.sock
NUM_WORKERS=3
echo "Starting $NAME"
cd $APP_DIR
source $VENV_DIR/bin/activate
export PYTHONPATH=$APP_DIR:$PYTHONPATH
exec gunicorn ${NAME}:app -b 0.0.0.0:8000 --workers=$NUM_WORKERS --bind=unix:$SOCKFILE