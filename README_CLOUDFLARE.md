# Cloudflare Pages 部署指南

本指南详细说明如何在 Cloudflare Pages 平台上部署和构建 IPTV Spider 项目。

## 1. 项目配置

### 必要文件

- `package.json` - Node.js 项目配置，定义构建脚本
- `build.sh` - Cloudflare Pages 构建脚本
- `pages.config.js` - Cloudflare Pages 配置
- `requirements.txt` - Python 依赖清单
- `_pages/functions/` - Cloudflare Pages 函数目录

### 构建环境配置

Cloudflare Pages 使用 Node.js 环境运行构建过程，但我们的项目是 Python 项目，因此需要：

1. **Node.js 16+** - 用于运行构建脚本
2. **Python 3.7+** - 用于运行项目代码
3. **pip** - 用于安装 Python 依赖

## 2. 部署步骤

### 步骤 1: 准备代码库

确保你的代码库包含上述所有必要文件，并且代码已经推送到 GitHub 或 GitLab 仓库。

### 步骤 2: 在 Cloudflare Pages 上创建项目

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)
2. 导航到 **Pages** 部分
3. 点击 **创建项目** 按钮
4. 选择你的代码仓库
5. 配置构建设置：
   - **构建命令**: `npm run build`
   - **构建输出目录**: `dist`
   - **根目录**: `/`

### 步骤 3: 设置环境变量

在 Cloudflare Pages 项目设置中，添加以下环境变量：

| 变量名 | 值 | 描述 |
|--------|-----|--------|
| NODE_VERSION | 16 | 使用 Node.js 16 版本 |
| PYTHON_VERSION | 3.9 | 使用 Python 3.9 版本 |
| LXML_BUILD_NO_EXTENSIONS | 1 | 禁用 lxml 从源码构建 |

### 步骤 4: 部署项目

1. 点击 **保存并部署** 按钮
2. Cloudflare Pages 将开始构建过程
3. 构建完成后，你的项目将被部署到 Cloudflare 的全球网络

## 3. 构建过程详解

### 构建脚本流程

1. **创建临时目录** - 用于存储临时文件
2. **升级 pip** - 确保使用最新版本的 pip
3. **安装 wheel** - 支持预编译包
4. **安装 lxml 预编译包** - 避免从源码构建的问题
5. **安装项目依赖** - 从 requirements.txt 安装其他依赖
6. **验证安装** - 检查所有依赖是否正确安装
7. **创建构建输出目录** - 准备部署文件
8. **复制必要文件** - 将项目文件复制到输出目录
9. **创建构建信息** - 记录构建时间和状态
10. **清理临时文件** - 减少构建产物大小

### 解决的技术问题

1. **lxml 安装失败** - 使用预编译包避免从源码构建
2. **依赖冲突** - 锁定所有依赖版本
3. **构建环境差异** - 标准化构建过程
4. **构建时间过长** - 优化依赖安装顺序

## 4. 常见问题及解决方案

### 问题 1: lxml 构建失败

**原因**: Cloudflare Pages 环境缺少 libxml2 和 libxslt 开发包

**解决方案**: 使用 `--only-binary=lxml` 强制使用预编译包

### 问题 2: 构建时间超过限制

**原因**: 依赖安装时间过长

**解决方案**: 优化构建脚本，使用预编译包，减少安装时间

### 问题 3: 依赖版本冲突

**原因**: 不同依赖之间的版本不兼容

**解决方案**: 在 requirements.txt 中锁定所有依赖版本

### 问题 4: Python 版本不匹配

**原因**: Cloudflare Pages 默认 Python 版本与项目要求不匹配

**解决方案**: 在环境变量中指定 PYTHON_VERSION

## 5. 性能优化

### 构建优化

- **使用预编译包** - 减少构建时间
- **缓存依赖** - Cloudflare Pages 会自动缓存依赖
- **并行安装** - 优化依赖安装顺序

### 运行时优化

- **使用 Cloudflare CDN** - 加速静态资源访问
- **函数边缘部署** - API 函数在 Cloudflare 边缘节点运行
- **全球网络** - 项目部署到 Cloudflare 的全球网络

## 6. 监控和调试

### 构建日志

Cloudflare Pages 提供详细的构建日志，可以在控制台中查看：

1. 登录 Cloudflare 控制台
2. 导航到你的 Pages 项目
3. 点击 **构建** 标签页
4. 查看最新构建的日志

### 健康检查

项目包含健康检查 API 端点：

- **URL**: `https://your-pages-project.pages.dev/api/health`
- **响应**: JSON 格式的健康状态信息

### 错误处理

构建失败时，检查以下几点：

1. **依赖安装** - 确保所有依赖都能正确安装
2. **构建脚本** - 检查 build.sh 脚本是否有错误
3. **环境变量** - 确保所有必要的环境变量都已设置
4. **Python 版本** - 确保使用正确的 Python 版本

## 7. 总结

通过本指南的配置和步骤，你应该能够在 Cloudflare Pages 平台上成功部署和构建 IPTV Spider 项目。Cloudflare Pages 提供了：

- **全球部署** - 项目部署到 Cloudflare 的全球网络
- **自动构建** - 代码推送到仓库时自动构建
- **边缘函数** - API 函数在边缘节点运行
- **免费计划** - 适合大多数项目的免费使用额度

如果你遇到任何问题，请参考上述常见问题及解决方案，或查看 Cloudflare Pages 官方文档。
