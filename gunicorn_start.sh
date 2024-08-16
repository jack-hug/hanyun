#!/bin/bash
NAME="app"  # 根据你的 Flask 应用模块名称调整
APP_DIR=/home/hanyun
VENV_DIR=/home/hanyun/venv
SOCKFILE=/home/hanyun/gunicorn.sock
NUM_WORKERS=3

echo "Starting $NAME"
cd $APP_DIR
source $VENV_DIR/bin/activate
export PYTHONPATH=$APP_DIR:$PYTHONPATH

exec gunicorn ${NAME}:app --workers=$NUM_WORKERS --bind=unix:$SOCKFILE