# Cloudflare Pages 部署文档

## 项目概述

IPTV 爬虫管理系统是一个基于 React + Cloudflare Pages 的前端应用，用于管理 IPTV 频道、监控系统状态和配置系统参数。本文档详细说明了如何将项目部署到 Cloudflare Pages 平台，并提供了完整的生产环境配置指南。

## 技术栈

- **前端**: React + Vite + Ant Design
- **后端**: Cloudflare Pages Functions (JavaScript)
- **构建工具**: Vite
- **部署平台**: Cloudflare Pages
- **CI/CD**: GitHub Actions
- **监控**: Google Analytics + 自定义性能监控

## 项目结构

```
├── _pages/             # Cloudflare Pages 配置和函数
│   ├── functions/      # Cloudflare Functions
│   │   ├── api/        # API 处理函数
│   │   └── utils/      # 工具函数
│   │       ├── logger.js     # 日志工具
│   │       ├── cors.js       # CORS 中间件
│   ├── _headers        # HTTP 头部配置
│   └── _redirects      # 路由重定向规则
├── dist/               # 构建输出目录
├── frontend/           # 前端源代码
│   ├── src/            # 前端源码
│   │   ├── utils/      # 前端工具
│   │   │   ├── performance.js # 性能监控
│   │   │   └── analytics.js   # 分析工具
│   ├── package.json    # 前端依赖
│   ├── vite.config.js  # Vite 配置
│   └── jest.config.js  # Jest 测试配置
├── .github/workflows/  # GitHub Actions 工作流
│   ├── ci-cd.yml       # CI/CD 流水线
│   └── rollback.yml    # 回滚流程
├── pages.config.js     # Cloudflare Pages 配置
└── README_CLOUDFLARE.md # 本部署文档
```

## Cloudflare Pages 配置

### 1. 基本配置

- **构建命令**: 根据分支自动选择构建命令
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
| `VITE_GA_TRACKING_ID` | 环境 | `` | Google Analytics 跟踪 ID |

### 3. 分支策略

| 分支 | 环境 | 部署 URL |
|------|------|----------|
| `main` | 生产 | `https://iptv-spider.pages.dev` |
| `staging` | 预发 | `https://iptv-spider-staging.pages.dev` |
| `develop` | 开发 | 仅构建，不部署 |

## 部署流程

### 1. 准备工作

1. **创建 Cloudflare 账户**
   - 访问 [Cloudflare 控制台](https://dash.cloudflare.com/)
   - 注册或登录现有账户

2. **连接 GitHub 仓库**
   - 在 Cloudflare Pages 控制台中，点击 "Create a project"
   - 选择 "Connect to Git"
   - 选择您的 GitHub 仓库

3. **配置 API 令牌**
   - 在 GitHub 仓库设置中，添加以下 secrets：
     - `CLOUDFLARE_API_TOKEN`: Cloudflare API 令牌
     - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare 账户 ID

### 2. 配置构建设置

1. **生产环境**
   - **项目名称**: `iptv-spider`
   - **生产分支**: `main`
   - **构建命令**: `cd frontend && npm install && npm run build:production`
   - **构建输出目录**: `dist`

2. **预发环境**
   - **项目名称**: `iptv-spider-staging`
   - **生产分支**: `staging`
   - **构建命令**: `cd frontend && npm install && npm run build:staging`
   - **构建输出目录**: `dist`

3. **高级设置**
   - **Node 版本**: 选择 `18`
   - **Build system version**: 选择最新版本

### 3. 部署项目

1. **自动部署**
   - 推送代码到 `main` 或 `staging` 分支
   - GitHub Actions 会自动触发构建和部署流程

2. **手动部署**
   - 在 GitHub Actions 中运行 `CI/CD Pipeline` 工作流
   - 选择目标分支进行部署

3. **回滚部署**
   - 在 GitHub Actions 中运行 `Rollback Deployment` 工作流
   - 选择目标环境和部署 ID

## 环境配置

### 1. 前端环境配置

项目支持多环境配置：

- **生产环境**: `frontend/.env.production`
- **预发环境**: `frontend/.env.staging`

### 2. 构建命令

| 环境 | 命令 |
|------|------|
| 开发 | `npm run dev` |
| 生产构建 | `npm run build:production` |
| 预发构建 | `npm run build:staging` |

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
  - 生产环境移除 console 和 debugger
  - 启用 tree shaking 移除未使用代码

### 2. 性能优化

- **懒加载**: 大型组件使用动态导入
- **缓存策略**: 合理设置静态资源缓存
- **网络优化**: 最小化 HTTP 请求，合并资源
- **性能监控**: 内置性能指标跟踪

## 安全配置

### 1. HTTP 头部设置

项目配置了以下安全头部：

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), autoplay=(), payment=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://*.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.cloudflare.com`
- `X-XSS-Protection: 1; mode=block`

