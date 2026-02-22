// Cloudflare Pages 配置文件

module.exports = {
  // 构建命令
  buildCommand: 'npm run build',
  
  // 构建输出目录
  publishDirectory: 'dist',
  
  // 开发命令
  devCommand: 'npm run dev',
  
  // 环境变量
  env: {
    NODE_ENV: 'production',
    VITE_API_URL: process.env.VITE_API_URL || '/api',
    VITE_APP_NAME: 'IPTV Spider',
    VITE_APP_VERSION: '1.0.0'
  },
  
  // 路由配置
  routes: [
    {
      pattern: '/*',
      destination: '/index.html'
    }
  ],
  
  // 函数配置
  functions: {
    'api/*': {
      runtime: 'nodejs18.x'
    }
  },
  
  // 构建缓存
  buildCache: {
    paths: [
      'node_modules/**/*',
      '.npm/**/*',
      'frontend/node_modules/**/*',
      'frontend/.npm/**/*'
    ]
  },
  
  // 预览配置
  preview: {
    port: 3000,
    open: true
  }
};
