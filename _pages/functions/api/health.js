// Cloudflare Pages 健康检查函数
export async function onRequest(context) {
  const { request, env, params, waitUntil } = context;
  
  return new Response(
    JSON.stringify({
      status: "ok",
      message: "IPTV Spider API is running",
      timestamp: new Date().toISOString()
    }),
    {
      headers: {
        "content-type": "application/json"
      }
    }
  );
}
