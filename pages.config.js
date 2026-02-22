// Cloudflare Pages 配置文件
const { BRANCH = 'main' } = process.env;

// Determine environment based on branch
const isProduction = BRANCH === 'main';
const isStaging = BRANCH === 'staging';

module.exports = {
  // 构建命令
  buildCommand: `cd frontend && npm install && npm run build:${isProduction ? 'production' : isStaging ? 'staging' : 'staging'}`,
  // 构建输出目录
  outputDirectory: 'frontend/dist',
  // 环境变量
  env: {
    NODE_VERSION: '18',
    // 前端 API 配置
    VITE_API_BASE_URL: '/api',
    // 构建优化
    NODE_ENV: isProduction ? 'production' : 'staging',
    // 禁用不必要的构建步骤
    SKIP_PREFLIGHT_CHECK: 'true',
    // Environment-specific variables
    VITE_APP_ENV: isProduction ? 'production' : 'staging',
    VITE_APP_DEBUG: isProduction ? 'false' : 'true',
    VITE_APP_TITLE: isProduction ? 'IPTV 管理系统' : 'IPTV 管理系统 (Staging)',
    VITE_APP_DOMAIN: isProduction 
      ? 'https://spider-iptv.pages.dev' 
      : 'https://spider-iptv-staging.pages.dev'
  },
  // 构建配置
  build: {
    // 启用并行构建
    parallel: true,
    // 构建超时设置
    timeout: 300,
    // 依赖缓存
    cache: true
  },
  // 路由规则
  routes: [
    {
      pattern: '/api/*',
      function: 'api'
    },
    {
      pattern: '/*',
      destination: '/index.html'
    }
  ]
};
