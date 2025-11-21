#!/bin/bash

# 檢查是否已經在運行
if [ -f "crawler.pid" ]; then
    PID=$(cat crawler.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "爬蟲程序已經在運行中 (PID: $PID)"
        exit 1
    else
        echo "清理舊的 PID 文件"
        rm -f crawler.pid
    fi
fi

# 檢查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 python3"
    exit 1
fi

# 檢查 crawler.py 是否存在
if [ ! -f "crawler.py" ]; then
    echo "錯誤: 未找到 crawler.py"
    exit 1
fi

# 啟動爬蟲程序並記錄 PID
echo "正在啟動爬蟲程序..."
nohup python3 crawler.py > crawler.log 2>&1 &
PID=$!

# 保存 PID
echo $PID > crawler.pid

# 等待一下確認程序是否成功啟動
sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "爬蟲程序啟動成功 (PID: $PID)"
    echo "日誌文件: crawler.log"
    echo "可以使用 'tail -f crawler.log' 查看運行日誌"
else
    echo "爬蟲程序啟動失敗，請查看 crawler.log"
    rm -f crawler.pid
    exit 1
fi
