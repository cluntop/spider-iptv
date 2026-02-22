#!/bin/bash

# Cloudflare Pages 构建脚本

echo "=== 开始构建 IPTV Spider ==="

# 创建临时目录
echo "创建临时目录..."
mkdir -p temp

# 升级 pip
echo "升级 pip..."
python -m pip install --upgrade pip

# 安装 wheel 以支持预编译包
echo "安装 wheel..."
python -m pip install wheel

# 安装 lxml 的预编译包
echo "安装 lxml 预编译包..."
python -m pip install lxml==4.9.4 --only-binary=lxml

# 安装其他依赖
echo "安装项目依赖..."
python -m pip install -r requirements.txt

# 验证安装
echo "验证安装..."
python -c "import lxml; print('lxml version:', lxml.__version__)"
python -c "import requests; print('requests version:', requests.__version__)"
python -c "import bs4; print('beautifulsoup4 version:', bs4.__version__)"
python -c "import psutil; print('psutil version:', psutil.__version__)"

# 创建构建输出目录
echo "创建构建输出目录..."
mkdir -p dist

# 复制必要文件到输出目录
echo "复制文件到输出目录..."
cp -r src dist/
cp main.py dist/
cp config.json dist/
cp requirements.txt dist/
cp README.md dist/

# 创建构建信息文件
echo "创建构建信息..."
echo "Build completed at: $(date)" > dist/BUILD_INFO.txt

# 清理临时文件
echo "清理临时文件..."
rm -rf temp

echo "=== 构建完成 ==="
