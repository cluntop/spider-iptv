// Cloudflare Pages 健康检查函数
import { log, handleApiError, createSuccessResponse } from '../utils/logger.js';
import { withCors } from '../utils/cors.js';

async function handler(context) {
  const { request, env, params, waitUntil } = context;
  
  try {
    log('info', 'Health check requested', {
      environment: env.CF_PAGES ? 'production' : 'development'
    });
    
    // 模拟数据库连接检查
    const dbStatus = await checkDatabaseStatus();
    
    const responseData = {
      status: "ok",
      message: "IPTV Spider API is running",
      database: dbStatus,
      version: "1.0.0",
      environment: env.CF_PAGES ? "production" : "development"
    };
    
    log('info', 'Health check completed successfully', {
      databaseStatus: dbStatus.status
    });
    
    return createSuccessResponse(responseData);
  } catch (error) {
    return handleApiError(error, context, 'Health check failed');
  }
}

// Export wrapped handler with CORS support
export const onRequest = withCors(handler);

// 检查数据库状态
async function checkDatabaseStatus() {
  try {
    // 在实际环境中，这里应该检查真实的数据库连接
    // 由于是模拟环境，返回正常状态
    return {
      status: "connected",
      latency: Math.floor(Math.random() * 100) + 1,
      last_check: new Date().toISOString()
    };
  } catch (error) {
    log('warn', 'Database connection check failed', {}, error);
    return {
      status: "disconnected",
      error: error.message,
      last_check: new Date().toISOString()
    };
  }
}
