// Cloudflare Pages 频道管理 API 函数
import { log, handleApiError, createSuccessResponse } from '../utils/logger.js';
import { withCors } from '../utils/cors.js';

async function handler(context) {
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

// Export wrapped handler with CORS support
export const onRequest = withCors(handler);

// 获取频道列表
async function handleGetChannels(context) {
  try {
    log('info', 'Get channels requested');
    
    // 从环境变量获取 Python 后端 API URL
    const pythonBackendUrl = env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    
    // 转发请求到 Python 后端
    const response = await fetch(`${pythonBackendUrl}/api/channels`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Python backend returned ${response.status}`);
    }
    
    const data = await response.json();
    return createSuccessResponse(data);
  } catch (error) {
    log('error', 'Failed to get channels', {}, error);
    // 降级到模拟数据
    return getMockChannels();
  }
}

// 创建频道
async function handleCreateChannel(context) {
  try {
    const { request, env } = context;
    const body = await request.json();
    
    log('info', 'Create channel requested', { channelName: body.name });
    
    // 从环境变量获取 Python 后端 API URL
    const pythonBackendUrl = env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    
    // 转发请求到 Python 后端
    const response = await fetch(`${pythonBackendUrl}/api/channels`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      throw new Error(`Python backend returned ${response.status}`);
    }
    
    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      {
        status: 201,
        headers: {
          'content-type': 'application/json'
        }
      }
    );
  } catch (error) {
    log('error', 'Failed to create channel', {}, error);
    // 降级到模拟创建
    return mockCreateChannel(body);
  }
}

// 更新频道
async function handleUpdateChannel(context) {
  try {
    const { request, env, params } = context;
    const body = await request.json();
    const channelId = params.id || body.id;
    
    log('info', 'Update channel requested', { channelId });
    
    // 从环境变量获取 Python 后端 API URL
    const pythonBackendUrl = env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    
    // 转发请求到 Python 后端
    const response = await fetch(`${pythonBackendUrl}/api/channels/${channelId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      throw new Error(`Python backend returned ${response.status}`);
    }
    
    const data = await response.json();
    return createSuccessResponse(data);
  } catch (error) {
    log('error', 'Failed to update channel', {}, error);
    // 降级到模拟更新
    return mockUpdateChannel(channelId, body);
  }
}

// 删除频道
async function handleDeleteChannel(context) {
  try {
    const { env, params } = context;
    const channelId = params.id;
    
    log('info', 'Delete channel requested', { channelId });
    
    // 从环境变量获取 Python 后端 API URL
    const pythonBackendUrl = env.PYTHON_BACKEND_URL || 'http://localhost:8000';
    
    // 转发请求到 Python 后端
    const response = await fetch(`${pythonBackendUrl}/api/channels/${channelId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Python backend returned ${response.status}`);
    }
    
    const data = await response.json();
    return createSuccessResponse(data);
  } catch (error) {
    log('error', 'Failed to delete channel', {}, error);
    // 降级到模拟删除
    return mockDeleteChannel(channelId);
  }
}

// 模拟数据 - 降级方案
function getMockChannels() {
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
  
  return createSuccessResponse({
    channels,
    total: channels.length,
    message: 'Channels retrieved from mock data'
  });
}

// 模拟创建频道
function mockCreateChannel(body) {
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
      message: 'Channel created (mock data)'
    }),
    {
      status: 201,
      headers: {
        'content-type': 'application/json'
      }
    }
  );
}

// 模拟更新频道
function mockUpdateChannel(channelId, body) {
  const updatedChannel = {
    id: channelId,
    ...body,
    lastChecked: new Date().toISOString()
  };
  
  return createSuccessResponse({
    channel: updatedChannel,
    message: 'Channel updated (mock data)'
  });
}

// 模拟删除频道
function mockDeleteChannel(channelId) {
  return createSuccessResponse({
    channelId,
    message: 'Channel deleted (mock data)'
  });
}
