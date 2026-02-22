// CORS middleware for Cloudflare Functions

/**
 * Handle CORS preflight requests
 * @param {Request} request - Request object
 * @returns {Response} CORS response
 */
export function handleCorsPreflight(request) {
  const origin = request.headers.get('Origin') || '*';
  
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': origin,
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
      'Access-Control-Max-Age': '86400',
      'Access-Control-Allow-Credentials': 'true'
    }
  });
}

/**
 * Add CORS headers to response
 * @param {Response} response - Original response
 * @param {Request} request - Request object
 * @returns {Response} Response with CORS headers
 */
export function addCorsHeaders(response, request) {
  const origin = request.headers.get('Origin') || '*';
  const newHeaders = new Headers(response.headers);
  
  // Add CORS headers
  newHeaders.set('Access-Control-Allow-Origin', origin);
  newHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  newHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  newHeaders.set('Access-Control-Max-Age', '86400');
  newHeaders.set('Access-Control-Allow-Credentials', 'true');
  
  // Create new response with updated headers
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  });
}

/**
 * CORS middleware for Cloudflare Functions
 * @param {Function} handler - Original request handler
 * @returns {Function} Wrapped handler with CORS support
 */
export function withCors(handler) {
  return async function (context) {
    const { request } = context;
    
    // Handle OPTIONS requests
    if (request.method === 'OPTIONS') {
      return handleCorsPreflight(request);
    }
    
    // Process the request
    const response = await handler(context);
    
    // Add CORS headers to the response
    return addCorsHeaders(response, request);
  };
}
