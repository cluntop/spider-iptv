// Cloudflare Pages 登出函数
import { withCors } from '../../utils/cors.js';

async function handler(context) {
  const { request, env, params, waitUntil } = context;
  
  if (request.method !== 'POST') {
    return new Response(
      JSON.stringify({ success: false, message: 'Method not allowed' }),
      {
        status: 405,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
  
  try {
    // 模拟登出逻辑
    // 在实际应用中，这里应该处理 token 失效等操作
    
    return new Response(
      JSON.stringify({
        success: true,
        message: 'Logout successful'
      }),
      {
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Logout failed', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}

// Export wrapped handler with CORS support
export const onRequest = withCors(handler);
