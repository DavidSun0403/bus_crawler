#!/bin/bash

# 檢查 PID 文件是否存在
if [ ! -f "crawler.pid" ]; then
    echo "未找到 PID 文件"
    echo "正在啟動爬蟲程序..."
    ./start_crawler.sh
    exit $?
fi

# 讀取 PID
PID=$(cat crawler.pid)

# 檢查進程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "爬蟲程序未運行，清理舊 PID 文件"
    rm -f crawler.pid
    echo "正在啟動爬蟲程序..."
    ./start_crawler.sh
    exit $?
fi

# 重啟服務
echo "正在重啟爬蟲程序 (PID: $PID)..."
./stop_crawler.sh

if [ $? -eq 0 ]; then
    sleep 2
    ./start_crawler.sh
    exit $?
else
    echo "停止爬蟲程序失敗，無法重啟"
    exit 1
fi
