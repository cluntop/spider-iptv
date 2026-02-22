// Performance monitoring utility

/**
 * Track page load performance
 */
export function trackPageLoad() {
  if ('performance' in window && 'timing' in window.performance) {
    const timing = window.performance.timing;
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    
    console.log(`Page load time: ${loadTime}ms`);
    
    // Send to analytics service if available
    if (window.gtag) {
      window.gtag('event', 'page_load', {
        event_category: 'performance',
        event_label: window.location.pathname,
        value: loadTime
      });
    }
    
    return loadTime;
  }
  return 0;
}

/**
 * Track API request performance
 * @param {string} endpoint - API endpoint
 * @param {number} duration - Request duration in milliseconds
 * @param {number} status - HTTP status code
 */
export function trackApiRequest(endpoint, duration, status) {
  console.log(`API request to ${endpoint}: ${duration}ms (status: ${status})`);
  
  // Send to analytics service if available
  if (window.gtag) {
    window.gtag('event', 'api_request', {
      event_category: 'performance',
      event_label: endpoint,
      value: duration,
      status: status
    });
  }
}

/**
 * Track component render time
 * @param {string} componentName - Component name
 * @param {number} duration - Render duration in milliseconds
 */
export function trackComponentRender(componentName, duration) {
  console.log(`Component ${componentName} render time: ${duration}ms`);
  
  // Send to analytics service if available
  if (window.gtag) {
    window.gtag('event', 'component_render', {
      event_category: 'performance',
      event_label: componentName,
      value: duration
    });
  }
}

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring() {
  // Track page load
  window.addEventListener('load', trackPageLoad);
  
  // Track first paint and first contentful paint
  if ('performance' in window && 'getEntriesByType' in window.performance) {
    new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.name === 'first-paint') {
          console.log(`First paint: ${entry.startTime}ms`);
        } else if (entry.name === 'first-contentful-paint') {
          console.log(`First contentful paint: ${entry.startTime}ms`);
        }
      });
    }).observe({ entryTypes: ['paint'] });
  }
}
