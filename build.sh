#!/bin/bash

# Cloudflare Pages 构建脚本

echo "=== 开始构建 IPTV Spider ==="

# 1. 构建前端
echo "=== 构建前端 ==="
cd frontend

# 安装 Node.js 依赖
echo "安装前端依赖..."
npm install

# 构建前端
echo "构建前端应用..."
npm run build

# 复制前端构建输出到根目录的 dist 文件夹
echo "复制前端构建输出..."
cd ..
mkdir -p dist
cp -r frontend/dist/* dist/

# 2. 构建后端
echo "=== 构建后端 ==="

# 设置环境变量以禁用 lxml 从源码构建
export LXML_BUILD_NO_EXTENSIONS=1
export STATIC_DEPS=true

echo "设置环境变量:"
echo "LXML_BUILD_NO_EXTENSIONS=$LXML_BUILD_NO_EXTENSIONS"
echo "STATIC_DEPS=$STATIC_DEPS"

# 创建临时目录
echo "创建临时目录..."
mkdir -p temp

# 升级 pip
echo "升级 pip..."
python -m pip install --upgrade pip

# 安装 wheel 以支持预编译包
echo "安装 wheel..."
python -m pip install wheel

# 安装 lxml 的预编译包 - 强制使用二进制包
echo "安装 lxml 预编译包..."
python -m pip install lxml --only-binary=lxml

# 检查 lxml 是否安装成功
echo "检查 lxml 安装..."
python -c "import lxml; print('lxml version:', lxml.__version__)"

# 安装其他依赖
echo "安装项目依赖..."
python -m pip install -r requirements.txt

# 验证安装
echo "验证安装..."
python -c "import requests; print('requests version:', requests.__version__)"
python -c "import bs4; print('beautifulsoup4 version:', bs4.__version__)"
python -c "import psutil; print('psutil version:', psutil.__version__)"

# 3. 复制 Cloudflare Functions
echo "=== 复制 Cloudflare Functions ==="
cp -r functions dist/functions 2>/dev/null || echo "No functions directory to copy"
cp -r _pages/_headers dist/ 2>/dev/null || echo "No _headers file to copy"
cp -r _pages/_redirects dist/ 2>/dev/null || echo "No _redirects file to copy"

# 4. 复制必要的后端文件
echo "=== 复制后端文件 ==="
mkdir -p dist/src
echo "复制后端代码..."
cp -r src/* dist/src/
cp main.py dist/
cp requirements.txt dist/
cp README.md dist/

# 5. 创建构建信息文件
echo "=== 创建构建信息 ==="
echo "Build completed at: $(date)" > dist/BUILD_INFO.txt
echo "Frontend build: $(cat frontend/package.json | grep version | head -1 | cut -d '"' -f 4)" >> dist/BUILD_INFO.txt
echo "Python backend: $(python -c 'import sys; print(sys.version)')" >> dist/BUILD_INFO.txt

# 6. 清理临时文件
echo "=== 清理临时文件 ==="
rm -rf temp

# 7. 验证构建输出
echo "=== 验证构建输出 ==="
echo "构建输出目录结构:"
ls -la dist/
if [ -d "dist/functions" ]; then
    echo "Cloudflare Functions:"
    ls -la dist/functions/
fi

if [ -d "dist/static" ]; then
    echo "前端静态资源:"
    ls -la dist/static/
fi

echo "=== 构建完成 ==="
echo "构建输出目录: $(pwd)/dist"
echo "下一步: 部署到 Cloudflare Pages 或其他平台"
