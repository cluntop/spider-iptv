import React from 'react'
import { Navigate } from 'react-router-dom'

const PrivateRoute = ({ children, currentUser }) => {
  // 检查用户是否已登录
  if (!currentUser) {
    // 如果未登录，重定向到登录页面
    return <Navigate to="/login" replace />
  }
  
  // 如果已登录，渲染子组件
  return children
}

export default PrivateRoute
