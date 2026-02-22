// Cloudflare Pages 频道管理 API 函数
export async function onRequest(context) {
  const { request, env, params, waitUntil } = context;
  
  // 处理不同的 HTTP 方法
  switch (request.method) {
    case 'GET':
      return handleGetChannels(context);
    case 'POST':
      return handleCreateChannel(context);
    case 'PUT':
      return handleUpdateChannel(context);
    case 'DELETE':
      return handleDeleteChannel(context);
    default:
      return new Response(
        JSON.stringify({ success: false, message: 'Method not allowed' }),
        {
          status: 405,
          headers: { 'content-type': 'application/json' }
        }
      );
  }
}

// 获取频道列表
async function handleGetChannels(context) {
  try {
    // 模拟频道数据
    const channels = [
      {
        id: 1,
        name: 'CCTV-1',
        url: 'http://example.com/cctv1',
        category: '央视',
        status: 'online',
        quality: 'HD',
        speed: 1.2,
        lastChecked: new Date().toISOString()
      },
      {
        id: 2,
        name: 'CCTV-2',
        url: 'http://example.com/cctv2',
        category: '央视',
        status: 'online',
        quality: 'HD',
        speed: 1.5,
        lastChecked: new Date().toISOString()
      },
      {
        id: 3,
        name: '东方卫视',
        url: 'http://example.com/dragon',
        category: '卫视',
        status: 'online',
        quality: 'HD',
        speed: 1.8,
        lastChecked: new Date().toISOString()
      }
    ];
    
    return new Response(
      JSON.stringify({
        success: true,
        channels,
        total: channels.length,
        message: 'Channels retrieved successfully'
      }),
      {
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Failed to get channels', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}

// 创建频道
async function handleCreateChannel(context) {
  try {
    const { request } = context;
    const body = await request.json();
    
    // 模拟创建频道
    const newChannel = {
      id: Date.now(),
      ...body,
      status: 'online',
      speed: 1.0,
      lastChecked: new Date().toISOString()
    };
    
    return new Response(
      JSON.stringify({
        success: true,
        channel: newChannel,
        message: 'Channel created successfully'
      }),
      {
        status: 201,
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Failed to create channel', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}

// 更新频道
async function handleUpdateChannel(context) {
  try {
    const { request, params } = context;
    const body = await request.json();
    const channelId = params.id || body.id;
    
    // 模拟更新频道
    const updatedChannel = {
      id: channelId,
      ...body,
      lastChecked: new Date().toISOString()
    };
    
    return new Response(
      JSON.stringify({
        success: true,
        channel: updatedChannel,
        message: 'Channel updated successfully'
      }),
      {
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Failed to update channel', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}

// 删除频道
async function handleDeleteChannel(context) {
  try {
    const { params } = context;
    const channelId = params.id;
    
    // 模拟删除频道
    return new Response(
      JSON.stringify({
        success: true,
        channelId,
        message: 'Channel deleted successfully'
      }),
      {
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, message: 'Failed to delete channel', error: error.message }),
      {
        status: 500,
        headers: { 'content-type': 'application/json' }
      }
    );
  }
}