### 2. CORS 配置

项目实现了完整的 CORS 支持：

- 支持所有 HTTP 方法
- 支持自定义头部
- 支持凭证传递
- 实现了预检请求处理

## 监控和分析

### 1. 性能监控

项目内置了性能监控功能：

- 页面加载时间跟踪
- API 请求性能监控
- 组件渲染时间监控
- 首屏绘制时间跟踪

### 2. 分析集成

项目支持 Google Analytics 集成：

- 页面浏览量跟踪
- 事件跟踪
- 性能指标跟踪

## 测试配置

### 1. 测试环境

项目配置了完整的测试环境：

- **测试框架**: Jest
- **测试库**: React Testing Library
- **测试命令**:
  - 运行测试: `npm test`
  - 监视模式: `npm run test:watch`
  - 覆盖率报告: `npm run test:coverage`

### 2. 代码质量

- **代码检查**: ESLint
- **代码格式**: 遵循 Airbnb 风格指南

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
- **回滚**: 建立完善的回滚机制

## 部署验证

部署完成后，验证以下功能：

1. **前端访问**: 打开部署 URL，确认页面正常加载
2. **API 连接**: 测试登录和数据获取功能
3. **路由导航**: 测试页面导航和刷新功能
4. **响应速度**: 检查页面加载速度和 API 响应时间
5. **跨浏览器兼容性**: 在不同浏览器中测试
6. **安全配置**: 检查安全头部和 CORS 设置
7. **监控集成**: 验证性能监控和分析功能

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

### 4. 性能问题

**症状**: 页面加载缓慢或 API 响应延迟

**解决方案**:
- 检查网络连接
- 验证 Cloudflare CDN 配置
- 优化前端代码，减少不必要的渲染
- 检查后端函数执行时间

## 总结

本项目已成功适配 Cloudflare Pages 平台，通过以下优化：

1. **前端构建优化**: 代码分割、资源压缩、缓存策略
2. **后端迁移**: 将 API 逻辑迁移到 Cloudflare Functions
3. **路由配置**: 支持单页应用路由
4. **缓存策略**: 合理的静态资源缓存
5. **安全配置**: 完整的安全头部和 CORS 设置
6. **CI/CD 集成**: 自动化测试和部署流程
7. **监控和分析**: 性能监控和用户行为分析
8. **多环境支持**: 生产、预发和开发环境配置

通过 Cloudflare Pages 部署，项目获得了以下优势：

- **全球 CDN**: 静态资源全球分发
- **边缘计算**: API 函数就近执行
- **自动 HTTPS**: 内置 SSL 证书
- **无服务器架构**: 无需管理服务器
- **部署简单**: 代码提交自动部署
- **高可用性**: Cloudflare 全球网络保障

## 联系信息

如有部署问题或建议，欢迎提交 Issue 或联系项目维护者。

---

**部署成功后，您的 IPTV 管理系统将在 Cloudflare Pages 平台上运行，享受全球 CDN 加速和边缘计算的优势。**
