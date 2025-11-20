#!/bin/bash

# 檢查是否已經在運行
if [ -f "gunicorn.pid" ]; then
    PID=$(cat gunicorn.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "服務已經在運行中 (PID: $PID)"
        exit 1
    else
        echo "清理舊的 PID 文件"
        rm -f gunicorn.pid
    fi
fi

# 啟動 gunicorn 並記錄 PID
echo "正在啟動服務..."
gunicorn app:app --bind 0.0.0.0:80 --daemon --pid gunicorn.pid

if [ $? -eq 0 ]; then
    PID=$(cat gunicorn.pid)
    echo "服務啟動成功 (PID: $PID)"
    echo "訪問地址: http://localhost"
else
    echo "服務啟動失敗"
    exit 1
fi