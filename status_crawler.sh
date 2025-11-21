#!/bin/bash

# 檢查 PID 文件是否存在
if [ ! -f "crawler.pid" ]; then
    echo "爬蟲程序未運行"
    exit 1
fi

# 讀取 PID
PID=$(cat crawler.pid)

# 檢查進程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "爬蟲程序未運行"
    rm -f crawler.pid
    exit 1
fi

# 顯示進程信息
echo "==================================="
echo "爬蟲程序狀態: 運行中"
echo "PID: $PID"
echo "-----------------------------------"
ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
echo "==================================="
echo ""
echo "日誌文件最後 20 行:"
echo "-----------------------------------"
if [ -f "crawler.log" ]; then
    tail -n 20 crawler.log
else
    echo "未找到日誌文件 crawler.log"
fi
