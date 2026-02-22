// Cloudflare Pages 获取用户信息函数
export async function onRequest(context) {
  const { request, env, params, waitUntil } = context;
  
  if (request.method !== 'GET') {
    return new Response(
      JSON.stringify({ success: false, message: 'Method not allowed' }),
      {
        status: 405,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
  
  try {
    // 模拟获取用户信息逻辑
    // 在实际应用中，这里应该验证 token 并从数据库获取用户信息
    const user = {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
      permissions: ['all'],
      lastLogin: new Date().toISOString(),
      createdAt: '2024-01-01T00:00:00.000Z'
    };
    
    return new Response(
      JSON.stringify({
        success: true,
        user,
        message: 'User information retrieved successfully'
      }),
      {
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Failed to get user information', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}
