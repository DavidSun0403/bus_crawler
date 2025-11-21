#!/bin/bash

# 守護進程腳本 - 監控並自動重啟 crawler.py
# 每分鐘檢查一次，如果程序停止則自動重啟

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRAWLER_PID_FILE="$SCRIPT_DIR/crawler.pid"
DAEMON_PID_FILE="$SCRIPT_DIR/crawler_daemon.pid"
DAEMON_LOG_FILE="$SCRIPT_DIR/crawler_daemon.log"
CHECK_INTERVAL=60  # 檢查間隔（秒）

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DAEMON_LOG_FILE"
}

# 檢查爬蟲是否運行
check_crawler() {
    if [ -f "$CRAWLER_PID_FILE" ]; then
        PID=$(cat "$CRAWLER_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0  # 運行中
        fi
    fi
    return 1  # 未運行
}

# 啟動爬蟲
start_crawler() {
    log "檢測到 crawler.py 未運行，正在啟動..."
    cd "$SCRIPT_DIR"
    
    # 清理舊的 PID 文件
    rm -f "$CRAWLER_PID_FILE"
    
    # 啟動爬蟲
    nohup python3 crawler.py > crawler.log 2>&1 &
    PID=$!
    echo $PID > "$CRAWLER_PID_FILE"
    
    # 等待確認啟動
    sleep 3
    
    if ps -p $PID > /dev/null 2>&1; then
        log "crawler.py 啟動成功 (PID: $PID)"
    else
        log "錯誤: crawler.py 啟動失敗，請查看 crawler.log"
    fi
}

# 主監控循環
monitor_loop() {
    log "守護進程啟動 (PID: $$)"
    log "檢查間隔: ${CHECK_INTERVAL} 秒"
    
    while true; do
        if ! check_crawler; then
            log "警告: crawler.py 未運行"
            start_crawler
        fi
        sleep $CHECK_INTERVAL
    done
}

# 停止守護進程
stop_daemon() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        DAEMON_PID=$(cat "$DAEMON_PID_FILE")
        if ps -p $DAEMON_PID > /dev/null 2>&1; then
            kill $DAEMON_PID
            rm -f "$DAEMON_PID_FILE"
            echo "守護進程已停止"
        else
            rm -f "$DAEMON_PID_FILE"
            echo "守護進程未運行"
        fi
    else
        echo "守護進程未運行"
    fi
}

# 檢查守護進程狀態
status_daemon() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        DAEMON_PID=$(cat "$DAEMON_PID_FILE")
        if ps -p $DAEMON_PID > /dev/null 2>&1; then
            echo "守護進程運行中 (PID: $DAEMON_PID)"
            return 0
        else
            echo "守護進程未運行（PID 文件存在但進程不存在）"
            rm -f "$DAEMON_PID_FILE"
            return 1
        fi
    else
        echo "守護進程未運行"
        return 1
    fi
}

# 處理命令行參數
case "$1" in
    start)
        if status_daemon > /dev/null 2>&1; then
            echo "守護進程已經在運行中"
            exit 1
        fi
        
        # 後台運行守護進程
        nohup $0 monitor >> "$DAEMON_LOG_FILE" 2>&1 &
        DAEMON_PID=$!
        echo $DAEMON_PID > "$DAEMON_PID_FILE"
        echo "守護進程已啟動 (PID: $DAEMON_PID)"
        echo "日誌文件: $DAEMON_LOG_FILE"
        ;;
    
    stop)
        stop_daemon
        ;;
    
    restart)
        stop_daemon
        sleep 2
        $0 start
        ;;
    
    status)
        status_daemon
        echo ""
        if check_crawler; then
            CRAWLER_PID=$(cat "$CRAWLER_PID_FILE")
            echo "crawler.py 運行中 (PID: $CRAWLER_PID)"
        else
            echo "crawler.py 未運行"
        fi
        ;;
    
    monitor)
        # 內部使用，不應直接調用
        monitor_loop
        ;;
    
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo ""
        echo "命令說明:"
        echo "  start   - 啟動守護進程"
        echo "  stop    - 停止守護進程"
        echo "  restart - 重啟守護進程"
        echo "  status  - 查看守護進程和爬蟲狀態"
        exit 1
        ;;
esac

exit 0
