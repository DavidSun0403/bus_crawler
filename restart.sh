#!/bin/bash

# 檢查 PID 文件是否存在
if [ ! -f "gunicorn.pid" ]; then
    echo "未找到 PID 文件"
    echo "正在啟動服務..."
    ./start.sh
    exit $?
fi

# 讀取 PID
PID=$(cat gunicorn.pid)

# 檢查進程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "服務未運行，清理舊 PID 文件"
    rm -f gunicorn.pid
    echo "正在啟動服務..."
    ./start.sh
    exit $?
fi

# 重啟服務
echo "正在重啟服務 (PID: $PID)..."
./stop.sh

if [ $? -eq 0 ]; then
    sleep 2
    ./start.sh
    exit $?
else
    echo "停止服務失敗，無法重啟"
    exit 1
fi
