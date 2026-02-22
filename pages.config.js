// Cloudflare Pages 配置文件
module.exports = {
  // 构建命令
  buildCommand: 'cd frontend && npm install && npm run build',
  // 构建输出目录
  outputDirectory: 'dist',
  // 环境变量
  env: {
    NODE_VERSION: '18',
    // 前端 API 配置
    VITE_API_BASE_URL: '/api',
    // 构建优化
    NODE_ENV: 'production',
    // 禁用不必要的构建步骤
    SKIP_PREFLIGHT_CHECK: 'true'
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
