#!/bin/bash

# 测试 npm 安装脚本
echo "=== 测试 npm 安装 ==="

# 清理 npm 缓存
echo "清理 npm 缓存..."
npm cache clean --force

# 安装依赖
echo "安装 npm 依赖..."
npm install --progress=false

# 验证安装
echo "验证 npm 安装..."
npm list

# 运行构建脚本
echo "运行构建脚本..."
npm run build

echo "=== 测试完成 ==="
