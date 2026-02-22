# Cloudflare Pages 部署指南

本指南将帮助你配置 Cloudflare Pages 与 GitHub 仓库的连接，实现前端应用的持续部署。

## 前提条件

1. 拥有 Cloudflare 账号
2. 拥有 GitHub 账号
3. 项目已存储在 GitHub 仓库中

## 配置步骤

### 1. 在 Cloudflare 中创建 Pages 项目

1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)
2. 在左侧导航栏中选择 **Pages**
3. 点击 **Create a project** 按钮
4. 选择 **Connect to Git**
5. 选择你的 GitHub 账号并授权 Cloudflare 访问你的仓库
6. 选择 `spider-iptv` 仓库
7. 点击 **Begin setup**

### 2. 配置构建设置

在构建配置页面，设置以下选项：

- **Project name**: `spider-iptv` (生产环境) 或 `iptv-spider-staging` ( staging 环境)
- **Production branch**: `main`
- **Build command**: `npm run build`
- **Build output directory**: `dist`
- **Root directory**: 留空 (使用仓库根目录)

### 3. 配置环境变量

在 **Environment variables** 部分，添加以下环境变量：

| 变量名 | 值 | 环境 |
|-------|-----|------|
| `NODE_ENV` | `production` | Production |
| `VITE_API_URL` | 你的 API 端点 URL | Production |
| `VITE_APP_NAME` | `IPTV Spider` | Production |
| `VITE_APP_VERSION` | `1.0.0` | Production |

### 4. 部署项目

1. 点击 **Save and Deploy** 按钮
2. Cloudflare Pages 将开始构建和部署你的项目
3. 等待部署完成，你将看到部署状态和访问 URL

### 5. 配置 GitHub Secrets

为了让 GitHub Actions 能够部署到 Cloudflare Pages，你需要在 GitHub 仓库中设置以下 Secrets：

1. 登录 GitHub 并导航到你的仓库
2. 点击 **Settings** > **Secrets and variables** > **Actions**
3. 点击 **New repository secret** 并添加以下 Secrets：

| Secret 名称 | 值 |
|------------|-----|
| `CLOUDFLARE_API_TOKEN` | 你的 Cloudflare API 令牌 |
| `CLOUDFLARE_ACCOUNT_ID` | 你的 Cloudflare 账户 ID |
| `VERCEL_TOKEN` | 你的 Vercel API 令牌 (用于后端部署) |

### 6. 获取 Cloudflare API 令牌

1. 登录 Cloudflare 控制台
2. 点击右上角的个人资料图标，选择 **My Profile**
3. 在左侧导航栏中选择 **API Tokens**
4. 点击 **Create Token**
5. 选择 **Create Custom Token**
6. 设置以下权限：
   - **Account** > **Cloudflare Pages** > **Edit**
   - **Account** > **Workers Scripts** > **Edit** (如果使用 Workers)
7. 点击 **Continue to Summary** 并创建令牌
8. 复制生成的 API 令牌并保存到 GitHub Secrets 中

### 7. 获取 Cloudflare 账户 ID

1. 登录 Cloudflare 控制台
2. 点击右上角的个人资料图标，选择 **My Profile**
3. 在 **Account ID** 部分复制你的账户 ID
4. 将账户 ID 保存到 GitHub Secrets 中

## 部署流程

### 开发分支 (develop)
- 推送代码到 `develop` 分支时，GitHub Actions 将执行构建和测试，但不会部署

### Staging 分支 (staging)
- 推送代码到 `staging` 分支时，GitHub Actions 将：
  1. 构建项目
  2. 运行测试
  3. 部署到 Cloudflare Pages 的 staging 环境
  4. 部署后端到 Vercel 的预览环境

### 生产分支 (main)
- 推送代码到 `main` 分支时，GitHub Actions 将：
  1. 构建项目
  2. 运行测试
  3. 部署到 Cloudflare Pages 的生产环境
  4. 部署后端到 Vercel 的生产环境
  5. 运行初始爬虫任务

## 访问 URL

部署完成后，你可以通过以下 URL 访问你的应用：

- 生产环境: `https://spider-iptv.pages.dev`
- Staging 环境: `https://iptv-spider-staging.pages.dev`

## 故障排查

### 构建失败

1. 检查 GitHub Actions 日志，查看具体错误信息
2. 确保所有依赖项已正确安装
3. 检查环境变量配置是否正确

### 部署失败

1. 检查 Cloudflare Pages 部署日志
2. 确保 GitHub Secrets 中的 API 令牌和账户 ID 正确
3. 确保构建输出目录存在且包含必要的文件

### API 连接问题

1. 确保 `VITE_API_URL` 环境变量设置正确
2. 检查后端服务是否正常运行
3. 检查 CORS 配置是否正确

## 自动化部署总结

通过本配置，你已实现：

1. **前端自动化部署**：代码推送到相应分支时，自动构建并部署到 Cloudflare Pages
2. **后端自动化部署**：代码推送到相应分支时，自动部署到 Vercel
3. **持续集成**：每次推送都会运行构建和测试
4. **环境隔离**：生产环境和 staging 环境分开部署
5. **初始爬虫任务**：部署完成后自动运行初始爬虫任务

## 相关链接

- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Vercel 文档](https://vercel.com/docs)
