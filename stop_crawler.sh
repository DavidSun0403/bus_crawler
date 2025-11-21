#!/bin/bash

# 檢查 PID 文件是否存在
if [ ! -f "crawler.pid" ]; then
    echo "未找到 PID 文件，爬蟲程序可能未運行"
    
    # 嘗試查找 crawler.py 進程
    PIDS=$(pgrep -f "python3 crawler.py")
    if [ -n "$PIDS" ]; then
        echo "找到運行中的 crawler.py 進程: $PIDS"
        echo "是否要停止這些進程？(y/n)"
        read -r response
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            echo "$PIDS" | xargs kill -9
            echo "已強制停止所有 crawler.py 進程"
        fi
    else
        echo "沒有找到運行中的 crawler.py 進程"
    fi
    exit 1
fi

# 讀取 PID
PID=$(cat crawler.pid)

# 檢查進程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "進程 (PID: $PID) 未運行，清理 PID 文件"
    rm -f crawler.pid
    exit 1
fi

# 停止服務
echo "正在停止爬蟲程序 (PID: $PID)..."
kill -TERM $PID

# 等待進程結束
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "爬蟲程序已成功停止"
        rm -f crawler.pid
        exit 0
    fi
    sleep 1
done

# 如果進程仍在運行，強制停止
if ps -p $PID > /dev/null 2>&1; then
    echo "進程未響應，強制停止..."
    kill -9 $PID
    sleep 1
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "爬蟲程序已強制停止"
        rm -f crawler.pid
        exit 0
    else
        echo "無法停止爬蟲程序"
        exit 1
    fi
fi
