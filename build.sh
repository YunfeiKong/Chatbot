#!/bin/bash
set -xe

# 检查virtualenv环境是否存在
ENVIRONMENT_NAME=".chatbot"
PYTHON_VERSION="3.8"

# 检查是否安装了virtualenv
if ! command -v virtualenv &> /dev/null; then
    echo "virtualenv 未安装，正在安装..."
    pip install virtualenv
fi

# 创建虚拟环境
if [ ! -d "$ENVIRONMENT_NAME" ]; then
    echo "环境 $ENVIRONMENT_NAME 不存在，正在创建..."
    virtualenv -p python$PYTHON_VERSION $ENVIRONMENT_NAME
    echo "环境 $ENVIRONMENT_NAME 已成功创建。"
else
    echo "环境 $ENVIRONMENT_NAME 已存在。"
fi

source $ENVIRONMENT_NAME/bin/activate
export PYTHONWARNINGS="ignore:Unverified HTTPS request"

pip install -r requirements.txt
