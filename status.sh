#!/bin/bash

# 檢查 PID 文件是否存在
if [ ! -f "gunicorn.pid" ]; then
    echo "服務未運行"
    exit 1
fi

# 讀取 PID
PID=$(cat gunicorn.pid)

# 檢查進程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "服務未運行"
    rm -f gunicorn.pid
    exit 1
fi

# 顯示進程信息
echo "==================================="
echo "服務狀態: 運行中"
echo "PID: $PID"
echo "-----------------------------------"
ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
echo "==================================="
