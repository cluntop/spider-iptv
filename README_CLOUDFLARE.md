# Cloudflare Pages 部署文档

## 项目概述

IPTV 爬虫管理系统是一个基于 React + Cloudflare Pages 的前端应用，用于管理 IPTV 频道、监控系统状态和配置系统参数。本文档详细说明了如何将项目部署到 Cloudflare Pages 平台。

## 技术栈

- **前端**: React + Vite + Ant Design
- **后端**: Cloudflare Pages Functions (JavaScript)
- **构建工具**: Vite
- **部署平台**: Cloudflare Pages

## 项目结构

```
├── _pages/             # Cloudflare Pages 配置和函数
│   ├── functions/      # Cloudflare Functions
│   │   └── api/        # API 处理函数
│   ├── _headers        # HTTP 头部配置
│   └── _redirects      # 路由重定向规则
├── dist/               # 构建输出目录
├── frontend/           # 前端源代码
│   ├── src/            # 前端源码
│   ├── package.json    # 前端依赖
│   └── vite.config.js  # Vite 配置
├── pages.config.js     # Cloudflare Pages 配置
└── README_CLOUDFLARE.md # 本部署文档
```

## Cloudflare Pages 配置

### 1. 基本配置

- **构建命令**: `cd frontend && npm install && npm run build`
- **构建输出目录**: `dist`
- **Node 版本**: 18

### 2. 环境变量

在 Cloudflare Pages 控制台中配置以下环境变量：

| 变量名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `NODE_VERSION` | 构建 | `18` | Node.js 版本 |
| `VITE_API_BASE_URL` | 环境 | `/api` | API 基础 URL |
| `VITE_APP_TITLE` | 环境 | `IPTV 管理系统` | 应用标题 |
| `VITE_APP_ENV` | 环境 | `production` | 应用环境 |

### 3. 路由规则

路由规则已在 `_pages/_redirects` 文件中配置：

- API 路由: `/api/*` → 保持原样
- 静态资源: `/assets/*`, `/chunks/*`, `/entry/*` → 保持原样
- 单页应用: `/*` → 重定向到 `/index.html`

### 4. 缓存策略

缓存策略已在 `_pages/_headers` 文件中配置：

- 静态资源: 1年缓存期 (`public, max-age=31536000, immutable`)
- API 请求: 无缓存 (`no-cache, no-store, must-revalidate`)
- 安全头部: 设置了 `X-Frame-Options`, `X-Content-Type-Options` 等

## 部署步骤

### 1. 准备工作

