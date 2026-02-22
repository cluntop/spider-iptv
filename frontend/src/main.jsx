import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Provider } from 'react-redux'
import store from './store'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { initPerformanceMonitoring } from './utils/performance'
import { initGoogleAnalytics } from './utils/analytics'

// Initialize performance monitoring
initPerformanceMonitoring()

// Initialize Google Analytics (only in production)
if (import.meta.env.PROD) {
  const trackingId = import.meta.env.VITE_GA_TRACKING_ID || ''
  if (trackingId) {
    initGoogleAnalytics(trackingId)
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ConfigProvider locale={zhCN}>
        <App />
      </ConfigProvider>
    </Provider>
  </React.StrictMode>,
)
