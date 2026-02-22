// Google Analytics integration

/**
 * Initialize Google Analytics
 * @param {string} trackingId - Google Analytics tracking ID
 */
export function initGoogleAnalytics(trackingId) {
  if (!trackingId) return;
  
  // Load Google Analytics script
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
  
  window.ga('create', trackingId, 'auto');
  window.ga('send', 'pageview');
  
  console.log('Google Analytics initialized');
}

/**
 * Track page view
 * @param {string} path - Page path
 * @param {string} title - Page title
 */
export function trackPageView(path, title) {
  if (window.ga) {
    window.ga('send', 'pageview', {
      page: path,
      title: title
    });
  }
}

/**
 * Track event
 * @param {string} category - Event category
 * @param {string} action - Event action
 * @param {string} label - Event label
 * @param {number} value - Event value
 */
export function trackEvent(category, action, label, value) {
  if (window.ga) {
    window.ga('send', 'event', {
      eventCategory: category,
      eventAction: action,
      eventLabel: label,
      eventValue: value
    });
  }
}
