// Cloudflare Pages 健康检查函数
export async function onRequest(context) {
  const { request, env, params, waitUntil } = context;
  
  try {
    // 模拟数据库连接检查
    const dbStatus = await checkDatabaseStatus();
    
    return new Response(
      JSON.stringify({
        status: "ok",
        message: "IPTV Spider API is running",
        timestamp: new Date().toISOString(),
        database: dbStatus,
        version: "1.0.0",
        environment: env.CF_PAGES ? "production" : "development"
      }),
      {
        headers: {
          "content-type": "application/json"
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        status: "error",
        message: "Health check failed",
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      {
        status: 500,
        headers: {
          "content-type": "application/json"
        }
      }
    );
  }
}

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
    return {
      status: "disconnected",
      error: error.message,
      last_check: new Date().toISOString()
    };
  }
}
