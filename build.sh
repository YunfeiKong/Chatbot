#!/bin/bash
set -xe

# 检查virtualenv环境是否存在
ENVIRONMENT_NAME="ChatBot"
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

# 激活虚拟环境
source $ENVIRONMENT_NAME/bin/activate

# 安装paddlepaddle-gpu和其他依赖
pip install paddlepaddle
pip install pytest-runner
pip install paddlespeech

# pip install -r requirements.txt