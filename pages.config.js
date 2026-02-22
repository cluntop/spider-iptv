// Cloudflare Pages 配置文件
module.exports = {
  // 构建命令
  buildCommand: 'npm run build',
  // 构建输出目录
  outputDirectory: 'dist',
  // 环境变量
  env: {
    NODE_VERSION: '16',
    PYTHON_VERSION: '3.9',
    // 构建时的临时目录
    BUILD_TEMP_DIR: './temp',
    // 禁用 lxml 从源码构建
    LXML_BUILD_NO_EXTENSIONS: '1'
  },
  // 构建过程中的目录规则
  rules: [
    {
      type: 'Header',
      pattern: '/*',
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    }
  ]
};
