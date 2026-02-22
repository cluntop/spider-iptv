import React, { useState } from 'react'
import { Card, Form, Input, Button, Checkbox, Alert, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { login } from '../services/authService'

const Login = ({ setCurrentUser }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const onFinish = async (values) => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await login(values.username, values.password)
      
      if (result.success) {
        // 设置当前用户
        setCurrentUser(result.user)
        message.success('登录成功')
      } else {
        throw new Error('登录失败')
      }
    } catch (err) {
      setError(err.message)
      message.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <Card title="管理员登录" className="login-card">
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}
        
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          
          <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            <a href="#" style={{ float: 'right' }}>忘记密码?</a>
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" className="login-button" loading={loading}>
              登录
            </Button>
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <p>默认账号: admin</p>
              <p>默认密码: admin123</p>
            </div>
          </Form.Item>
        </Form>
      </Card>
      
      <style jsx>{`
        .login-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .login-card {
          width: 400px;
          padding: 24px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .login-button {
          width: 100%;
        }
      `}</style>
    </div>
  )
}

export default Login
