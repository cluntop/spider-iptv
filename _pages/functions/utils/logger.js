// Logger utility for Cloudflare Functions

/**
 * Log a message with context information
 * @param {string} level - Log level: info, warn, error
 * @param {string} message - Log message
 * @param {Object} context - Additional context
 * @param {Error} error - Optional error object
 */
export function log(level, message, context = {}, error = null) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    level,
    message,
    context,
    error: error ? {
      message: error.message,
      stack: error.stack,
      name: error.name
    } : null
  };
  
  // Log to Cloudflare console
  console[level](JSON.stringify(logEntry));
  
  return logEntry;
}

/**
 * Handle API errors consistently
 * @param {Error} error - Error object
 * @param {Object} context - Cloudflare context
 * @param {string} defaultMessage - Default error message
 * @returns {Response} Error response
 */
export function handleApiError(error, context, defaultMessage = 'Internal Server Error') {
  // Log the error
  log('error', defaultMessage, {
    request: {
      url: context.request.url,
      method: context.request.method
    }
  }, error);
  
  // Determine error status code
  let status = 500;
  if (error.status) {
    status = error.status;
  } else if (error.name === 'ValidationError') {
    status = 400;
  } else if (error.name === 'UnauthorizedError') {
    status = 401;
  } else if (error.name === 'ForbiddenError') {
    status = 403;
  } else if (error.name === 'NotFoundError') {
    status = 404;
  }
  
  // Create error response
  return new Response(
    JSON.stringify({
      error: {
        message: error.message || defaultMessage,
        code: error.code || 'INTERNAL_ERROR',
        status
      },
      timestamp: new Date().toISOString()
    }),
    {
      status,
      headers: {
        'content-type': 'application/json',
        'x-error-code': error.code || 'INTERNAL_ERROR'
      }
    }
  );
}

/**
 * Create a success response
 * @param {Object} data - Response data
 * @param {number} status - HTTP status code
 * @returns {Response} Success response
 */
export function createSuccessResponse(data, status = 200) {
  return new Response(
    JSON.stringify({
      success: true,
      data,
      timestamp: new Date().toISOString()
    }),
    {
      status,
      headers: {
        'content-type': 'application/json'
      }
    }
  );
}

/**
 * Validate request body
 * @param {Request} request - Request object
 * @param {Array} requiredFields - Required fields
 * @returns {Promise<Object>} Parsed body
 * @throws {Error} Validation error
 */
export async function validateRequestBody(request, requiredFields = []) {
  try {
    const body = await request.json();
    
    // Check for required fields
    const missingFields = requiredFields.filter(field => !body.hasOwnProperty(field));
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }
    
    return body;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error('Invalid JSON format');
    }
    throw error;
  }
}
