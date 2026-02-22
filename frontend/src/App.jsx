import React, { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Menu, Button, Avatar, Badge, message } from 'antd'
import { 
  DashboardOutlined, 
  SettingOutlined, 
  UserOutlined, 
  UserAddOutlined, 
  VideoCameraOutlined, 
  DatabaseOutlined, 
  ScheduleOutlined, 
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import UserManagement from './pages/UserManagement'
import ChannelManagement from './pages/ChannelManagement'
import DatabaseManagement from './pages/DatabaseManagement'
import SchedulerManagement from './pages/SchedulerManagement'
import SystemSettings from './pages/SystemSettings'
import Login from './pages/Login'
import PrivateRoute from './components/PrivateRoute'
import { getCurrentUser, logout } from './services/authService'
import { canAccessPage } from './utils/permission'

const { Header, Sider, Content } = Layout
const { SubMenu } = Menu

function App() {
  const [collapsed, setCollapsed] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const { notificationCount } = useSelector(state => state.notification)

  useEffect(() => {
    // 初始化时获取当前用户信息
    const initUser = async () => {
      try {
        const user = await getCurrentUser()
        setCurrentUser(user)
      } catch (error) {
        // 用户未登录，保持currentUser为null
        message.info('请先登录')
      } finally {
        setLoading(false)
      }
    }
    initUser()
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
      setCurrentUser(null)
      message.success('退出登录成功')
    } catch (error) {
      message.error('退出登录失败')
    }
  }

  if (loading) {
    return <div className="loading-container">加载中...</div>
  }

  return (
    <Router>
      <Layout className="app-container">
        <Routes>
          {/* 登录页面 */}
          <Route path="/login" element={<Login setCurrentUser={setCurrentUser} />} />
          
          {/* 私有路由 - 需要登录才能访问 */}
          <Route path="/" element={
            <PrivateRoute currentUser={currentUser}>
              <Layout style={{ minHeight: '100vh' }}>
                <Sider trigger={null} collapsible collapsed={collapsed}>
                  <div className="logo" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6 }} />
                  <Menu
                    theme="dark"
                    mode="inline"
                    defaultSelectedKeys={['1']}
                    items={[
                      // 仪表盘 - 所有角色都可以访问
                      ...(canAccessPage(currentUser, 'dashboard') ? [{
                        key: '1',
                        icon: <DashboardOutlined />,
                        label: '仪表盘',
                        path: '/dashboard'
                      }] : []),
                      
                      // 用户管理 - 只有管理员和经理可以访问
                      ...(canAccessPage(currentUser, 'users') ? [{
                        key: '2',
                        icon: <UserOutlined />,
                        label: '用户管理',
                        children: [
                          {
                            key: '2-1',
                            icon: <UserOutlined />,
                            label: '用户列表',
                            path: '/users'
                          }
                        ]
                      }] : []),
                      
                      // 频道管理 - 所有角色都可以访问（查看权限）
                      ...(canAccessPage(currentUser, 'channels') ? [{
                        key: '3',
                        icon: <VideoCameraOutlined />,
                        label: '频道管理',
                        path: '/channels'
                      }] : []),
                      
                      // 数据库管理 - 只有管理员和经理可以访问
                      ...(canAccessPage(currentUser, 'database') ? [{
                        key: '4',
                        icon: <DatabaseOutlined />,
                        label: '数据库管理',
                        path: '/database'
                      }] : []),
                      
                      // 调度管理 - 只有管理员和经理可以访问
                      ...(canAccessPage(currentUser, 'scheduler') ? [{
                        key: '5',
                        icon: <ScheduleOutlined />,
                        label: '调度管理',
                        path: '/scheduler'
                      }] : []),
                      
                      // 系统设置 - 只有管理员可以访问
                      ...(canAccessPage(currentUser, 'settings') ? [{
                        key: '6',
                        icon: <SettingOutlined />,
                        label: '系统设置',
                        path: '/settings'
                      }] : [])
                    ].map(item => ({
                      ...item,
                      onClick: () => {
                        if (item.path) {
                          window.location.href = `#${item.path}`
                        }
                      }
                    }))}
                  />
                </Sider>
                <Layout>
                  <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
                    <Button
                      type="text"
                      icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                      onClick={() => setCollapsed(!collapsed)}
                      style={{ fontSize: '16px', width: 64, height: 64 }}
                    />
                    <div style={{ flex: 1 }} />
                    <Badge count={notificationCount} style={{ marginRight: 24 }}>
                      <Button type="text" icon={<BellOutlined />} style={{ fontSize: '16px' }} />
                    </Badge>
                    <Menu mode="horizontal" selectable={false} style={{ border: 'none' }}>
                      <SubMenu
                        title={
                          <span style={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar style={{ marginRight: 8 }}>
                              {currentUser?.username?.[0] || 'A'}
                            </Avatar>
                            <span>{currentUser?.username || '管理员'}</span>
                          </span>
                        }
                      >
                        <Menu.Item key="profile">个人资料</Menu.Item>
                        <Menu.Item key="settings">账户设置</Menu.Item>
                        <Menu.Item 
                          key="logout" 
                          icon={<LogoutOutlined />}
                          onClick={handleLogout}
                        >
                          退出登录
                        </Menu.Item>
                      </SubMenu>
                    </Menu>
                  </Header>
                  <Content style={{ margin: '24px', overflow: 'auto' }}>
                    <Routes>
                      {/* 仪表盘 - 所有角色都可以访问 */}
                      {canAccessPage(currentUser, 'dashboard') && (
                        <Route path="/dashboard" element={<Dashboard />} />
                      )}
                      
                      {/* 用户管理 - 只有管理员和经理可以访问 */}
                      {canAccessPage(currentUser, 'users') && (
                        <Route path="/users" element={<UserManagement />} />
                      )}
                      
                      {/* 频道管理 - 所有角色都可以访问（查看权限） */}
                      {canAccessPage(currentUser, 'channels') && (
                        <Route path="/channels" element={<ChannelManagement />} />
                      )}
                      
                      {/* 数据库管理 - 只有管理员和经理可以访问 */}
                      {canAccessPage(currentUser, 'database') && (
                        <Route path="/database" element={<DatabaseManagement />} />
                      )}
                      
                      {/* 调度管理 - 只有管理员和经理可以访问 */}
                      {canAccessPage(currentUser, 'scheduler') && (
                        <Route path="/scheduler" element={<SchedulerManagement />} />
                      )}
                      
                      {/* 系统设置 - 只有管理员可以访问 */}
                      {canAccessPage(currentUser, 'settings') && (
                        <Route path="/settings" element={<SystemSettings />} />
                      )}
                      
                      {/* 默认路由 */}
                      <Route path="/" element={
                        canAccessPage(currentUser, 'dashboard') ? (
                          <Navigate to="/dashboard" replace />
                        ) : canAccessPage(currentUser, 'channels') ? (
                          <Navigate to="/channels" replace />
                        ) : (
                          <div>无权限访问任何页面</div>
                        )
                      } />
                    </Routes>
                  </Content>
                </Layout>
              </Layout>
            </PrivateRoute>
          } />
          
          {/* 404页面 */}
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
