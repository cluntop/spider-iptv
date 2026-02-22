// Cloudflare Pages 登录认证函数
export async function onRequest(context) {
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
    const body = await request.json();
    const { username, password } = body;
    
    // 模拟认证逻辑
    if (username === 'admin' && password === 'admin123') {
      const token = 'mock-token-' + Date.now();
      const user = {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
        permissions: ['all']
      };
      
      return new Response(
        JSON.stringify({
          success: true,
          token,
          user,
          message: 'Login successful'
        }),
        {
          headers: {
            'content-type': 'application/json'
          }
        }
      );
    } else {
      return new Response(
        JSON.stringify({ success: false, message: 'Invalid username or password' }),
        {
          status: 401,
          headers: { 'content-type': 'application/json' }
        }
      );
    }
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Login failed', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}
