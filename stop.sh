#!/bin/bash

# 指定要查找的端口号
PORT=8086

# 查找使用指定端口号的进程ID (PID)
PID=$(lsof -t -i:$PORT)

# 检查是否找到进程
if [ -z "$PID" ]; then
  echo "没有找到使用端口号 $PORT 的进程。"
else
  # 终止进程
  echo "终止使用端口号 $PORT 的进程 (PID: $PID)..."
  kill -9 $PID

  # 检查是否成功终止进程
  if [ $? -eq 0 ]; then
    echo "进程 (PID: $PID) 已成功终止。"
  else
    echo "无法终止进程 (PID: $PID)。"
  fi
fi