1. **创建 Cloudflare 账户**
   - 访问 [Cloudflare 控制台](https://dash.cloudflare.com/)
   - 注册或登录现有账户

2. **连接 GitHub 仓库**
   - 在 Cloudflare Pages 控制台中，点击 "Create a project"
   - 选择 "Connect to Git"
   - 选择您的 GitHub 仓库

### 2. 配置构建设置

1. **基本配置**
   - **项目名称**: 输入您的项目名称
   - **生产分支**: 选择要部署的分支（如 `main` 或 `master`）
   - **构建命令**: `cd frontend && npm install && npm run build`
   - **构建输出目录**: `dist`

2. **环境变量**
   - 点击 "Environment variables"
   - 添加上述环境变量配置

3. **高级设置**
   - **Node 版本**: 选择 `18`
   - **Build system version**: 选择最新版本

### 3. 部署项目

1. **开始部署**
   - 点击 "Save and Deploy"
   - Cloudflare Pages 将开始构建和部署过程

2. **监控部署状态**
   - 在 "Deployments" 标签页中查看部署进度
   - 部署完成后，会显示部署状态和访问 URL

3. **访问应用**
   - 部署完成后，通过分配的 URL 访问应用
   - 默认 URL 格式: `https://{project-name}.pages.dev`

## API 结构

Cloudflare Pages Functions 提供了以下 API 端点：

### 1. 健康检查

- **URL**: `/api/health`
- **方法**: GET
- **描述**: 检查 API 服务状态
- **响应**: JSON 格式的健康状态信息

### 2. 认证相关

- **登录**: `/api/auth/login` (POST)
- **登出**: `/api/auth/logout` (POST)
- **获取用户信息**: `/api/auth/me` (GET)

### 3. 频道管理

- **获取频道列表**: `/api/channels` (GET)
- **创建频道**: `/api/channels` (POST)
- **更新频道**: `/api/channels` (PUT)
- **删除频道**: `/api/channels` (DELETE)

## 前端构建优化

### 1. 资源打包策略

- **代码分割**: 按功能模块分割代码
  - `vendor`: React 相关依赖
  - `antd`: Ant Design 组件库
  - `charts`: 图表库
  - `form`: 表单相关库
  - `echarts`: ECharts 图表库

- **资源命名**: 使用哈希值命名静态资源，确保缓存有效性
  - CSS: `assets/index-{hash}.css`
  - JS chunks: `chunks/{name}-{hash}.js`
  - 入口文件: `entry/index-{hash}.js`

- **压缩优化**: 使用 Terser 进行代码压缩

### 2. 性能优化

- **懒加载**: 大型组件使用动态导入
- **缓存策略**: 合理设置静态资源缓存
- **网络优化**: 最小化 HTTP 请求，合并资源

## 环境变量配置

### 前端环境变量

前端环境变量在 `frontend/.env` 文件中配置：

```env
# 前端环境变量配置
VITE_API_BASE_URL=/api
VITE_APP_TITLE=IPTV 管理系统
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=production
VITE_APP_DEBUG=false
```

### Cloudflare Pages 环境变量

在 Cloudflare Pages 控制台中配置：

1. **构建环境变量**: 影响构建过程的变量
2. **生产环境变量**: 部署后应用使用的变量

## 常见问题解决

### 1. 构建失败

**症状**: 部署过程中构建失败

**解决方案**:
- 检查 `package.json` 中的依赖配置
- 确保 Node 版本为 18
- 检查 `vite.config.js` 中的配置
- 查看构建日志中的详细错误信息

### 2. API 请求失败

**症状**: 前端无法连接到 API

**解决方案**:
- 检查 Cloudflare Functions 是否正确部署
- 验证 API 路由规则配置
- 检查 `_redirects` 文件中的路由配置
- 查看浏览器开发者工具中的网络请求

### 3. 静态资源加载失败

**症状**: CSS、JS 等静态资源无法加载

**解决方案**:
- 检查构建输出目录结构
- 验证 `vite.config.js` 中的 `base` 配置
- 检查 `_headers` 文件中的缓存策略

### 4. 路由刷新 404

**症状**: 刷新页面后出现 404 错误

**解决方案**:
- 确保 `_redirects` 文件中配置了单页应用路由规则
- 验证重定向规则是否正确

## 最佳实践

### 1. 构建优化

- **依赖管理**: 定期更新依赖包
- **代码分割**: 合理使用动态导入
- **资源压缩**: 启用生产环境压缩
- **缓存策略**: 合理设置缓存时间

### 2. 安全最佳实践

- **HTTP 头部**: 配置适当的安全头部
- **CORS 设置**: 合理配置跨域资源共享
- **输入验证**: 前端和后端都要进行输入验证
- **环境变量**: 敏感信息通过环境变量配置

### 3. 部署最佳实践

- **分支管理**: 使用不同分支部署测试和生产环境
- **构建缓存**: 启用 Cloudflare Pages 的构建缓存
- **部署预览**: 利用 Cloudflare Pages 的部署预览功能
- **监控**: 配置应用性能监控

## 监控和维护

### 1. 健康检查

- **API 健康检查**: `/api/health`
- **系统状态监控**: 前端仪表盘页面
- **Cloudflare Analytics**: 使用 Cloudflare 的分析工具

### 2. 日志管理

- **函数日志**: Cloudflare Pages Functions 日志
- **前端错误**: 浏览器控制台和监控工具
- **构建日志**: Cloudflare Pages 构建日志

### 3. 定期维护

- **依赖更新**: 定期更新前端依赖
- **代码优化**: 优化构建输出大小
- **缓存清理**: 必要时清理 Cloudflare 缓存

## 部署验证

部署完成后，验证以下功能：

1. **前端访问**: 打开部署 URL，确认页面正常加载
2. **API 连接**: 测试登录和数据获取功能
3. **路由导航**: 测试页面导航和刷新功能
4. **响应速度**: 检查页面加载速度和 API 响应时间
5. **跨浏览器兼容性**: 在不同浏览器中测试

## 故障排除

### 1. 构建错误

**错误信息**: `Error: Could not resolve './store'`
**解决方案**: 确保所有依赖模块都已正确安装和配置

### 2. 部署错误

**错误信息**: `Deployment failed: Build failed`
**解决方案**: 检查构建命令和输出目录配置

### 3. 运行时错误

**错误信息**: `API request failed`
**解决方案**: 检查 Cloudflare Functions 配置和 API 路由

## 总结

本项目已成功适配 Cloudflare Pages 平台，通过以下优化：

1. **前端构建优化**: 代码分割、资源压缩、缓存策略
2. **后端迁移**: 将 API 逻辑迁移到 Cloudflare Functions
3. **路由配置**: 支持单页应用路由
4. **缓存策略**: 合理的静态资源缓存
5. **安全配置**: 适当的 HTTP 头部设置

通过 Cloudflare Pages 部署，项目获得了以下优势：

- **全球 CDN**: 静态资源全球分发
- **边缘计算**: API 函数就近执行
- **自动 HTTPS**: 内置 SSL 证书
- **无服务器架构**: 无需管理服务器
- **部署简单**: 代码提交自动部署

## 联系信息

如有部署问题或建议，欢迎提交 Issue 或联系项目维护者。

---

**部署成功后，您的 IPTV 管理系统将在 Cloudflare Pages 平台上运行，享受全球 CDN 加速和边缘计算的优势。**
