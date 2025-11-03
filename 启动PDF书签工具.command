#!/bin/bash
# PDF Content Bookmark Generator 启动脚本

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本所在目录
cd "$DIR"

# 检查Python是否可用
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "错误: 未找到Python解释器"
    echo "请先安装Python 3.6或更高版本"
    read -p "按回车键退出..." 
    exit 1
fi

# 检查main.py是否存在
if [ ! -f "main.py" ]; then
    echo "错误: 未找到main.py文件"
    echo "请确保在正确的目录下运行此脚本"
    read -p "按回车键退出..." 
    exit 1
fi

# 启动应用
echo "正在启动PDF Content Bookmark Generator..."
echo "请在浏览器中打开 http://localhost:8083 访问应用"
echo "按 Ctrl+C 可以停止应用"

$PYTHON_CMD main.py